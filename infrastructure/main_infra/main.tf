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
# EC2 - Auto Scaling CONFIGURATION
# =============================================================================

# EC2 launch template. Gonna place this under autoscaling group
resource "aws_launch_template" "my_launch_template" {
  name_prefix = "mlops-pipeline-ec2-"     # generate a unique name everytime
  image_id = data.aws_ami.ubuntu.id
  instance_type = "t2.micro"
  key_name      = "general-key-pair" 
  vpc_security_group_ids = [aws_security_group.my_sg.id]

  user_data = base64encode(
    templatefile("${path.module}/user-data.sh", {
      minio_user = var.minio_user,
      minio_password = var.minio_password
      mlflow_uri     = var.mlflow_uri
      mlflow_user    = var.mlflow_user
      mlflow_pass    = var.mlflow_pass
    })
  )

  tags = local.common_tags
}

resource "aws_autoscaling_group" "my_asg" {
  name = "mlops-pipeline-asg-"
  min_size = 2
  max_size = 4
  desired_capacity    = 2
  vpc_zone_identifier = module.vpc.public_subnets

  launch_template {
    id = aws_launch_template.my_launch_template.id
    version = "$Latest"
  }

  # This links the ASG to the Load Balancer's Target Group -- required for instances health checks
  target_group_arns = [aws_lb_target_group.my_tg.arn]

  # This helps the ASG replace unhealthy instances
  health_check_type = "ELB"   # Let load balancer check instance health
  health_check_grace_period = 300
}