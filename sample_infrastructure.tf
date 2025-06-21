# Sample Infrastructure for InfraMorph Testing
# This file contains various resources with potential issues for analysis

# Provider configuration
provider "aws" {
  region = "us-west-2"
}

# Variables
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

variable "project" {
  description = "Project name"
  type        = string
  default     = "myapp"
}

# VPC Configuration
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "main-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "main-igw"
  }
}

# Public Subnet
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-west-2a"
  map_public_ip_on_launch = true

  tags = {
    Name = "public-subnet"
  }
}

# Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "public-rt"
  }
}

# Route Table Association
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# Security Group - Missing proper rules
resource "aws_security_group" "web" {
  name        = "web-sg"
  description = "Security group for web servers"
  vpc_id      = aws_vpc.main.id

  # This is too permissive - security issue
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "web-sg"
  }
}

# EC2 Instance - Oversized for cost optimization demo
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.xlarge"  # Oversized - could be t3.medium
  subnet_id     = aws_subnet.public.id

  vpc_security_group_ids = [aws_security_group.web.id]

  # Missing user data for proper configuration
  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y httpd
              systemctl start httpd
              systemctl enable httpd
              EOF

  tags = {
    Name = "web-server"
  }
}

# S3 Bucket - Missing encryption
resource "aws_s3_bucket" "data" {
  bucket = "myapp-data-bucket-12345"

  tags = {
    Name = "data-bucket"
  }
}

# S3 Bucket Public Access Block
resource "aws_s3_bucket_public_access_block" "data" {
  bucket = aws_s3_bucket.data.id

  block_public_acls       = false  # Security issue - should be true
  block_public_policy     = false  # Security issue - should be true
  ignore_public_acls      = false  # Security issue - should be true
  restrict_public_buckets = false  # Security issue - should be true
}

# RDS Instance - Missing encryption
resource "aws_db_instance" "database" {
  identifier        = "myapp-db"
  engine            = "mysql"
  engine_version    = "8.0"
  instance_class    = "db.t3.large"  # Could be optimized
  allocated_storage = 20
  storage_type      = "gp2"

  db_name  = "myapp"
  username = "admin"
  password = "password123"  # Security issue - should use secrets manager

  skip_final_snapshot = true

  tags = {
    Name = "myapp-database"
  }
}

# IAM Role - Overly permissive
resource "aws_iam_role" "ec2_role" {
  name = "ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy - Too permissive
resource "aws_iam_policy" "ec2_policy" {
  name        = "ec2-policy"
  description = "Policy for EC2 instances"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "*"  # Security issue - too permissive
        Resource = "*"
      }
    ]
  })
}

# IAM Role Policy Attachment
resource "aws_iam_role_policy_attachment" "ec2_policy_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.ec2_policy.arn
}

# CloudWatch Log Group - Missing retention
resource "aws_cloudwatch_log_group" "app_logs" {
  name = "/aws/ec2/myapp"

  tags = {
    Name = "app-logs"
  }
}

# Outputs
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_id" {
  description = "Public Subnet ID"
  value       = aws_subnet.public.id
}

output "web_instance_id" {
  description = "Web Instance ID"
  value       = aws_instance.web.id
}

output "database_endpoint" {
  description = "Database endpoint"
  value       = aws_db_instance.database.endpoint
} 