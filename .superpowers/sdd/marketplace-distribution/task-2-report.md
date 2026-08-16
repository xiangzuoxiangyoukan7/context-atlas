# Task 2 Report

- status: completed
- scope: 使用 `marketplaces/context-atlas/` 作为 Marketplace 发布包根，未写仓库根 `.agents`
- commit: skipped
- commit_reason: 当前环境无法可靠写入 `.git/index.lock`，按 brief 不强行提交

## Changes

- 新增 `marketplaces/context-atlas/.agents/plugins/marketplace.json`
- 新增 `marketplaces/context-atlas/.claude-plugin/marketplace.json`
- 更新 `scripts/project_kb/plugin_contract.py`，把 Marketplace 读取根切到 `marketplaces/context-atlas/`，并校验：
  - 顶层 `name`
  - `interface.displayName`
  - 非空 `plugins`
  - 第一条插件的 `name`
  - `source.source == "local"`
  - `source.path == "./plugins/context-atlas"`
  - `policy.installation == "AVAILABLE"`
  - `policy.authentication == "ON_INSTALL"`
  - `category == "Productivity"`
  - 禁止插件条目出现非标准字段
- 更新 `tests/unit/test_plugin_contract.py` 的 fixture 与断言路径，统一指向 `marketplaces/context-atlas/`

## Test command output

### RED

Command:

```powershell
py -m unittest tests.unit.test_plugin_contract
```

Output:

```text
.........F.E.
======================================================================
ERROR: test_two_marketplaces_reference_the_same_plugin (tests.unit.test_plugin_contract.PluginContractTests.test_two_marketplaces_reference_the_same_plugin)
两个 Marketplace 应暴露同一个插件和稳定来源路径。
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\loong-workspace-python\context-atlas\tests\unit\test_plugin_contract.py", line 105, in test_two_marketplaces_reference_the_same_plugin
    codex_marketplace, claude_marketplace = load_marketplace_manifests(ROOT)
                                            ~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "D:\loong-workspace-python\context-atlas\scripts\project_kb\plugin_contract.py", line 52, in load_marketplace_manifests
    codex = _load_object(root / ".agents" / "plugins" / "marketplace.json")
  File "D:\loong-workspace-python\context-atlas\scripts\project_kb\plugin_contract.py", line 31, in _load_object
    payload = json.loads(path.read_text(encoding="utf-8"))
                         ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^
  File "C:\Users\Seven\AppData\Local\Python\pythoncore-3.14-64\Lib\pathlib\__init__.py", line 787, in read_text
    with self.open(mode='r', encoding=encoding, errors=errors, newline=newline) as f:
         ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\Seven\AppData\Local\Python\pythoncore-3.14-64\Lib\pathlib\__init__.py", line 771, in open
    return io.open(self, mode, buffering, encoding, errors, newline)
           ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: 'D:\\loong-workspace-python\\context-atlas\\.agents\\plugins\\marketplace.json'

======================================================================
FAIL: test_repository_contract_has_no_errors (tests.unit.test_plugin_contract.PluginContractTests.test_repository_contract_has_no_errors)
验证 repository_contract_has_no_errors 场景。
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\loong-workspace-python\context-atlas\tests\unit\test_plugin_contract.py", line 100, in test_repository_contract_has_no_errors
    self.assertEqual([], validate_plugin_contract(ROOT))
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: Lists differ: [] != ["[Errno 2] No such file or directory: 'D:[83 chars]on'"]

Second list contains 1 additional elements.
First extra element 0:
"[Errno 2] No such file or directory: 'D:\\\\loong-workspace-python\\\\context-atlas\\\\.agents\\\\plugins\\\\marketplace.json'"

- []
+ ['[Errno 2] No such file or directory: '
+  "'D:\\\\loong-workspace-python\\\\context-atlas\\\\.agents\\\\plugins\\\\marketplace.json'"]

----------------------------------------------------------------------
Ran 13 tests in 0.231s

FAILED (failures=1, errors=1)
```

### GREEN

Command:

```powershell
py -m unittest tests.unit.test_plugin_contract
```

Output:

```text
.............
----------------------------------------------------------------------
Ran 13 tests in 0.484s

OK
```
