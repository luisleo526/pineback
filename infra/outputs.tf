output "public_ip" {
  description = "Elastic IP address of the EC2 instance"
  value       = aws_eip.backtest.public_ip
}

output "app_url" {
  description = "Application URL"
  value       = "https://${var.domain_name}"
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ~/.ssh/${var.key_pair_name}.pem ec2-user@${aws_eip.backtest.public_ip}"
}

output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.backtest.id
}
