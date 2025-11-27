#!/bin/bash

set -euo pipefail

# Update all packages
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Git, Docker and AWS CLI
sudo apt-get install -y git
sudo apt-get install docker.io awscli docker-compose-plugin -y

systemctl enable docker
systemctl start docker

# Cloning the code
sudo git clone https://github.com/dakshsawhneyy/Sentiment-Analysis-MLOps-Pipeline.git /opt/MLOps
cd /opt/MLOps


# Write environment variables
cat <<EOF >> /opt/MLOps/.env
MINIO_ROOT_USER=${minio_user}
MINIO_ROOT_PASSWORD=${minio_password}
MLFLOW_TRACKING_URI=${mlflow_uri}
MLFLOW_TRACKING_USERNAME=${mlflow_user}
MLFLOW_TRACKING_PASSWORD=${mlflow_pass}
EOF

# Run Docker Compose 
docker compose -f docker-compose.yml up -d