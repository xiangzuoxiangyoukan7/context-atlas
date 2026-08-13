# 统一关系引用与影响分析 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 `rel_<type>` Obsidian 文件链接、受控关系目录、反向索引和三级影响分析，为需求、功能、接口、数据表、任务和验收证据联动提供确定性底座。

**Architecture:** `relation_catalog.py` 读取唯一 JSON 关系目录，`relations.py` 解析并校验 Wikilink、建立正反向索引，`impact.py` 根据变化类型与反向关系生成 `required`、`review_required`、`informational` 结果。现有验证器负责组合这些模块；CLI 只输出分析结果，不修改知识文件或裁决业务含义。

**Tech Stack:** Python 3 标准库、`unittest`、Markdown、受限 YAML Front Matter、JSON、Obsidian Wikilink、Git。

## Global Constraints

- 所有用户可见说明、Python 模块/类/方法/关键属性注释使用中文；Python 参数和返回值必须有类型标注。
- 正式关系只使用扁平 `rel_<type>` 字段，不维护第二套裸 ID 关系。
- 每个关系值必须同时包含目标 Markdown 路径、可选标题或块锚点、目标知识项 ID。
- 关系只保存一个权威方向；反向消费者由检查器计算，基础文档不得手工维护反向列表。
- 未登记 `rel_*` 必须报错；检查器不得自动修改文档。
- 影响分析只输出 `required`、`review_required`、`informational`，不能自动确认业务结论。
- 首期只使用 Python 标准库，不引入 YAML、图数据库或 Obsidian 运行时依赖。
- 根资产为权威实现，`skills/context-atlas/assets/` 通过同步脚本生成并检查一致性。
- 每个任务遵循失败测试、最小实现、通过验证、独立提交。

---

### Task 1: 支持关系字段所需的 Front Matter 列表语法

**Files:**
- Modify: `scripts/project_kb/frontmatter.py`
- Modify: `skills/context-atlas/assets/scripts/project_kb/frontmatter.py`（由同步脚本更新）
- Test: `tests/unit/test_frontmatter.py`

**Interfaces:**
- Consumes: Markdown UTF-8 文档。
- Produces: `parse_document(path: Path) -> DocumentRecord`，支持行内列表和两空格缩进的 `- "[[...]]"` 字符串列表。

- [ ] **Step 1: 写块列表成功与嵌套对象拒绝测试**

```python
def test_frontmatter_parses_quoted_relation_block_list(self) -> None:
    document = self.write("""---
id: FEATURE-001
rel_implements:
  - "[[01-功能/需求#REQ-001 下单|REQ-001]]"
---
""")
    self.assertEqual(
        ["[[01-功能/需求#REQ-001 下单|REQ-001]]"],
        parse_document(document).metadata["rel_implements"],
    )

def test_frontmatter_still_rejects_nested_mapping(self) -> None:
    document = self.write("---\nrelations:\n  implements: REQ-001\n---\n")
    with self.assertRaises(FrontMatterError):
        parse_document(document)
```

- [ ] **Step 2: 运行测试确认旧解析器因 `nested metadata is unsupported` 失败**

Run: `py -m unittest tests.unit.test_frontmatter -v`

- [ ] **Step 3: 最小实现标量列表状态机**

实现 `_unquote_scalar(value: str) -> str`，只去除成对单/双引号；`parse_document` 允许空值键后连续的两个空格加 `- ` 列表项，拒绝混用标量、空列表项、三层缩进和映射项。

- [ ] **Step 4: 运行 Front Matter 与全量测试**

Run: `py -m unittest tests.unit.test_frontmatter -v`

Run: `py -m unittest discover -s tests -p 'test_*.py'`

- [ ] **Step 5: 同步资产并提交**

```powershell
py scripts/sync_skill_assets.py
git add scripts/project_kb/frontmatter.py skills/context-atlas/assets/scripts/project_kb/frontmatter.py tests/unit/test_frontmatter.py
git commit -m "解析：支持关系链接列表"
```

---

### Task 2: 建立受控关系目录与影响规则目录

**Files:**
- Create: `schemas/relation-catalog.json`
- Create: `scripts/project_kb/relation_catalog.py`
- Test: `tests/unit/test_relation_catalog.py`

**Interfaces:**
- Produces: `RelationDefinition(field: str, name_zh: str, source_prefixes: frozenset[str], target_prefixes: frozenset[str], direction: str, status: str)`。
- Produces: `RelationCatalog.load(path: Path) -> RelationCatalog`。
- Produces: `RelationCatalog.get(field: str) -> RelationDefinition | None`。
- Produces: `RelationCatalog.impact_level(field: str, change_type: str) -> str`。

