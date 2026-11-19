#!/bin/bash
# ==============================================================================
# CloudVault - AWS EC2 User Data Bootstrap Script
# Môi trường: AWS Academy Learner Lab (Ubuntu 22.04 LTS)
# ==============================================================================

set -e

echo "[1/5] Updating packages and installing prerequisites..."
apt-get update -y
apt-get install -y ca-certificates curl gnupg lsb-release git

echo "[2/5] Installing Docker Engine..."
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

systemctl enable docker
systemctl start docker
usermod -aG docker ubuntu

echo "[3/5] Setting up project directory..."
DEPLOY_DIR="/opt/cloudvault"
mkdir -p $DEPLOY_DIR

# Thay thế bằng repo Git thực tế của nhóm:
# git clone https://github.com/your-username/cloudvault.git $DEPLOY_DIR
# cd $DEPLOY_DIR

echo "[4/5] Environment configuration..."
# cp .env.example .env
# Chỉnh sửa biến môi trường phù hợp với Public IP của EC2

echo "[5/5] Docker Compose Up..."
# docker compose up -d --build

echo "Bootstrap completed successfully!"
