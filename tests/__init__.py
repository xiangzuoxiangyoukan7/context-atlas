"""测试包初始化。"""

from __future__ import annotations

import os
import sys
import tempfile


if os.name == "nt":

    def _windows_sandbox_mkdtemp(
        suffix: str | None = None,
        prefix: str | None = None,
        dir: str | None = None,
    ) -> str:
        """兼容限制 0700 子目录写入的受管 Windows 测试环境。"""

        prefix, suffix, directory, output_type = tempfile._sanitize_params(  # type: ignore[attr-defined]
            prefix, suffix, dir
        )
        names = tempfile._get_candidate_names()  # type: ignore[attr-defined]
        if output_type is bytes:
            names = map(os.fsencode, names)

        for _ in range(tempfile.TMP_MAX):
            name = next(names)
            path = os.path.join(directory, prefix + name + suffix)
            sys.audit("tempfile.mkdtemp", path)
            try:
                os.mkdir(path, 0o777)
            except (FileExistsError, PermissionError):
                continue
            return os.path.abspath(path)
        raise FileExistsError("找不到可用的测试临时目录名")

    tempfile.mkdtemp = _windows_sandbox_mkdtemp
