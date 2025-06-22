import os
import asyncio
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from azure.mgmt.resource import ResourceManagementClient
from azure.identity import DefaultAzureCredential
from google.cloud import resourcemanager_v3
from google.cloud import storage
from google.auth import default

class CloudProvider(ABC):
    """Abstract base class for cloud providers"""
    
    @abstractmethod
    async def get_resources(self) -> Dict[str, Any]:
        """Get all resources from the cloud provider"""
        pass
    
    @abstractmethod
    async def get_resource_details(self, resource_id: str, resource_type: str) -> Dict[str, Any]:
        """Get detailed information about a specific resource"""
        pass
    
    @abstractmethod
    async def estimate_cost(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate cost for the given resources"""
        pass
    
    @abstractmethod
    async def check_compliance(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check compliance for the given resources"""
        pass

class AWSProvider(CloudProvider):
    """AWS cloud provider implementation"""
    
    def __init__(self):
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        
        if self.aws_access_key and self.aws_secret_key:
            self.ec2 = boto3.client('ec2', region_name=self.aws_region)
            self.s3 = boto3.client('s3', region_name=self.aws_region)
            self.rds = boto3.client('rds', region_name=self.aws_region)
            self.vpc = boto3.client('ec2', region_name=self.aws_region)
            self.iam = boto3.client('iam', region_name=self.aws_region)
            self.cloudwatch = boto3.client('cloudwatch', region_name=self.aws_region)
        else:
            self.ec2 = None
            self.s3 = None
            self.rds = None
            self.vpc = None
            self.iam = None
            self.cloudwatch = None
    
    async def get_resources(self) -> Dict[str, Any]:
        """Get all AWS resources"""
        if not self.ec2:
            return {"error": "AWS credentials not configured"}
        
        resources = {
            "ec2_instances": [],
            "s3_buckets": [],
            "rds_instances": [],
            "vpc_resources": [],
            "security_groups": [],
            "iam_roles": [],
            "load_balancers": []
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
                        "launch_time": instance['LaunchTime'].isoformat(),
                        "vpc_id": instance.get('VpcId'),
                        "subnet_id": instance.get('SubnetId')
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
                    "instance_class": instance['DBInstanceClass'],
                    "storage_type": instance.get('StorageType'),
                    "allocated_storage": instance.get('AllocatedStorage')
                })
            
            # Get Security Groups
            response = self.vpc.describe_security_groups()
            for sg in response['SecurityGroups']:
                resources["security_groups"].append({
                    "id": sg['GroupId'],
                    "name": sg['GroupName'],
                    "description": sg['Description'],
                    "vpc_id": sg['VpcId'],
                    "rules": sg.get('IpPermissions', [])
                })
                
        except Exception as e:
            resources["error"] = str(e)
        
        return resources
    
    async def get_resource_details(self, resource_id: str, resource_type: str) -> Dict[str, Any]:
        """Get detailed information about a specific AWS resource"""
        if not self.ec2:
            return {"error": "AWS credentials not configured"}
        
        try:
            if resource_type == "ec2_instance":
                response = self.ec2.describe_instances(InstanceIds=[resource_id])
                if response['Reservations']:
                    instance = response['Reservations'][0]['Instances'][0]
                    return {
                        "id": instance['InstanceId'],
                        "type": instance['InstanceType'],
                        "state": instance['State']['Name'],
                        "tags": instance.get('Tags', []),
                        "launch_time": instance['LaunchTime'].isoformat(),
                        "vpc_id": instance.get('VpcId'),
                        "subnet_id": instance.get('SubnetId'),
                        "public_ip": instance.get('PublicIpAddress'),
                        "private_ip": instance.get('PrivateIpAddress'),
                        "security_groups": instance.get('SecurityGroups', [])
                    }
            
            elif resource_type == "s3_bucket":
                try:
                    response = self.s3.head_bucket(Bucket=resource_id)
                    return {
                        "name": resource_id,
                        "status": "exists",
                        "region": response.get('ResponseMetadata', {}).get('HTTPHeaders', {}).get('x-amz-bucket-region')
                    }
                except ClientError as e:
                    return {"error": f"Bucket {resource_id} not found or access denied"}
            
            elif resource_type == "rds_instance":
                response = self.rds.describe_db_instances(DBInstanceIdentifier=resource_id)
                if response['DBInstances']:
                    instance = response['DBInstances'][0]
                    return {
                        "id": instance['DBInstanceIdentifier'],
                        "engine": instance['Engine'],
                        "status": instance['DBInstanceStatus'],
                        "instance_class": instance['DBInstanceClass'],
                        "storage_type": instance.get('StorageType'),
                        "allocated_storage": instance.get('AllocatedStorage'),
                        "endpoint": instance.get('Endpoint'),
                        "port": instance.get('DbInstancePort')
                    }
                    
        except Exception as e:
            return {"error": str(e)}
        
        return {"error": f"Resource type {resource_type} not supported"}
    
    async def estimate_cost(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate AWS cost for the given resources"""
        # This is a simplified cost estimation
        # In production, you would use AWS Cost Explorer API
        total_cost = 0
        cost_breakdown = {}
        
        for resource in resources:
            resource_type = resource.get('type', '')
            if 'aws_instance' in resource_type:
                # Simplified EC2 cost estimation
                instance_type = resource.get('instance_type', 't3.micro')
                cost_per_hour = {
                    't3.micro': 0.0104,
                    't3.small': 0.0208,
                    't3.medium': 0.0416,
                    'm5.large': 0.096,
                    'c5.large': 0.085
                }.get(instance_type, 0.0104)
                
                monthly_cost = cost_per_hour * 24 * 30
                cost_breakdown[resource.get('name', 'EC2 Instance')] = monthly_cost
                total_cost += monthly_cost
            
            elif 'aws_s3_bucket' in resource_type:
                # Simplified S3 cost estimation
                storage_gb = resource.get('storage_gb', 1)
                monthly_cost = storage_gb * 0.023  # Standard storage cost per GB
                cost_breakdown[resource.get('name', 'S3 Bucket')] = monthly_cost
                total_cost += monthly_cost
            
            elif 'aws_db_instance' in resource_type:
                # Simplified RDS cost estimation
                instance_class = resource.get('instance_class', 'db.t3.micro')
                cost_per_hour = {
                    'db.t3.micro': 0.017,
                    'db.t3.small': 0.034,
                    'db.t3.medium': 0.068,
                    'db.r5.large': 0.29
                }.get(instance_class, 0.017)
                
                monthly_cost = cost_per_hour * 24 * 30
                cost_breakdown[resource.get('name', 'RDS Instance')] = monthly_cost
                total_cost += monthly_cost
        
        return {
            "total_monthly_cost": round(total_cost, 2),
            "currency": "USD",
            "cost_breakdown": cost_breakdown,
            "provider": "aws"
        }
    
    async def check_compliance(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check AWS compliance for the given resources"""
        compliance_results = {
            "overall_compliant": True,
            "issues": [],
            "recommendations": []
        }
        
        for resource in resources:
            resource_type = resource.get('type', '')
            
            # Check for security group compliance
            if 'aws_security_group' in resource_type:
                rules = resource.get('rules', [])
                for rule in rules:
                    if rule.get('IpProtocol') == '-1' and '0.0.0.0/0' in str(rule.get('IpRanges', [])):
                        compliance_results["overall_compliant"] = False
                        compliance_results["issues"].append({
                            "resource": resource.get('name', 'Security Group'),
                            "issue": "Security group allows all traffic (0.0.0.0/0)",
                            "severity": "high"
                        })
                        compliance_results["recommendations"].append({
                            "resource": resource.get('name', 'Security Group'),
                            "recommendation": "Restrict security group rules to specific IP ranges"
                        })
            
            # Check for S3 bucket compliance
            elif 'aws_s3_bucket' in resource_type:
                if not resource.get('encryption', False):
                    compliance_results["overall_compliant"] = False
                    compliance_results["issues"].append({
                        "resource": resource.get('name', 'S3 Bucket'),
                        "issue": "S3 bucket encryption not enabled",
                        "severity": "medium"
                    })
                    compliance_results["recommendations"].append({
                        "resource": resource.get('name', 'S3 Bucket'),
                        "recommendation": "Enable server-side encryption for S3 bucket"
                    })
        
        return compliance_results

class AzureProvider(CloudProvider):
    """Azure cloud provider implementation"""
    
    def __init__(self):
        self.subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        self.credential = DefaultAzureCredential()
        
        if self.subscription_id:
            self.resource_client = ResourceManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
        else:
            self.resource_client = None
    
    async def get_resources(self) -> Dict[str, Any]:
        """Get all Azure resources"""
        if not self.resource_client:
            return {"error": "Azure credentials not configured"}
        
        resources = {
            "virtual_machines": [],
            "storage_accounts": [],
            "sql_databases": [],
            "virtual_networks": [],
            "network_security_groups": []
        }
        
        try:
            # Get all resources
            resource_list = self.resource_client.resources.list()
            
            for resource in resource_list:
                resource_type = resource.type.lower()
                
                if 'microsoft.compute/virtualmachines' in resource_type:
                    resources["virtual_machines"].append({
                        "id": resource.id,
                        "name": resource.name,
                        "location": resource.location,
                        "type": resource.type
                    })
                
                elif 'microsoft.storage/storageaccounts' in resource_type:
                    resources["storage_accounts"].append({
                        "id": resource.id,
                        "name": resource.name,
                        "location": resource.location,
                        "type": resource.type
                    })
                
                elif 'microsoft.sql/servers' in resource_type:
                    resources["sql_databases"].append({
                        "id": resource.id,
                        "name": resource.name,
                        "location": resource.location,
                        "type": resource.type
                    })
                    
        except Exception as e:
            resources["error"] = str(e)
        
        return resources
    
    async def get_resource_details(self, resource_id: str, resource_type: str) -> Dict[str, Any]:
        """Get detailed information about a specific Azure resource"""
        if not self.resource_client:
            return {"error": "Azure credentials not configured"}
        
        try:
            # Parse resource ID to get resource group and resource name
            parts = resource_id.split('/')
            if len(parts) >= 4:
                resource_group = parts[4]
                resource_name = parts[-1]
                
                resource = self.resource_client.resources.get(
                    resource_group_name=resource_group,
                    resource_provider_namespace=parts[6],
                    parent_resource_path="",
                    resource_type=parts[7],
                    resource_name=resource_name
                )
                
                return {
                    "id": resource.id,
                    "name": resource.name,
                    "location": resource.location,
                    "type": resource.type,
                    "tags": resource.tags or {}
                }
                
        except Exception as e:
            return {"error": str(e)}
        
        return {"error": f"Resource type {resource_type} not supported"}
    
    async def estimate_cost(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate Azure cost for the given resources"""
        # Simplified Azure cost estimation
        total_cost = 0
        cost_breakdown = {}
        
        for resource in resources:
            resource_type = resource.get('type', '')
            if 'microsoft.compute/virtualmachines' in resource_type:
                # Simplified VM cost estimation
                vm_size = resource.get('vm_size', 'Standard_B1s')
                cost_per_hour = {
                    'Standard_B1s': 0.0104,
                    'Standard_B2s': 0.0416,
                    'Standard_D2s_v3': 0.096,
                    'Standard_E2s_v3': 0.126
                }.get(vm_size, 0.0104)
                
                monthly_cost = cost_per_hour * 24 * 30
                cost_breakdown[resource.get('name', 'Virtual Machine')] = monthly_cost
                total_cost += monthly_cost
        
        return {
            "total_monthly_cost": round(total_cost, 2),
            "currency": "USD",
            "cost_breakdown": cost_breakdown,
            "provider": "azure"
        }
    
    async def check_compliance(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check Azure compliance for the given resources"""
        compliance_results = {
            "overall_compliant": True,
            "issues": [],
            "recommendations": []
        }
        
        # Simplified Azure compliance checks
        for resource in resources:
            resource_type = resource.get('type', '')
            
            if 'microsoft.storage/storageaccounts' in resource_type:
                if not resource.get('encryption', False):
                    compliance_results["overall_compliant"] = False
                    compliance_results["issues"].append({
                        "resource": resource.get('name', 'Storage Account'),
                        "issue": "Storage account encryption not enabled",
                        "severity": "medium"
                    })
        
        return compliance_results

class GCPProvider(CloudProvider):
    """Google Cloud Platform provider implementation"""
    
    def __init__(self):
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        
        if self.project_id:
            try:
                self.resource_client = resourcemanager_v3.ProjectsClient()
                self.storage_client = storage.Client()
            except Exception:
                self.resource_client = None
                self.storage_client = None
        else:
            self.resource_client = None
            self.storage_client = None
    
    async def get_resources(self) -> Dict[str, Any]:
        """Get all GCP resources"""
        if not self.resource_client:
            return {"error": "GCP credentials not configured"}
        
        resources = {
            "compute_instances": [],
            "storage_buckets": [],
            "sql_instances": [],
            "networks": []
        }
        
        try:
            # Get storage buckets
            if self.storage_client:
                buckets = self.storage_client.list_buckets()
                for bucket in buckets:
                    resources["storage_buckets"].append({
                        "name": bucket.name,
                        "location": bucket.location,
                        "storage_class": bucket.storage_class
                    })
                    
        except Exception as e:
            resources["error"] = str(e)
        
        return resources
    
    async def get_resource_details(self, resource_id: str, resource_type: str) -> Dict[str, Any]:
        """Get detailed information about a specific GCP resource"""
        if not self.resource_client:
            return {"error": "GCP credentials not configured"}
        
        try:
            if resource_type == "storage_bucket" and self.storage_client:
                bucket = self.storage_client.get_bucket(resource_id)
                return {
                    "name": bucket.name,
                    "location": bucket.location,
                    "storage_class": bucket.storage_class,
                    "created": bucket.time_created.isoformat() if bucket.time_created else None
                }
                
        except Exception as e:
            return {"error": str(e)}
        
        return {"error": f"Resource type {resource_type} not supported"}
    
    async def estimate_cost(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate GCP cost for the given resources"""
        # Simplified GCP cost estimation
        total_cost = 0
        cost_breakdown = {}
        
        for resource in resources:
            resource_type = resource.get('type', '')
            if 'google_compute_instance' in resource_type:
                # Simplified Compute Engine cost estimation
                machine_type = resource.get('machine_type', 'e2-micro')
                cost_per_hour = {
                    'e2-micro': 0.008,
                    'e2-small': 0.016,
                    'e2-medium': 0.032,
                    'n1-standard-1': 0.0475
                }.get(machine_type, 0.008)
                
                monthly_cost = cost_per_hour * 24 * 30
                cost_breakdown[resource.get('name', 'Compute Instance')] = monthly_cost
                total_cost += monthly_cost
        
        return {
            "total_monthly_cost": round(total_cost, 2),
            "currency": "USD",
            "cost_breakdown": cost_breakdown,
            "provider": "gcp"
        }
    
    async def check_compliance(self, resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check GCP compliance for the given resources"""
        compliance_results = {
            "overall_compliant": True,
            "issues": [],
            "recommendations": []
        }
        
        # Simplified GCP compliance checks
        for resource in resources:
            resource_type = resource.get('type', '')
            
            if 'google_storage_bucket' in resource_type:
                if not resource.get('encryption', False):
                    compliance_results["overall_compliant"] = False
                    compliance_results["issues"].append({
                        "resource": resource.get('name', 'Storage Bucket'),
                        "issue": "Storage bucket encryption not enabled",
                        "severity": "medium"
                    })
        
        return compliance_results

class CloudProviderFactory:
    """Factory class to create cloud provider instances"""
    
    @staticmethod
    def create_provider(provider_type: str) -> CloudProvider:
        """Create a cloud provider instance based on type"""
        if provider_type.lower() == "aws":
            return AWSProvider()
        elif provider_type.lower() == "azure":
            return AzureProvider()
        elif provider_type.lower() == "gcp":
            return GCPProvider()
        else:
            raise ValueError(f"Unsupported cloud provider: {provider_type}")
    
    @staticmethod
    async def get_multi_cloud_resources(providers: List[str]) -> Dict[str, Any]:
        """Get resources from multiple cloud providers"""
        results = {}
        
        for provider_type in providers:
            try:
                provider = CloudProviderFactory.create_provider(provider_type)
                resources = await provider.get_resources()
                results[provider_type] = resources
            except Exception as e:
                results[provider_type] = {"error": str(e)}
        
        return results 