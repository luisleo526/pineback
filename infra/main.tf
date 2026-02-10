terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ── AMI: latest Amazon Linux 2023 (auto-resolved per region) ─────

data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# ── VPC: default or user-specified ───────────────────────────────

data "aws_vpc" "selected" {
  id      = var.vpc_id != "" ? var.vpc_id : null
  default = var.vpc_id == "" ? true : null
}

data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.selected.id]
  }
}

# ── Security Group ───────────────────────────────────────────────

resource "aws_security_group" "backtest" {
  name_prefix = "pineback-${local.slug}-"
  description = "PineBack ${local.slug}: HTTP, HTTPS, SSH"
  vpc_id      = data.aws_vpc.selected.id

  # HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP"
  }

  # HTTPS
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_ssh_cidr]
    description = "SSH"
  }

  # All outbound
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "backtest-sg"
  }
}

# ── Naming: derive a unique prefix from the domain ───────────────
# e.g. "interview.4pass.io" -> "interview", "interview-v2.4pass.io" -> "interview-v2"

locals {
  slug = split(".", var.domain_name)[0]  # subdomain part
}

# ── Secrets Manager: OpenAI API key ──────────────────────────────

resource "aws_secretsmanager_secret" "openai" {
  name        = "pineback/${local.slug}/openai-api-key"
  description = "OpenAI API key for PineBack (${var.domain_name})"

  tags = {
    Name = "pineback-${local.slug}-openai-key"
  }
}

resource "aws_secretsmanager_secret_version" "openai" {
  secret_id     = aws_secretsmanager_secret.openai.id
  secret_string = jsonencode({ OPENAI_API_KEY = var.openai_api_key })
}

# ── IAM: EC2 role with Secrets Manager read access ──────────────

resource "aws_iam_role" "backtest" {
  name = "pineback-${local.slug}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })

  tags = {
    Name = "pineback-${local.slug}-ec2-role"
  }
}

resource "aws_iam_role_policy" "secrets_read" {
  name = "pineback-${local.slug}-secrets-read"
  role = aws_iam_role.backtest.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "secretsmanager:GetSecretValue"
      Resource = aws_secretsmanager_secret.openai.arn
    }]
  })
}

resource "aws_iam_instance_profile" "backtest" {
  name = "pineback-${local.slug}-ec2-profile"
  role = aws_iam_role.backtest.name
}

# ── EC2 Instance ─────────────────────────────────────────────────

resource "aws_instance" "backtest" {
  ami                    = data.aws_ami.al2023.id
  instance_type          = var.instance_type
  key_name               = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.backtest.id]
  subnet_id              = var.subnet_id != "" ? var.subnet_id : data.aws_subnets.public.ids[0]
  iam_instance_profile   = aws_iam_instance_profile.backtest.name

  root_block_device {
    volume_size = var.volume_size
    volume_type = "gp3"
  }

  user_data = templatefile("${path.module}/user_data.sh.tpl", {
    repo_url          = var.repo_url
    domain_name       = var.domain_name
    admin_email       = var.admin_email
    aws_region        = var.aws_region
    openai_secret_name = aws_secretsmanager_secret.openai.name
  })

  tags = {
    Name = "pineback-${local.slug}"
  }
}

# ── Elastic IP (stable public address) ──────────────────────────

resource "aws_eip" "backtest" {
  instance = aws_instance.backtest.id
  domain   = "vpc"

  tags = {
    Name = "pineback-${local.slug}-eip"
  }
}

# ── Route 53 DNS Record ─────────────────────────────────────────

data "aws_route53_zone" "hosted" {
  name = var.hosted_zone_name
}

resource "aws_route53_record" "app" {
  zone_id = data.aws_route53_zone.hosted.zone_id
  name    = var.domain_name
  type    = "A"
  ttl     = 300
  records = [aws_eip.backtest.public_ip]
}
