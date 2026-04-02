#!/bin/bash
set -eo pipefail

# ===================== 配置项 =====================
APP_NAME="kio"
IMAGE_NAME="kio-1.0"
CONTAINER_NAME="kio-app"
HOST_PORT="9000"
# ==================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO] $*${NC}"; }
warn() { echo -e "${YELLOW}[WARN] $*${NC}"; }
error() { echo -e "${RED}[ERROR] $*${NC}"; exit 1; }

info "================================================"
info " 🚀 开始自动部署 $APP_NAME"
info "================================================"

# 检查 Docker 是否运行
if ! docker info >/dev/null 2>&1; then
  error "Docker 未运行，请先启动 Docker！"
fi

# 1. 停止旧容器
info "\n[1/6] 停止旧容器 $CONTAINER_NAME..."
if docker ps --filter "name=^/$CONTAINER_NAME$" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
  docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || warn "停止容器失败，可能已停止"
else
  warn "容器 $CONTAINER_NAME 未运行，跳过停止"
fi

# 2. 删除旧容器
info "[2/6] 删除旧容器 $CONTAINER_NAME..."
if docker ps -a --filter "name=^/$CONTAINER_NAME$" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
  docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || warn "删除容器失败"
else
  warn "容器 $CONTAINER_NAME 不存在，跳过删除"
fi

# 检查端口是否被占用
if lsof -i:$HOST_PORT >/dev/null 2>&1; then
  error "端口 $HOST_PORT 已被占用，无法启动！"
fi

# 3. 构建镜像
info "[3/6] 构建镜像：$IMAGE_NAME"
if ! docker build -t "$IMAGE_NAME" .; then
  error "镜像构建失败！"
fi

# 4. 清理悬空镜像（避免占空间）
info "[4/6] 清理旧悬空镜像"
#docker image prune -f --filter "dangling=true" >/dev/null 2>&1 || true

# 5. 启动新容器
info "[5/6] 启动新容器：$CONTAINER_NAME"
if ! docker run -d \
  --restart=always \
  --name "$CONTAINER_NAME" \
  -p "$HOST_PORT":9000 \
  "$IMAGE_NAME"; then
  error "容器启动失败！"
fi

# 6. 健康检查
info "[6/6] 检查容器状态..."
sleep 2
if docker ps --filter "name=^/$CONTAINER_NAME$" --format "{{.Status}}" | grep -q "Up"; then
  info "✅ 容器启动成功！"
else
  error "❌ 容器启动后异常退出！"
fi

info "\n================================================"
info "✅ 部署成功！"
info "🌐 访问地址: http://本机IP:$HOST_PORT"
info "📜 查看日志: docker logs -f $CONTAINER_NAME"
info "================================================"


# chmod +x deploy.sh
# ./deploy.sh
