#!/bin/bash

# 停止现有容器
docker-compose down

# 拉取最新代码
git pull

# 构建并启动容器
docker-compose up -d --build

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 检查服务状态
docker-compose ps

# 显示日志
docker-compose logs -f 