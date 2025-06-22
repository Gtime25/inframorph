# Demo AWS Infrastructure with Security and Cost Issues
# This file is intentionally created with issues for testing InfraMorph

# VPC Configuration
resource "aws_vpc" "demo_vpc" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = "demo-vpc"
    Environment = "demo"
  }
}

# Security Group with Critical Security Issues
resource "aws_security_group" "demo_sg" {
  name        = "demo-security-group"
  description = "Demo security group with security issues"
  vpc_id      = aws_vpc.demo_vpc.id

  # CRITICAL: Open to all traffic
  ingress {
    description = "SSH from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # SECURITY ISSUE: Open to all IPs
  }

  # CRITICAL: Open to all traffic
  ingress {
    description = "HTTP from anywhere"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # SECURITY ISSUE: Open to all IPs
  }

  # CRITICAL: Open to all traffic
  ingress {
    description = "HTTPS from anywhere"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # SECURITY ISSUE: Open to all IPs
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "demo-security-group"
  }
}

# EC2 Instance with Cost Issues
resource "aws_instance" "demo_instance" {
  ami           = "ami-0c55b159cbfafe1f0"  # COST ISSUE: Using expensive instance type
  instance_type = "m5.xlarge"              # COST ISSUE: Over-provisioned for demo
  
  vpc_security_group_ids = [aws_security_group.demo_sg.id]
  subnet_id              = aws_subnet.demo_subnet.id

  # SECURITY ISSUE: No encryption specified
  root_block_device {
    volume_size = 100  # COST ISSUE: Large volume for demo
    volume_type = "gp2"
    # encryption = true  # SECURITY ISSUE: Encryption disabled
  }

  tags = {
    Name = "demo-instance"
    Environment = "demo"
  }
}

# S3 Bucket with Security Issues
resource "aws_s3_bucket" "demo_bucket" {
  bucket = "demo-bucket-12345"  # NAMING ISSUE: Generic name

  tags = {
    Name = "demo-bucket"
  }
}

# SECURITY ISSUE: Public access enabled
resource "aws_s3_bucket_public_access_block" "demo_bucket_public" {
  bucket = aws_s3_bucket.demo_bucket.id

  block_public_acls   = false  # SECURITY ISSUE: Public ACLs allowed
  block_public_policy = false  # SECURITY ISSUE: Public policies allowed
  ignore_public_acls  = false  # SECURITY ISSUE: Public ACLs not ignored
  restrict_public_buckets = false  # SECURITY ISSUE: Public access not restricted
}

# RDS Instance with Security Issues
resource "aws_db_instance" "demo_db" {
  identifier = "demo-db"
  
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"
  
  allocated_storage     = 20
  storage_type         = "gp2"
  storage_encrypted    = false  # SECURITY ISSUE: Encryption disabled
  
  db_name  = "demodb"
  username = "admin"
  password = "password123"  # SECURITY ISSUE: Hardcoded password
  
  publicly_accessible = true  # SECURITY ISSUE: Publicly accessible
  
  skip_final_snapshot = true  # SECURITY ISSUE: No backup
  
  tags = {
    Name = "demo-database"
  }
}

# IAM Role with Excessive Permissions
resource "aws_iam_role" "demo_role" {
  name = "demo-role"

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

# SECURITY ISSUE: Excessive permissions
resource "aws_iam_role_policy" "demo_policy" {
  name = "demo-policy"
  role = aws_iam_role.demo_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "*"  # SECURITY ISSUE: Wildcard permissions
        Resource = "*"  # SECURITY ISSUE: All resources
      }
    ]
  })
}

# Subnet Configuration
resource "aws_subnet" "demo_subnet" {
  vpc_id     = aws_vpc.demo_vpc.id
  cidr_block = "10.0.1.0/24"

  tags = {
    Name = "demo-subnet"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "demo_igw" {
  vpc_id = aws_vpc.demo_vpc.id

  tags = {
    Name = "demo-igw"
  }
}

# Route Table
resource "aws_route_table" "demo_rt" {
  vpc_id = aws_vpc.demo_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.demo_igw.id
  }

  tags = {
    Name = "demo-route-table"
  }
}

# Route Table Association
resource "aws_route_table_association" "demo_rta" {
  subnet_id      = aws_subnet.demo_subnet.id
  route_table_id = aws_route_table.demo_rt.id
} 