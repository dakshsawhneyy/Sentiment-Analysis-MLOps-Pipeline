output "load_balancer_ip" {
  description = "The public URL for the application load balancer."
  value = "https://${aws_lb.my_lb.dns_name}"
}

output "autoscaling_group_name" {
  description = "The name of the Auto Scaling Group."
  value       = aws_autoscaling_group.my_asg.name
}