- [ ] **Step 1: 写目录完整性失败测试**

```python
def test_catalog_declares_required_core_relations(self) -> None:
    catalog = RelationCatalog.load(ROOT / "schemas" / "relation-catalog.json")
    self.assertEqual(
        {
            "rel_supported_by", "rel_conforms_to", "rel_implements",
            "rel_exposes", "rel_reads", "rel_writes", "rel_depends_on",
            "rel_verified_by", "rel_changes", "rel_supersedes",
            "rel_logical_parent", "rel_evidenced_by", "rel_executes",
        },
        set(catalog.relations),
    )
```

另写反例：缺中文名、非法状态、空起点、未知影响等级和重复字段必须抛出 `ValueError`。

- [ ] **Step 2: 运行测试确认模块或目录缺失**

Run: `py -m unittest tests.unit.test_relation_catalog -v`

- [ ] **Step 3: 创建目录和加载器**

JSON 每条关系必须包含 `field`、`name_zh`、`source_prefixes`、`target_prefixes`、`direction: forward_only`、`status: active`、`impact_rules` 和 `default_impact: review_required`。明确变化规则至少覆盖：

- `rel_reads + field_removed/type_changed/enum_value_removed -> required`
- `rel_writes + required_added/type_changed/enum_value_removed -> required`
- `rel_logical_parent + key_changed -> required`
- `rel_verified_by + behavior_changed -> review_required`
- `rel_conforms_to + rule_changed -> review_required`
- `formatting_only/file_moved -> informational`

- [ ] **Step 4: 运行目录测试、注释检查和全量测试**

Run: `py -m unittest tests.unit.test_relation_catalog -v`

Run: `py scripts/check_python_documentation.py --root .`

- [ ] **Step 5: 提交**

```powershell
git add schemas/relation-catalog.json scripts/project_kb/relation_catalog.py tests/unit/test_relation_catalog.py
git commit -m "规范：建立受控关系目录"
```

---

### Task 3: 解析 Wikilink 并建立知识项与反向关系索引

**Files:**
- Create: `scripts/project_kb/relations.py`
- Modify: `scripts/project_kb/model.py`
- Test: `tests/unit/test_relations.py`

**Interfaces:**
- Produces: `KnowledgeTarget(identifier: str, path: Path, anchor: str | None, kind: str)`。
- Produces: `RelationEdge(field: str, source: KnowledgeTarget, target: KnowledgeTarget)`。
- Produces: `RelationIndex.build(root: Path, records: Iterable[DocumentRecord], catalog: RelationCatalog) -> tuple[RelationIndex, list[Issue]]`。
- Produces: `RelationIndex.outgoing(identifier: str) -> tuple[RelationEdge, ...]`。
- Produces: `RelationIndex.incoming(identifier: str) -> tuple[RelationEdge, ...]`。

- [ ] **Step 1: 写合法索引和精确错误码测试**

使用临时知识库验证：

```python
self.assertEqual("REQ-001", index.outgoing("FEATURE-001")[0].target.identifier)
self.assertEqual("FEATURE-001", index.incoming("REQ-001")[0].source.identifier)
```

反例必须得到：

- `KB_REL_FIELD_UNKNOWN`
- `KB_REL_LINK_FORMAT`
- `KB_REL_TARGET_FILE`
- `KB_REL_TARGET_ID`
- `KB_REL_TARGET_ANCHOR`
- `KB_REL_DIRECTION`
- `KB_REL_DUPLICATE`

- [ ] **Step 2: 运行测试确认 `relations` 模块缺失**

Run: `py -m unittest tests.unit.test_relations -v`

- [ ] **Step 3: 实现 Wikilink 与索引**

只接受：

```text
[[相对/目标文件#可选锚点|TARGET-ID]]
```

路径相对知识库根且隐含 `.md`；禁止绝对路径、`..`、空显示 ID。目标 ID 可以来自目标文件 Front Matter `id`，也可以来自正文标题 `## TARGET-ID 中文名`；聚合文件关系必须带标题锚点，锚点在目标文件中必须唯一。

- [ ] **Step 4: 运行测试和安全路径反例**

Run: `py -m unittest tests.unit.test_relations -v`

- [ ] **Step 5: 提交**

```powershell
git add scripts/project_kb/model.py scripts/project_kb/relations.py tests/unit/test_relations.py
git commit -m "检查：建立关系与反向索引"
```

