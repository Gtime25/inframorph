import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import subprocess
import tempfile
from pathlib import Path

class DriftDetector:
    def __init__(self):
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        
        # Initialize AWS clients
        if self.aws_access_key and self.aws_secret_key:
            self.ec2 = boto3.client('ec2', region_name=self.aws_region)
            self.s3 = boto3.client('s3', region_name=self.aws_region)
            self.rds = boto3.client('rds', region_name=self.aws_region)
            self.vpc = boto3.client('ec2', region_name=self.aws_region)
        else:
            self.ec2 = None
            self.s3 = None
            self.rds = None
            self.vpc = None
    
    async def detect_drift(
        self, 
        terraform_files: List[str], 
        cloud_provider: str = "aws"
    ) -> Dict[str, Any]:
        """
        Detect drift between Terraform code and deployed infrastructure
        
        Args:
            terraform_files: List of paths to Terraform files
            cloud_provider: Cloud provider (aws, azure, gcp)
            
        Returns:
            Dictionary containing drift analysis results
        """
        try:
            if cloud_provider == "aws":
                return await self._detect_aws_drift(terraform_files)
            elif cloud_provider == "azure":
                return await self._detect_azure_drift(terraform_files)
            elif cloud_provider == "gcp":
                return await self._detect_gcp_drift(terraform_files)
            else:
                raise ValueError(f"Unsupported cloud provider: {cloud_provider}")
                
        except Exception as e:
            return {
                "error": str(e),
                "drift_detected": False,
                "drift_summary": "Error during drift detection",
                "resources": [],
                "timestamp": datetime.now().isoformat()
            }
    
    async def _detect_aws_drift(self, terraform_files: List[str]) -> Dict[str, Any]:
        """Detect drift for AWS infrastructure"""
        if not self.ec2:
            return {
                "error": "AWS credentials not configured",
                "drift_detected": False,
                "drift_summary": "Cannot detect drift without AWS credentials",
                "resources": [],
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Parse Terraform files to extract resource definitions
            terraform_resources = await self._parse_terraform_resources(terraform_files)
            
            # Get actual AWS resources
            aws_resources = await self._get_aws_resources()
            
            # Compare and detect drift
            drift_results = await self._compare_resources(terraform_resources, aws_resources)
            
            return {
                "drift_detected": len(drift_results) > 0,
                "drift_summary": f"Found {len(drift_results)} resources with drift",
                "resources": drift_results,
                "total_resources": len(aws_resources),
                "drifted_resources": len(drift_results),
                "timestamp": datetime.now().isoformat(),
                "cloud_provider": "aws"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "drift_detected": False,
                "drift_summary": "Error during AWS drift detection",
                "resources": [],
                "timestamp": datetime.now().isoformat()
            }
    
    async def _parse_terraform_resources(self, terraform_files: List[str]) -> Dict[str, Any]:
        """Parse Terraform files to extract resource definitions"""
        resources = {
            "ec2_instances": [],
            "s3_buckets": [],
            "rds_instances": [],
            "vpc_resources": [],
            "security_groups": []
        }
        
        for file_path in terraform_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Simple parsing - in production, use proper Terraform parser
                if 'resource "aws_instance"' in content:
                    # Extract instance information
                    resources["ec2_instances"].append({
                        "file": file_path,
                        "type": "aws_instance",
                        "content": content
                    })
                
                if 'resource "aws_s3_bucket"' in content:
                    resources["s3_buckets"].append({
                        "file": file_path,
                        "type": "aws_s3_bucket",
                        "content": content
                    })
                
                if 'resource "aws_db_instance"' in content:
                    resources["rds_instances"].append({
                        "file": file_path,
                        "type": "aws_db_instance",
                        "content": content
                    })
                    
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        
        return resources
    
    async def _get_aws_resources(self) -> Dict[str, Any]:
        """Get actual AWS resources"""
        resources = {
            "ec2_instances": [],
            "s3_buckets": [],
            "rds_instances": [],
            "vpc_resources": [],
            "security_groups": []
        }
        
        try:
            # Get EC2 instances
            response = self.ec2.describe_instances()
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    resources["ec2_instances"].append({
                        "id": instance['InstanceId'],
                        "type": instance['InstanceType'],
                        "state": instance['State']['Name'],
                        "tags": instance.get('Tags', []),
                        "launch_time": instance['LaunchTime'].isoformat()
                    })
            
            # Get S3 buckets
            response = self.s3.list_buckets()
            for bucket in response['Buckets']:
                resources["s3_buckets"].append({
                    "name": bucket['Name'],
                    "creation_date": bucket['CreationDate'].isoformat()
                })
            
            # Get RDS instances
            response = self.rds.describe_db_instances()
            for instance in response['DBInstances']:
                resources["rds_instances"].append({
                    "id": instance['DBInstanceIdentifier'],
                    "engine": instance['Engine'],
                    "status": instance['DBInstanceStatus'],
                    "instance_class": instance['DBInstanceClass']
                })
            
            # Get Security Groups
            response = self.vpc.describe_security_groups()
            for sg in response['SecurityGroups']:
                resources["security_groups"].append({
                    "id": sg['GroupId'],
                    "name": sg['GroupName'],
                    "description": sg['Description'],
                    "vpc_id": sg['VpcId']
                })
                
        except Exception as e:
            print(f"Error getting AWS resources: {e}")
        
        return resources
    
    async def _compare_resources(
        self, 
        terraform_resources: Dict[str, Any], 
        aws_resources: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Compare Terraform resources with AWS resources"""
        drift_results = []
        
        # Compare EC2 instances
        terraform_instances = terraform_resources.get("ec2_instances", [])
        aws_instances = aws_resources.get("ec2_instances", [])
        
        # Find instances in AWS but not in Terraform (unmanaged)
        terraform_instance_ids = set()
        for tf_instance in terraform_instances:
            # Extract instance ID from Terraform content (simplified)
            if 'instance_type' in tf_instance['content']:
                terraform_instance_ids.add("managed_by_terraform")
        
        for aws_instance in aws_instances:
            if aws_instance['id'] not in terraform_instance_ids:
                drift_results.append({
                    "resource_type": "ec2_instance",
                    "resource_id": aws_instance['id'],
                    "drift_type": "unmanaged",
                    "description": f"EC2 instance {aws_instance['id']} exists in AWS but not managed by Terraform",
                    "severity": "medium",
                    "recommendation": "Add this instance to Terraform configuration or terminate it",
                    "aws_data": aws_instance
                })
        
        # Compare S3 buckets
        terraform_buckets = terraform_resources.get("s3_buckets", [])
        aws_buckets = aws_resources.get("s3_buckets", [])
        
        terraform_bucket_names = set()
        for tf_bucket in terraform_buckets:
            # Extract bucket name from Terraform content (simplified)
            if 'bucket' in tf_bucket['content']:
                terraform_bucket_names.add("managed_by_terraform")
        
        for aws_bucket in aws_buckets:
            if aws_bucket['name'] not in terraform_bucket_names:
                drift_results.append({
                    "resource_type": "s3_bucket",
                    "resource_id": aws_bucket['name'],
                    "drift_type": "unmanaged",
                    "description": f"S3 bucket {aws_bucket['name']} exists in AWS but not managed by Terraform",
                    "severity": "high",
                    "recommendation": "Add this bucket to Terraform configuration or delete it",
                    "aws_data": aws_bucket
                })
        
        return drift_results
    
    async def _detect_azure_drift(self, terraform_files: List[str]) -> Dict[str, Any]:
        """Detect drift for Azure infrastructure (placeholder)"""
        return {
            "drift_detected": False,
            "drift_summary": "Azure drift detection not yet implemented",
            "resources": [],
            "timestamp": datetime.now().isoformat(),
            "cloud_provider": "azure"
        }
    
    async def _detect_gcp_drift(self, terraform_files: List[str]) -> Dict[str, Any]:
        """Detect drift for GCP infrastructure (placeholder)"""
        return {
            "drift_detected": False,
            "drift_summary": "GCP drift detection not yet implemented",
            "resources": [],
            "timestamp": datetime.now().isoformat(),
            "cloud_provider": "gcp"
        }
    
    async def generate_drift_report(self, drift_results: Dict[str, Any]) -> str:
        """Generate a human-readable drift report"""
        if not drift_results.get("drift_detected", False):
            return "✅ No infrastructure drift detected. Your infrastructure matches your code."
        
        report = f"""# 🔍 Infrastructure Drift Report

## 📊 Summary
- **Drift Detected**: {drift_results.get("drift_detected", False)}
- **Total Resources**: {drift_results.get("total_resources", 0)}
- **Drifted Resources**: {drift_results.get("drifted_resources", 0)}
- **Cloud Provider**: {drift_results.get("cloud_provider", "Unknown")}
- **Timestamp**: {drift_results.get("timestamp", "Unknown")}

## 🚨 Drift Details

"""
        
        for resource in drift_results.get("resources", []):
            report += f"""### {resource.get("resource_type", "Unknown Resource")}
- **Resource ID**: {resource.get("resource_id", "Unknown")}
- **Drift Type**: {resource.get("drift_type", "Unknown")}
- **Severity**: {resource.get("severity", "Unknown")}
- **Description**: {resource.get("description", "No description")}
- **Recommendation**: {resource.get("recommendation", "No recommendation")}

"""
        
        report += """## 🛠️ Next Steps

1. **Review Drift**: Examine each drifted resource
2. **Decide Action**: Import to Terraform or remove from cloud
3. **Apply Changes**: Use `terraform import` or delete resources
4. **Verify**: Run drift detection again to confirm resolution

---
*Generated by InfraMorph Drift Detection*
"""
        
        return report 