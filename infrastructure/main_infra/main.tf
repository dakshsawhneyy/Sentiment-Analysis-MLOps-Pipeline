############################
# VPC
############################
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project_name}-vpc"
  cidr = var.vpc_cidr

  azs             = local.azs
  public_subnets  = local.public_subnets
  private_subnets = local.private_subnets

  enable_nat_gateway = true
  single_nat_gateway = var.enable_single_natgateway

  create_igw = true

  map_public_ip_on_launch = true

  tags = local.common_tags
}

# =============================================================================
# EC2 CONFIGURATION
# =============================================================================
module "ec2_instance" {
  source  = "terraform-aws-modules/ec2-instance/aws"

  name = "${var.project_name}-ec2"

  ami = data.aws_ami.ubuntu.id
  instance_type = "t2.medium"
  key_name      = "general-key-pair"
  subnet_id     = module.vpc.public_subnets[0]

  # Attach web security group to ssh into web_server
  vpc_security_group_ids = [aws_security_group.my_sg.id]

  # Converting into tpl file, so we can pass env while calling the file
  user_data = templatefile("${path.module}/user-data.sh.tpl", {
    minio_user = var.minio_user,
    minio_password = var.minio_password
    mlflow_uri     = var.mlflow_uri
    mlflow_user    = var.mlflow_user
    mlflow_pass    = var.mlflow_pass
  })

  tags = local.common_tags
}