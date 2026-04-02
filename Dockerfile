# syntax=docker/dockerfile:1.6
# 告诉 Docker：我用 1.6 语法，别用老规则解析
############################
# Builder: 用 Python 3.12 精简版镜像，命名为 builder，后面会用到
############################
FROM python:3.12-slim AS builder

# 进容器内的 /app 目录。
WORKDIR /app

# 安装 uv —— 一个比 pip 快 10~100 倍的 Python 包管理器
RUN pip install --no-cache-dir uv

# 只复制依赖清单文件，不复制代码 → 让 Docker 缓存更快。
COPY pyproject.toml uv.lock ./

# 根据清单安装所有运行依赖，生成虚拟环境 /app/.venv。
RUN uv sync --frozen --no-dev

# 复制你的项目代码
COPY kio ./kio


############################
# 重新开一个干净的精简镜像，只放运行需要的东西。
############################
FROM python:3.12-slim AS runtime

# 进入目录，安装 uv
WORKDIR /app

# Install `uv` so we can run the project with: `uv run kio/app.py`
RUN pip install --no-cache-dir uv

# 从 builder 阶段把依赖和代码复制过来，不重复安装，体积更小
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/kio ./kio
COPY --from=builder /app/pyproject.toml ./pyproject.toml
COPY --from=builder /app/uv.lock ./uv.lock

# 让容器里自动使用项目自己的虚拟环境（.venv），而不是系统自带的 Python
ENV VIRTUAL_ENV=/app/.venv
# 优先使用 .venv 里的命令，而不是系统命令
ENV PATH="/app/.venv/bin:$PATH"
# 告诉 Python：去 /app 目录下找包
ENV PYTHONPATH=/app:$PYTHONPATH
# 设置环境变量
ENV KIO_HOST=0.0.0.0
ENV KIO_PORT=9000
ENV KIO_RELOAD=0

EXPOSE 9000
# 让容器停止时更安全、更优雅。
STOPSIGNAL SIGTERM

# kio-1.0 runtime start
#CMD ["uv", "run", "kio/app.py"]
# 标准 Python 模块运行方式，同样能解决导入问题
# 运行 app.py,就是运行kio/app.py 这个文件里的全部顶层代码，特别是启动 Uvicorn/FastAPI 的那一段
CMD ["uv", "run", "-m", "kio.app"]

#cd /Users/jiaxiaopeng/pyhub/kio
#docker build -t kio-1.0 .
#docker run --rm -p 9000:9000 kio-1.0