---

### Task 4: 将关系校验接入知识库检查器

**Files:**
- Modify: `scripts/project_kb/validator.py`
- Modify: `scripts/check_knowledge_base.py`
- Create: `tests/fixtures/invalid/relation-unknown-field/`
- Create: `tests/fixtures/invalid/relation-broken-target/`
- Create: `tests/fixtures/invalid/relation-wrong-direction/`
- Modify: `tests/unit/test_validator.py`

**Interfaces:**
- `ValidationConfig` 增加 `relation_catalog_path: Path | None = None`。
- `validate(root: Path, config: ValidationConfig) -> list[Issue]` 自动使用 `schema_root/relation-catalog.json`。

- [ ] **Step 1: 写三个端到端失败夹具测试**

```python
def test_invalid_relation_fixtures_have_exact_codes(self) -> None:
    expected = {
        "relation-unknown-field": "KB_REL_FIELD_UNKNOWN",
        "relation-broken-target": "KB_REL_TARGET_FILE",
        "relation-wrong-direction": "KB_REL_DIRECTION",
    }
```

- [ ] **Step 2: 运行确认夹具被旧验证器错误接受**

Run: `py -m unittest tests.unit.test_validator -v`

- [ ] **Step 3: 在 Schema 验证后、追溯验证前接入关系索引**

关系目录缺失或格式错误必须返回稳定问题 `KB_REL_CATALOG`，不能用 Python traceback 代替用户错误。

- [ ] **Step 4: 验证文本和 JSON 报告都能定位关系字段**

Run: `py scripts/check_knowledge_base.py tests/fixtures/invalid/relation-broken-target --schema-root schemas --format json`

- [ ] **Step 5: 提交**

```powershell
git add scripts/project_kb/validator.py scripts/check_knowledge_base.py tests/fixtures/invalid tests/unit/test_validator.py
git commit -m "检查：验证类型化文档关系"
```

---

### Task 5: 实现三级影响分析和命令行入口

**Files:**
- Create: `scripts/project_kb/impact.py`
- Create: `scripts/analyze_knowledge_impact.py`
- Test: `tests/unit/test_impact.py`
- Test: `tests/integration/test_impact_cli.py`

**Interfaces:**
- Produces: `ImpactItem(changed_id: str, affected_id: str, relation: str, level: str, depth: int, source_path: Path, affected_path: Path)`。
- Produces: `analyze_impact(index: RelationIndex, catalog: RelationCatalog, changed_id: str, change_type: str, max_depth: int = 2) -> list[ImpactItem]`。
- CLI: `py scripts/analyze_knowledge_impact.py ROOT --schema-root SCHEMAS --changed-id ID --change-type TYPE --format {text,json}`。

- [ ] **Step 1: 写直接、间接和未知变化测试**

```python
self.assertEqual("required", impacts[0].level)
self.assertEqual(1, impacts[0].depth)
self.assertEqual("review_required", impacts[1].level)
self.assertEqual(2, impacts[1].depth)
```

未知变化类型不得猜测为 `required`，统一降级为 `review_required`；`formatting_only` 为 `informational`。

- [ ] **Step 2: 运行测试确认接口缺失**

Run: `py -m unittest tests.unit.test_impact tests.integration.test_impact_cli -v`

- [ ] **Step 3: 实现反向遍历和稳定排序**

直接影响使用目录规则；间接影响最高只能继承为 `review_required`，不得把不确定传播升级为 `required`。结果按等级、深度、受影响 ID 排序并同时包含来源与受影响文件路径。

- [ ] **Step 4: 验证 CLI 只读且退出码稳定**

- 成功完成分析：0。
- changed ID 不存在、关系目录无效：2。
- 不因存在 `required` 影响返回失败；影响结果是 Proposal 输入，不是任务执行门禁。

- [ ] **Step 5: 提交**

```powershell
git add scripts/project_kb/impact.py scripts/analyze_knowledge_impact.py tests/unit/test_impact.py tests/integration/test_impact_cli.py
git commit -m "分析：增加文档变化影响清单"
```

---

### Task 6: 更新规则、模板、Skill 和黄金样例

