variable "region" {
  type    = string
  default = "ap-south-1"
}

variable "project_name" {
  type    = string
  default = "sentiment-Analysis-MLOps"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "enable_single_natgateway" {
  type    = bool
  default = true
}

variable "minio_user" {
  type        = string
  description = "MinIO root user"
}

variable "minio_password" {
  type        = string
  description = "MinIO root password"
  sensitive   = true
}

variable "mlflow_uri" {
  type        = string
  description = "MLflow tracking URI"
}

variable "mlflow_user" {
  type        = string
  description = "MLflow username"
}

variable "mlflow_pass" {
  type        = string
  description = "MLflow password/token"
  sensitive   = true
}
