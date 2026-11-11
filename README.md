# TaskFlow API + Pytest 自动化测试实战项目

![Python](https://img.shields.io/badge/Python-3.12-blue) ![Pytest](https://img.shields.io/badge/Testing-Pytest-green) ![CI](https://img.shields.io/badge/CI-GitHub_Actions-blue)

一个可以直接上传 GitHub 的**完整练习项目**：包含一个真正可运行的任务管理 REST API、使用 `requests` 的 API Client、单元测试与真实 HTTP 集成测试、自动创建/清理 Fixture、参数化异常测试、日志、HTML + JUnit XML 报告，以及 GitHub Actions CI。

**不依赖 PetClinic / Docker / 数据库。** 测试启动时会自动在本机随机端口启动 HTTP 服务，结束后关闭；每条集成测试拥有独立内存数据。可在 Windows 本地和 GitHub Actions 的 Ubuntu 环境执行。

> 这是用于学习测试开发的教学 API，数据只保存在内存中，手动停止服务后不会持久化；不应直接公开部署到互联网。

## 项目结构

```text
.github/workflows/pytest-ci.yml  # push/PR 自动运行，上传 Artifacts
src/taskflow/app.py              # Python 标准库实现的 REST API
src/taskflow/validation.py       # 数据校验，供单元测试
src/taskflow/client.py           # Requests 封装 GET/POST/PUT/DELETE + logging
tests/conftest.py               # Fixture：启动/关闭测试服务、生成/删除数据
tests/unit/                    # 单元测试
 tests/integration/              # 真实 HTTP 集成测试
logs/                           # pytest.log
reports/                        # HTML 和 JUnit XML
pyproject.toml                  # 依赖、Marker、日志配置
 docs/LEARNING_GUIDE.md         # 复习路线与练习任务
```

## 1. Windows 一键开始（PowerShell）

解压后进入项目根目录（这个目录下能看到 `pyproject.toml`）：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
```

如果电脑上没有 `py` 启动器，可使用 `python -m venv .venv`。依赖安装需要联网。

## 2. 运行全部测试 + 生成两种报告

```powershell
.\.venv\Scripts\python.exe -m pytest -v --html=reports/report.html --self-contained-html --junitxml=reports/results.xml
```

测试中 **不需要提前手动启动后端**，因为 `tests/conftest.py` 的 `live_server` Fixture 会自动启动并关闭服务。

查看 HTML 报告：

```powershell
Invoke-Item .\reports\report.html
```

其他常用命令：

```powershell
.\.venv\Scripts\python.exe -m pytest -m unit -v
.\.venv\Scripts\python.exe -m pytest -m integration -v
.\.venv\Scripts\python.exe -m pytest -m "integration and negative" -v
.\.venv\Scripts\python.exe -m pytest -m smoke -v
.\.venv\Scripts\python.exe -m pytest -v --log-cli-level=INFO
```

日志写入 `logs/pytest.log`。日志只记录请求方法、URL、状态码和耗时，不打印请求体或密钥。

## 3. 可选：手动启动 REST API

打开**第一个** PowerShell 窗口：

```powershell
.\.venv\Scripts\python.exe -m taskflow.app --port 8000
```

然后浏览器访问： http://127.0.0.1:8000/api/health

在**第二个** PowerShell 窗口调用 API（PowerShell 内置 Invoke-RestMethod）：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/tasks

$body = @{ title = 'Learn Pytest'; priority = 'high'; completed = $false } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/tasks -Method Post -ContentType 'application/json' -Body $body

Invoke-RestMethod http://127.0.0.1:8000/api/tasks
```

停止服务：在第一个窗口按 **Ctrl+C**。

## 4. REST API 说明

| 方法 | 路径 | 作用 | 成功码 |
|---|---|---|---|
| GET | `/api/health` | 健康检查 | 200 |
| GET | `/api/tasks` | 查询任务列表 | 200 |
| GET | `/api/tasks/{id}` | 查询指定任务 | 200 |
| POST | `/api/tasks` | 创建任务 | 201 |
| PUT | `/api/tasks/{id}` | 整体更新任务 | 200 |
| DELETE | `/api/tasks/{id}` | 删除任务 | 204 |

任务字段：`title`（必填，去首尾空白后 1–50 字符）、`priority`（low/medium/high，默认 medium）、`completed`（布尔值，默认 false）。无效输入返回 400，不存在资源返回 404。

成功创建示例：

```json
{"id": 1, "title": "Learn Pytest", "priority": "high", "completed": false}
```

## 5. 上传 GitHub（新建一个空仓库）

建议仓库名：`taskflow-pytest-automation`。在 GitHub 创建 **空仓库**，不要预先创建 README/License，避免首次推送冲突。以下命令在项目根目录运行：

```powershell
git init
git add .
git commit -m "Initial TaskFlow API automation project"
git branch -M main
git remote add origin https://github.com/你的用户名/taskflow-pytest-automation.git
git push -u origin main
```

GitHub 仓库 → **Actions** → **TaskFlow Pytest CI** → 最新运行记录 → **Artifacts** → 下载 `taskflow-test-reports`。它包含 `reports/report.html`、`reports/results.xml` 和 `logs/pytest.log`。

如 GitHub 提示需要登录认证，请按 Git Credential Manager / GitHub 官方登录流程操作，不要把 Token 写入仓库文件。

## 6. 面试能怎么介绍？

> 我独立学习和整理了一套基于 Python、Requests、Pytest 的 REST API 自动化测试练习项目。将 GET/POST/PUT/DELETE 请求封装为统一客户端，使用 Fixture 自动管理服务与数据生命周期，结合参数化覆盖正常、边界和异常场景，通过 Marker 分类执行测试，使用 logging 记录请求耗时和失败信息，并利用 GitHub Actions 在提交代码后自动执行测试、生成 HTML/JUnit XML 报告并上传 Artifacts。

**注意**：上面的描述应在你亲自将代码上传 GitHub 且 CI 实际运行通过之后使用；本项目中的服务端是专门构建的练习系统，不能把它描述为生产业务系统。

继续学习请看：[`docs/LEARNING_GUIDE.md`](docs/LEARNING_GUIDE.md)。
