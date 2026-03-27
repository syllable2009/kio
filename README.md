## 项目概览

该仓库包含两个 FastAPI HTTP 服务：`kio` 和 `dio`。

每个服务都采用“标准工程化分层”：

* `api`：HTTP 路由层（FastAPI）
* `services`：业务层（编排）
* `db`：数据访问层（当前示例用占位 `HealthRepository`）

当前示例接口：

* `GET /health` -> `{"status": "ok"}`

## 启动方式

* 启动 `kio`：`uv run kio/app.py`
* 启动 `dio`：`uv run dio/app.py`

环境变量：

* `KIO_HOST`/`KIO_PORT`/`KIO_RELOAD`（默认 `0.0.0.0:9000`, `reload=1`）
* `DIO_HOST`/`DIO_PORT`/`DIO_RELOAD`（默认 `0.0.0.0:9001`, `reload=1`）

## swagger

* `kio`：`http://127.0.0.1:9000/docs`
* `dio`：`http://127.0.0.1:9001/docs`


## 验证接口

启动后分别访问：

* `kio`：`http://127.0.0.1:9000/health`
* `dio`：`http://127.0.0.1:9001/health`

返回：

```json
{"status":"ok"}
```
