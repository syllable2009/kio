#!/bin/bash
set -eo pipefail

# ===================== 配置项 =====================
APP_NAME="kio"
IMAGE_NAME="kio-1.0"
CONTAINER_NAME="kio-app"
HOST_PORT="9000"

# ===================== 远程服务器配置 =====================
REMOTE_HOST="192.168.31.124"    # 远程机器IP
REMOTE_USER="root"             # 远程用户名
REMOTE_PASS="你的服务器密码"   # 这里填密码
REMOTE_DIR="/opt/kio"          # 远程存放镜像的目录
# ==========================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO] $*${NC}"; }
warn() { echo -e "${YELLOW}[WARN] $*${NC}"; }
error() { echo -e "${RED}[ERROR] $*${NC}"; exit 1; }

# 自动 SSH / SCP 函数（自带密码，全程免输）
SSH() {
  sshpass -p "$REMOTE_PASS" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 "$REMOTE_USER@$REMOTE_HOST" "$@"
}
SCP() {
  sshpass -p "$REMOTE_PASS" scp -o StrictHostKeyChecking=no -q "$1" "$REMOTE_USER@$REMOTE_HOST:$2"
}

info "================================================"
info " 🚀 开始自动部署 $APP_NAME (本地构建 → 远程全自动部署)"
info "================================================"

# 检查本地 Docker
if ! docker info >/dev/null 2>&1; then
  error "Docker 未运行，请先启动 Docker！"
fi

# 检查 sshpass 已安装
if ! command -v sshpass &> /dev/null; then
  error "请先安装 sshpass：brew install sshpass 或 apt install sshpass -y"
fi

# ===================== 部署流程 =====================
info "\n[1/7] 构建镜像：$IMAGE_NAME"
docker build -t "$IMAGE_NAME" .

info "[2/7] 导出镜像：${IMAGE_NAME}.tar"
docker save -o "${IMAGE_NAME}.tar" "$IMAGE_NAME"

info "[3/7] 创建远程目录并传输镜像"
SSH "mkdir -p $REMOTE_DIR"
SCP "${IMAGE_NAME}.tar" "$REMOTE_DIR/"

info "[4/7] 远程加载镜像"
SSH "cd $REMOTE_DIR && docker load -i ${IMAGE_NAME}.tar"

info "[5/7] 远程清理旧容器"
SSH "
  docker stop $CONTAINER_NAME >/dev/null 2>&1 || true
  docker rm $CONTAINER_NAME >/dev/null 2>&1 || true
"

info "[6/7] 检查远程端口 $HOST_PORT 是否占用"
SSH "
  if command -v ss &>/dev/null; then
    if ss -tulpn | grep -q :$HOST_PORT; then
      echo 'ERROR: 端口 $HOST_PORT 已被占用' >&2
      exit 1
    fi
  fi
"

info "[7/7] 启动远程新容器"
SSH "
  docker run -d \
    --restart=always \
    --name $CONTAINER_NAME \
    -p $HOST_PORT:9000 \
    $IMAGE_NAME
"

# 健康检查
sleep 2
status=$(SSH "docker ps --filter 'name=^/${CONTAINER_NAME}$' --format '{{.Status}}'")
if [[ -z "$status" || ! "$status" =~ ^Up ]]; then
  error "容器启动失败！请检查远程日志"
fi

# 清理本地临时文件
rm -f "${IMAGE_NAME}.tar"

info "\n================================================"
info "✅ 全自动部署成功！"
info "🌐 访问地址: http://$REMOTE_HOST:$HOST_PORT"
info "📜 查看远程日志: ssh $REMOTE_USER@$REMOTE_HOST docker logs -f $CONTAINER_NAME"
info "================================================"




## 以下为本地docker启动操作

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
