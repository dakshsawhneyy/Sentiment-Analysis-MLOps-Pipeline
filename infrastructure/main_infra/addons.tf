# =============================================================================
# Load Balancer CONFIGURATION
# =============================================================================
resource "aws_lb" "my_lb" {
  name = "${var.project_name}-lb"
  internal = false    # LB is internet-facing
  load_balancer_type = "application"
  security_groups = [aws_security_group.my_sg.id]
  subnets = module.vpc.public_subnets

  tags = local.common_tags
}

# Target Group [Where to send the data]
resource "aws_lb_target_group" "my_tg" {
  name = "${var.project_name}-tg"
  port = 8000   # FastAPI server running on 8000
  protocol = "HTTP"
  vpc_id = module.vpc.vpc_id

  health_check {
    path = "/healthy"     # /healthy route is created in service A
  }

  tags = local.common_tags
}

# Listeners [When and how to send the load]
resource "aws_lb_listener" "my_listener" {
  load_balancer_arn = aws_lb.my_lb.arn
  port = "80"
  protocol = "HTTP"

  # Specifies what to do with the request
  default_action {
    type = "forward"    # forwards the request
    target_group_arn = aws_lb_target_group.my_tg.arn   # forwards to the target groups
  }
}