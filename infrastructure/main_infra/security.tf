resource "aws_security_group" "my_sg" {
  name = "${var.project_name}-my_sg"
  description = "Allows SSH and HTTP traffic"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]    
  } 
  ingress {
    from_port   = 80
    to_port     =  80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # This is the universal code for "anywhere"
  }
  ingress {
    from_port   = 443
    to_port     =  443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # This is the universal code for "anywhere"
  }
  ingress {
    from_port   = 9090
    to_port     =  9090
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # This is the universal code for "anywhere"
  }
  ingress {
    from_port   = 3000
    to_port     =  3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # This is the universal code for "anywhere"
  }
  ingress {
    from_port   = 8000
    to_port     =  8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # This is the universal code for "anywhere"
  }
  ingress {
    from_port   = 9000
    to_port     =  9000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # This is the universal code for "anywhere"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"          # -1 = all protocols
    cidr_blocks = ["0.0.0.0/0"] # anywhere
  }

  tags = local.common_tags
}