# ── Required (no defaults — user must provide) ──────────────────

variable "key_pair_name" {
  description = "Name of an existing EC2 key pair for SSH access"
  type        = string
}

variable "repo_url" {
  description = "Git repository URL to clone on the EC2 instance"
  type        = string
}

# ── Domain & DNS ─────────────────────────────────────────────────

variable "domain_name" {
  description = "Full domain name for the app (e.g. interview.4pass.io)"
  type        = string
  default     = "interview.4pass.io"
}

variable "hosted_zone_name" {
  description = "Route 53 hosted zone name (e.g. 4pass.io). Must already exist in your AWS account."
  type        = string
  default     = "4pass.io"
}

variable "admin_email" {
  description = "Email for Let's Encrypt SSL certificate registration"
  type        = string
  default     = "admin@4pass.io"
}

# ── Compute ──────────────────────────────────────────────────────

variable "aws_region" {
  description = "AWS region to deploy to"
  type        = string
  default     = "ap-southeast-1"
}

variable "instance_type" {
  description = "EC2 instance type (t3.medium=2vCPU/4GB, t3.large=2vCPU/8GB, t3.xlarge=4vCPU/16GB)"
  type        = string
  default     = "t3.large"
}

variable "volume_size" {
  description = "Root EBS volume size in GB (30GB recommended for DB + Docker images)"
  type        = number
  default     = 30
}

# ── Secrets ──────────────────────────────────────────────────────

variable "openai_api_key" {
  description = "OpenAI API key for the voice AI agent. Stored in Secrets Manager."
  type        = string
  sensitive   = true
  default     = ""
}

# ── Network ──────────────────────────────────────────────────────

variable "allowed_ssh_cidr" {
  description = "CIDR block allowed to SSH (e.g. 1.2.3.4/32 or 0.0.0.0/0 for any)"
  type        = string
  default     = "0.0.0.0/0"
}

variable "vpc_id" {
  description = "VPC ID to deploy into. Leave empty to use the default VPC."
  type        = string
  default     = ""
}

variable "subnet_id" {
  description = "Subnet ID to deploy into. Leave empty to auto-select the first public subnet."
  type        = string
  default     = ""
}
