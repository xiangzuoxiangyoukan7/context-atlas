"""验证增强摄取的批次、网页和非正式历史边界。"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from email.message import Message
import json
from pathlib import Path
import tempfile
import unittest

from scripts.project_kb.ingest_enhancements import (
    aggregate_batch_reports,
    fetch_web_snapshot,
    save_ingest_history,
    validate_batch_sources,
)


class _FakeResponse:
    """提供网页快照测试所需的最小响应接口。"""

    def __init__(self, body: bytes, final_url: str = "https://8.8.8.8/final") -> None:
        """保存虚构正文、最终 URL 和纯文本响应头。"""

        self.body = body
        self.final_url = final_url
        self.headers = Message()
        self.headers["Content-Type"] = "text/plain; charset=utf-8"

    def __enter__(self) -> _FakeResponse:
        """进入虚构响应上下文并返回自身。"""

        return self

    def __exit__(self, *args: object) -> None:
        """退出虚构响应上下文，不抑制异常。"""

        return None

    def geturl(self) -> str:
        """返回测试规定的最终重定向 URL。"""

        return self.final_url

    def read(self, size: int) -> bytes:
        """按调用方上限返回虚构响应字节。"""

        return self.body[:size]


class IngestEnhancementTests(unittest.TestCase):
    """确保增强能力有界、可追溯且不写正式知识。"""

    def test_batch_rejects_empty_over_limit_and_duplicate_sources(self) -> None:
        """批次必须为 1～20 个不同的稳定来源身份。"""

        with self.assertRaises(ValueError):
            validate_batch_sources([])
        with self.assertRaises(ValueError):
            validate_batch_sources(
                [{"type": "repository_file", "reference": str(index)} for index in range(21)]
            )
        with self.assertRaises(ValueError):
            validate_batch_sources(
                [
                    {"type": "repository_file", "reference": "a.md"},
                    {"type": "repository_file", "reference": "a.md"},
                ]
            )

    def test_batch_aggregate_preserves_per_source_results_and_routes(self) -> None:
        """单项阻塞不能抹掉成功项，汇总路由需要稳定去重。"""

        report = aggregate_batch_reports(
            [
                {"status": "analyzed", "route_plan": ["context-atlas-add"]},
                {"status": "blocked", "route_plan": []},
                {"status": "analyzed", "route_plan": ["context-atlas-add", "context-atlas-revise"]},
            ]
        )

        self.assertEqual("analyzed", report["status"])
        self.assertEqual(3, report["source_count"])
        self.assertEqual(["context-atlas-add", "context-atlas-revise"], report["route_plan"])
        self.assertFalse(report["writes_performed"])

    def test_web_snapshot_records_final_url_and_digest_without_crawling(self) -> None:
        """网页读取只消费一个响应并记录最终定位与内容摘要。"""

        calls: list[str] = []

        def opener(request: object, timeout: int) -> _FakeResponse:
            """记录唯一请求并返回无需网络的虚构响应。"""

            calls.append(str(getattr(request, "full_url")))
            return _FakeResponse("网页正文".encode())

        snapshot = fetch_web_snapshot(
            "https://8.8.8.8/source",
            observed_at=datetime(2026, 8, 22, tzinfo=UTC),
            opener=opener,
        )

        self.assertEqual(["https://8.8.8.8/source"], calls)
        self.assertEqual("https://8.8.8.8/final", snapshot.final_url)
        self.assertEqual(64, len(snapshot.content_sha256))
        self.assertEqual("网页正文", snapshot.text)

    def test_web_snapshot_blocks_local_and_credential_urls(self) -> None:
        """网页入口不得访问本地网络或接受 URL 内凭据。"""

        for url in ("file:///tmp/a", "http://localhost/a", "https://user:pass@8.8.8.8/a"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                fetch_web_snapshot(url)

    def test_explicit_history_is_sanitized_bounded_and_non_formal(self) -> None:
        """历史只写非正式目录，脱敏且按时间和条数清理。"""

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            formal = root / "doc-example" / "README.md"
            formal.parent.mkdir()
            formal.write_text("unchanged\n", encoding="utf-8")
            now = datetime(2026, 8, 22, tzinfo=UTC)
            old = save_ingest_history(
                root,
                {"status": "blocked", "raw_content": "omit", "reason": "token=top-secret"},
                recorded_at=now - timedelta(days=31),
            )
            latest = None
            for index in range(101):
                latest = save_ingest_history(
                    root,
                    {"status": "analyzed", "index": index, "note": "password=hunter2"},
                    recorded_at=now + timedelta(microseconds=index),
                )

            files = sorted((root / ".context-atlas" / "ingest-history").glob("*.json"))
            serialized = "\n".join(path.read_text(encoding="utf-8") for path in files)
            self.assertEqual(100, len(files))
            self.assertNotIn(Path(old.path).name, {path.name for path in files})
            self.assertNotIn("top-secret", serialized)
            self.assertNotIn("hunter2", serialized)
            self.assertNotIn("raw_content", serialized)
            self.assertEqual("unchanged\n", formal.read_text(encoding="utf-8"))
            self.assertIsNotNone(latest)
            self.assertFalse(latest.formal_knowledge_written)


if __name__ == "__main__":
    unittest.main()