**Files:**
- Modify: `rules/知识治理规则.md`
- Create: `templates/core/doc-project/02-架构与契约/关系目录.md`
- Create: `templates/core/doc-project/03-实施与验收/影响分析/TEMPLATE.md`
- Modify: `templates/core/doc-project/README.md`
- Modify: `skills/context-atlas/references/知识采集与确认.md`
- Create: `skills/context-atlas/references/关系与影响分析.md`
- Modify: `skills/context-atlas/SKILL.md`
- Modify: `examples/single-stack/`
- Modify: `examples/multi-stack/`
- Test: `tests/unit/test_skill_package.py`
- Test: `tests/integration/test_examples.py`

**Interfaces:**
- 权威规则增加稳定编号 `RULE-REL-002` 和 `RULE-IMPACT-002`。
- 模板关系只使用 `rel_<type>` Wikilink。
- 影响分析模板字段包含来源、变化类型、受影响项、等级、深度、处理状态、确认人和证据链接。

- [ ] **Step 1: 写资产和样例失败测试**

测试必须运行检查器，而不是只搜索文本；两套样例至少形成 `REQ -> FEATURE -> TABLE/API -> AC/EVIDENCE` 的可计算关系链，并验证反向影响输出。

- [ ] **Step 2: 运行测试确认模板与 Skill 引用缺失**

Run: `py -m unittest tests.unit.test_skill_package tests.integration.test_examples -v`

- [ ] **Step 3: 更新权威资产和中文使用契约**

说明必须明确：关系的写法、读取方式、禁止反向手填、文件移动处理、三级影响含义、人工确认边界和 Obsidian 图谱粒度。

- [ ] **Step 4: 同步并验证自包含产物**

```powershell
py scripts/sync_skill_assets.py
py scripts/sync_skill_assets.py --check
py scripts/check_knowledge_base.py examples/single-stack --schema-root schemas
py scripts/check_knowledge_base.py examples/multi-stack --schema-root schemas
```

- [ ] **Step 5: 提交**

```powershell
git add rules templates skills examples tests
git commit -m "文档：落地关系与影响分析规范"
```

---

### Task 7: 全量验证并记录阶段证据

**Files:**
- Create: `doc-atlas/03-实施与验收/任务包/TASK-KB-007-统一关系与影响分析.md`
- Create: `doc-atlas/03-实施与验收/验收证据/统一关系与影响分析.md`
- Modify: `doc-atlas/03-实施与验收/验收矩阵.md`
- Modify: `doc-atlas/03-实施与验收/当前变更.md`

**Interfaces:**
- 新增 `KB-AC-30`：关系链接和方向确定性验证。
- 新增 `KB-AC-31`：反向索引和三级影响结果。
- 新增 `KB-AC-32`：模板、Skill、黄金样例和自包含检查一致。

- [ ] **Step 1: 运行全量门禁**

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
py -m unittest discover -s tests -p 'test_*.py'
py scripts/check_python_documentation.py --root .
py scripts/check_rule_coverage.py --root .
py scripts/sync_skill_assets.py --check
py scripts/check_knowledge_base.py examples/single-stack --schema-root schemas
py scripts/check_knowledge_base.py examples/multi-stack --schema-root schemas
py scripts/check_knowledge_base.py doc-atlas --schema-root schemas
git diff --check
```

- [ ] **Step 2: 运行代表性影响分析并记录脱敏摘要**

```powershell
py scripts/analyze_knowledge_impact.py examples/multi-stack --schema-root schemas --changed-id TABLE-ORDER-001 --change-type enum_value_removed --format json
```

证据只保存 ID、关系、等级、深度、文件相对路径和退出码，不保存项目外路径或模型正文。

- [ ] **Step 3: 更新任务包和验收矩阵**

只有链接格式、关系方向、反向索引、影响等级、Skill 同步和两套样例全部有成功证据时，`KB-AC-30`～`32` 才能标记 `passed`。

- [ ] **Step 4: 最终检查并提交**

```powershell
py scripts/check_knowledge_base.py doc-atlas --schema-root schemas
git diff --check
git add docs/superpowers/plans/2026-08-13-typed-relations-and-impact-analysis.md doc-atlas/03-实施与验收
git commit -m "验收：完成关系与影响分析阶段"
```

## Plan Self-Review

- 覆盖已批准的 `DIR-004`、`DIR-009`、`DIR-020`、`DIR-027`～`DIR-030`、`DIR-032`。
- 明确采用 Wikilink 唯一表示、受控目录、反向索引和三级影响，没有第二套关系字段。
- 不包含数据库字段和值域模型；该模型在关系底座完成后进入独立计划。
- 不包含自动知识捕获和人员身份；二者不会阻塞本计划独立验收。
- 所有任务均给出确定接口、错误码、测试命令和提交边界。
