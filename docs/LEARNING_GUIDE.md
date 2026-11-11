# TaskFlow 项目复习路线（对应前 1–33 课）

## 一、建议按顺序阅读这 5 个文件

1. `src/taskflow/validation.py`：字典、字符串、`strip()`、`len()`、`isinstance()`、`raise`。
2. `tests/unit/test_validation.py`：`assert`、`pytest.raises()`、`match`、`@pytest.mark.parametrize()`、边界值。
3. `src/taskflow/client.py`：class、`__init__`、GET/POST/PUT/DELETE、`json=payload`、`response.status_code`、`response.json()`、logging。
4. `tests/conftest.py`：`@pytest.fixture`、`yield`、Setup/Teardown、数据隔离、自动创建删除任务。
5. `tests/integration/`：对真正监听端口的 HTTP 服务进行 Requests 测试，检查 200/201/204/400/404。

## 二、课程知识点对应表

| 原来学过的知识 | 在新项目里找哪里 |
|---|---|
| GET、Response、status_code、JSON | `client.py`, `test_tasks_crud.py` |
| 字典、列表、for、len、in | `test_fixture_and_logging.py` |
| `assert`、FAILED、调试 | 任意 `test_*.py` |
| `isinstance`、`strip` | `validation.py` |
| Fixture / `yield` / `conftest.py` | `tests/conftest.py` |
| 参数化 / 元组 / 边界值 | `test_validation.py`, `test_tasks_negative.py` |
| `pytest.raises` 和 `match` | `test_validation.py` |
| POST / PUT / DELETE | `client.py`, `test_tasks_crud.py` |
| 测试数据隔离与清理 | `live_server`, `created_task` Fixtures |
| Marker + `-m` | `pyproject.toml`, 所有测试 |
| 日志 logging | `client.py`, `logs/pytest.log` |
| HTML + JUnit XML 报告 | `reports/`, CI 文件 |
| GitHub Actions / Artifacts | `.github/workflows/pytest-ci.yml` |

## 三、5 个由浅入深的动手练习

### 练习 1：修改一条断言，观察 FAILED
在 `test_health()` 中暂时把预期 `200` 改成 `404`，运行后查看 `>` 与 `E assert 200 == 404`。做完后**恢复**为 200。

### 练习 2：增加参数化边界用例
`title` 允许的最大长度为 50。尝试在 `tests/unit/test_validation.py` 添加长度 49、50、51 的测试，分别预期通过、通过、抛出 ValueError。

### 练习 3：观察 Fixture 自动清理
执行 `python -m pytest tests/integration/test_tasks_crud.py -v --log-cli-level=INFO`，观察 `SETUP created task` / `TEARDOWN delete task` 日志。

### 练习 4：练习异常测试
尝试通过 API 创建 `{"title": "   "}`，应该得到 HTTP 400；而直接调用 `validate_task({"title": "   "})` 则会在 Python 中抛出 ValueError。区别是什么？

### 练习 5：触发一次 GitHub Actions
在 README 加一句项目介绍，提交并推送。在 GitHub 的 Actions 中找到运行记录，下载 Artifacts，打开 HTML 报告。

## 四、8 个测试开发面试复习问题

1. HTTP GET、POST、PUT、DELETE 分别有什么作用？
2. 200、201、204、400、404 分别表示什么？
3. `requests.post(url, json=payload)` 为什么使用 `json=`？
4. Fixture 的 `yield` 前后分别做什么？测试失败时会不会清理？
5. `@pytest.mark.parametrize` 如何把一个函数执行多次？
6. `@pytest.mark.integration` 和 `-m integration` 的关系？
7. 服务器 HTTP 400 与 Python 的 ValueError 有什么区别？
8. 为什么 CI 要设置 `if: always()` 上传报告？

## 五、常见问题排查

- `No module named taskflow`：需要在项目根目录安装 `python -m pip install -e ".[test]"`，不要仅复制某一个测试文件。
- `unrecognized arguments: --html`：没安装 `pytest-html`，重新执行安装命令。
- `FileNotFoundError: logs/pytest.log`：确保 `logs` 文件夹存在，项目包内已包含 `logs/.gitkeep`。
- `Connection refused`：集成测试正常不需要手动启动服务器；请确认运行的是本项目的 `tests/`，并保留 `tests/conftest.py`。如果手动调用 `8000` 端口，需要先启动 `python -m taskflow.app --port 8000`。
- GitHub CI 显示 Failure：点击失败步骤查看报错；不要通过 `continue-on-error` 隐藏失败。

## 六、项目限制

- 服务器数据仅在内存，不能持久化，关闭后任务全部消失。
- 为练习而实现的标准库 REST API，非生产应用，无鉴权和数据库。
- 真实 HTTP 测试由 Fixture 自动启动本机服务，不依赖 Docker 或云端外部 API。
- CI 成功与否需要在你上传 GitHub 后以 Actions 实际运行结果为准。
