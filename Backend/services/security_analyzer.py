import re
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
from pathlib import Path
import os

class SecurityAnalyzer:
    """Advanced security analyzer for infrastructure code"""
    
    def __init__(self):
        # Check if OpenAI API key is available
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            openai.api_key = openai_api_key
            self.ai_enabled = True
        else:
            self.ai_enabled = False
            print("Warning: OPENAI_API_KEY not found. AI-powered analysis will be disabled.")
        
        # Security patterns and rules
        self.security_patterns = {
            "aws": {
                "security_group_open": r'cidr_blocks\s*=\s*\[["\']0\.0\.0\.0/0["\']\]',
                "s3_public_access": r'force_destroy\s*=\s*true',
                "rds_publicly_accessible": r'publicly_accessible\s*=\s*true',
                "iam_policy_wildcard": r'"Resource":\s*"\\*"',
                "encryption_disabled": r'encryption\s*=\s*false',
                "ssl_disabled": r'storage_encrypted\s*=\s*false'
            },
            "azure": {
                "nsg_open": r'source_address_prefix\s*=\s*"\\*"',
                "storage_public": r'allow_blob_public_access\s*=\s*true',
                "sql_public": r'public_network_access_enabled\s*=\s*true'
            },
            "gcp": {
                "firewall_open": r'source_ranges\s*=\s*\[["\']0\.0\.0\.0/0["\']\]',
                "bucket_public": r'uniform_bucket_level_access\s*=\s*false',
                "sql_public": r'ip_configuration\s*{\s*ipv4_enabled\s*=\s*true'
            }
        }
        
        # Compliance frameworks
        self.compliance_frameworks = {
            "cis": {
                "name": "CIS Benchmarks",
                "rules": [
                    "Ensure no security groups allow ingress from 0.0.0.0/0 to port 22",
                    "Ensure no security groups allow ingress from 0.0.0.0/0 to port 3389",
                    "Ensure S3 buckets are not publicly accessible",
                    "Ensure RDS instances are not publicly accessible",
                    "Ensure IAM policies do not allow full administrative privileges"
                ]
            },
            "pci": {
                "name": "PCI DSS",
                "rules": [
                    "Ensure encryption in transit",
                    "Ensure encryption at rest",
                    "Ensure access controls are implemented",
                    "Ensure audit logging is enabled",
                    "Ensure vulnerability management is in place"
                ]
            },
            "hipaa": {
                "name": "HIPAA",
                "rules": [
                    "Ensure PHI is encrypted at rest",
                    "Ensure PHI is encrypted in transit",
                    "Ensure access controls are implemented",
                    "Ensure audit trails are maintained",
                    "Ensure backup and recovery procedures"
                ]
            }
        }
    
    async def analyze_security(
        self, 
        files: List[str], 
        cloud_provider: str = "aws",
        compliance_frameworks: List[str] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive security analysis
        
        Args:
            files: List of file paths to analyze
            cloud_provider: Cloud provider (aws, azure, gcp)
            compliance_frameworks: List of compliance frameworks to check
            
        Returns:
            Dictionary containing security analysis results
        """
        try:
            # Initialize results
            results = {
                "overall_security_score": 100,
                "critical_issues": [],
                "high_issues": [],
                "medium_issues": [],
                "low_issues": [],
                "compliance_results": {},
                "recommendations": [],
                "timestamp": datetime.now().isoformat(),
                "cloud_provider": cloud_provider
            }
            
            # Pattern-based analysis
            pattern_results = await self._pattern_analysis(files, cloud_provider)
            results.update(pattern_results)
            
            # AI-powered analysis
            ai_results = await self._ai_security_analysis(files, cloud_provider)
            results.update(ai_results)
            
            # Add note if AI is disabled
            if ai_results.get("ai_disabled"):
                results["ai_note"] = "AI-powered analysis is disabled. Only pattern-based analysis is available."
            
            # Compliance analysis
            if compliance_frameworks:
                compliance_results = await self._compliance_analysis(
                    files, cloud_provider, compliance_frameworks
                )
                results["compliance_results"] = compliance_results
            
            # Calculate overall security score
            results["overall_security_score"] = self._calculate_security_score(results)
            
            # Generate recommendations
            results["recommendations"] = self._generate_security_recommendations(results)
            
            return results
            
        except Exception as e:
            print(f"Security analysis error: {e}")
            return {
                "error": str(e),
                "overall_security_score": 0,
                "critical_issues": [],
                "high_issues": [],
                "medium_issues": [],
                "low_issues": [],
                "recommendations": [],
                "ai_disabled": True
            }
    
    async def _pattern_analysis(self, files: List[str], cloud_provider: str) -> Dict[str, Any]:
        """Perform pattern-based security analysis"""
        issues = {
            "critical_issues": [],
            "high_issues": [],
            "medium_issues": [],
            "low_issues": []
        }
        
        patterns = self.security_patterns.get(cloud_provider, {})
        
        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                file_name = Path(file_path).name
                
                # Check each security pattern
                for pattern_name, pattern in patterns.items():
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    
                    for match in matches:
                        line_number = content[:match.start()].count('\n') + 1
                        
                        issue = {
                            "file": file_name,
                            "line": line_number,
                            "pattern": pattern_name,
                            "matched_text": match.group(),
                            "description": self._get_pattern_description(pattern_name, cloud_provider),
                            "severity": self._get_pattern_severity(pattern_name),
                            "recommendation": self._get_pattern_recommendation(pattern_name, cloud_provider)
                        }
                        
                        # Categorize by severity
                        severity = issue["severity"]
                        if severity == "critical":
                            issues["critical_issues"].append(issue)
                        elif severity == "high":
                            issues["high_issues"].append(issue)
                        elif severity == "medium":
                            issues["medium_issues"].append(issue)
                        else:
                            issues["low_issues"].append(issue)
                            
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
        
        return issues
    
    async def _ai_security_analysis(self, files: List[str], cloud_provider: str) -> Dict[str, Any]:
        """Perform AI-powered security analysis"""
        try:
            # Check if AI is enabled
            if not self.ai_enabled:
                return {
                    "ai_issues": [],
                    "ai_compliance": [],
                    "ai_best_practices": [],
                    "ai_disabled": True
                }
            
            # Read all files
            file_contents = []
            for file_path in files:
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    file_contents.append(f"File: {Path(file_path).name}\n{content}\n")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
            
            if not file_contents:
                return {"ai_issues": [], "ai_recommendations": []}
            
            combined_content = "\n".join(file_contents)
            
            # Create AI prompt
            prompt = f"""
            Analyze the following {cloud_provider.upper()} infrastructure code for security vulnerabilities and best practices.
            
            Infrastructure Code:
            {combined_content}
            
            Please provide a comprehensive security analysis including:
            1. Security vulnerabilities found
            2. Compliance issues
            3. Best practice violations
            4. Specific recommendations for improvement
            
            Focus on:
            - Network security (security groups, firewalls, VPCs)
            - Data protection (encryption, access controls)
            - Identity and access management
            - Monitoring and logging
            - Compliance with security standards
            
            Return the analysis in JSON format with the following structure:
            {{
                "vulnerabilities": [
                    {{
                        "type": "vulnerability_type",
                        "severity": "critical|high|medium|low",
                        "description": "detailed description",
                        "location": "file and line reference",
                        "recommendation": "how to fix"
                    }}
                ],
                "compliance_issues": [
                    {{
                        "framework": "compliance_framework",
                        "requirement": "specific requirement",
                        "status": "compliant|non_compliant",
                        "description": "explanation"
                    }}
                ],
                "best_practices": [
                    {{
                        "category": "security_category",
                        "recommendation": "specific recommendation",
                        "priority": "high|medium|low"
                    }}
                ]
            }}
            """
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a cybersecurity expert specializing in cloud infrastructure security analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            # Parse AI response
            ai_content = response.choices[0].message.content
            
            try:
                ai_results = json.loads(ai_content)
                return {
                    "ai_issues": ai_results.get("vulnerabilities", []),
                    "ai_compliance": ai_results.get("compliance_issues", []),
                    "ai_best_practices": ai_results.get("best_practices", [])
                }
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "ai_issues": [],
                    "ai_compliance": [],
                    "ai_best_practices": [],
                    "ai_raw_response": ai_content
                }
                
        except Exception as e:
            return {
                "ai_issues": [],
                "ai_compliance": [],
                "ai_best_practices": [],
                "ai_error": str(e)
            }
    
    async def _compliance_analysis(
        self, 
        files: List[str], 
        cloud_provider: str, 
        frameworks: List[str]
    ) -> Dict[str, Any]:
        """Analyze compliance with specified frameworks"""
        compliance_results = {}
        
        for framework in frameworks:
            if framework in self.compliance_frameworks:
                framework_info = self.compliance_frameworks[framework]
                compliance_results[framework] = {
                    "name": framework_info["name"],
                    "overall_compliant": True,
                    "requirements": []
                }
                
                # Check each requirement
                for requirement in framework_info["rules"]:
                    # This is a simplified check - in production, you'd have more sophisticated logic
                    is_compliant = await self._check_compliance_requirement(
                        files, cloud_provider, framework, requirement
                    )
                    
                    compliance_results[framework]["requirements"].append({
                        "requirement": requirement,
                        "compliant": is_compliant,
                        "details": "Compliance check completed"
                    })
                    
                    if not is_compliant:
                        compliance_results[framework]["overall_compliant"] = False
        
        return compliance_results
    
    async def _check_compliance_requirement(
        self, 
        files: List[str], 
        cloud_provider: str, 
        framework: str, 
        requirement: str
    ) -> bool:
        """Check if a specific compliance requirement is met"""
        # Simplified compliance checking
        # In production, this would be much more sophisticated
        
        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Check for common compliance violations
                if "0.0.0.0/0" in content and "security" in requirement.lower():
                    return False
                
                if "encryption" in requirement.lower() and "encryption = false" in content:
                    return False
                
                if "public" in requirement.lower() and "publicly_accessible = true" in content:
                    return False
                    
            except Exception:
                continue
        
        return True
    
    def _calculate_security_score(self, results: Dict[str, Any]) -> int:
        """Calculate overall security score based on issues found"""
        score = 100
        
        # Deduct points for issues
        score -= len(results.get("critical_issues", [])) * 20
        score -= len(results.get("high_issues", [])) * 10
        score -= len(results.get("medium_issues", [])) * 5
        score -= len(results.get("low_issues", [])) * 2
        
        # Ensure score doesn't go below 0
        return max(0, score)
    
    def _generate_security_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate security recommendations based on analysis results"""
        recommendations = []
        
        # Critical issues recommendations
        if results.get("critical_issues"):
            recommendations.append("🔴 CRITICAL: Address all critical security vulnerabilities immediately")
        
        # High issues recommendations
        if results.get("high_issues"):
            recommendations.append("🟠 HIGH: Review and fix high-severity security issues")
        
        # Specific recommendations based on patterns
        for issue in results.get("critical_issues", []) + results.get("high_issues", []):
            if "security_group_open" in issue.get("pattern", ""):
                recommendations.append("🔒 Restrict security group rules to specific IP ranges instead of 0.0.0.0/0")
            
            if "s3_public_access" in issue.get("pattern", ""):
                recommendations.append("🪣 Disable public access for S3 buckets and use IAM policies for access control")
            
            if "encryption_disabled" in issue.get("pattern", ""):
                recommendations.append("🔐 Enable encryption for all data at rest and in transit")
        
        # Compliance recommendations
        for framework, compliance in results.get("compliance_results", {}).items():
            if not compliance.get("overall_compliant", True):
                recommendations.append(f"📋 {framework.upper()}: Address compliance violations to meet {compliance['name']} requirements")
        
        # General recommendations
        if results.get("overall_security_score", 100) < 80:
            recommendations.append("🛡️ Implement comprehensive security monitoring and alerting")
            recommendations.append("📊 Regular security audits and penetration testing recommended")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _get_pattern_description(self, pattern_name: str, cloud_provider: str) -> str:
        """Get description for a security pattern"""
        descriptions = {
            "security_group_open": "Security group allows unrestricted access (0.0.0.0/0)",
            "s3_public_access": "S3 bucket has public access enabled",
            "rds_publicly_accessible": "RDS instance is publicly accessible",
            "iam_policy_wildcard": "IAM policy uses wildcard (*) resource permissions",
            "encryption_disabled": "Encryption is explicitly disabled",
            "ssl_disabled": "SSL/TLS encryption is disabled"
        }
        return descriptions.get(pattern_name, f"Security issue detected: {pattern_name}")
    
    def _get_pattern_severity(self, pattern_name: str) -> str:
        """Get severity level for a security pattern"""
        critical_patterns = ["security_group_open", "iam_policy_wildcard"]
        high_patterns = ["s3_public_access", "rds_publicly_accessible"]
        medium_patterns = ["encryption_disabled", "ssl_disabled"]
        
        if pattern_name in critical_patterns:
            return "critical"
        elif pattern_name in high_patterns:
            return "high"
        elif pattern_name in medium_patterns:
            return "medium"
        else:
            return "low"
    
    def _get_pattern_recommendation(self, pattern_name: str, cloud_provider: str) -> str:
        """Get recommendation for fixing a security pattern"""
        recommendations = {
            "security_group_open": "Restrict security group rules to specific IP ranges and ports",
            "s3_public_access": "Disable public access and use IAM policies for controlled access",
            "rds_publicly_accessible": "Set publicly_accessible = false and use VPC for access",
            "iam_policy_wildcard": "Replace wildcard (*) with specific resource ARNs",
            "encryption_disabled": "Enable encryption for data protection",
            "ssl_disabled": "Enable SSL/TLS encryption for secure communication"
        }
        return recommendations.get(pattern_name, "Review and fix the identified security issue")
    
    async def generate_security_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive security report"""
        report = f"""# 🔒 Security Analysis Report

## 📊 Executive Summary
- **Overall Security Score**: {results.get('overall_security_score', 0)}/100
- **Cloud Provider**: {results.get('cloud_provider', 'Unknown').upper()}
- **Analysis Date**: {results.get('timestamp', 'Unknown')}

## 🚨 Security Issues Found

### Critical Issues ({len(results.get('critical_issues', []))})
"""
        
        for issue in results.get('critical_issues', []):
            report += f"""- **{issue.get('file', 'Unknown')}:{issue.get('line', 'Unknown')}** - {issue.get('description', 'No description')}
  - Recommendation: {issue.get('recommendation', 'No recommendation')}
"""
        
        report += f"""
### High Issues ({len(results.get('high_issues', []))})
"""
        
        for issue in results.get('high_issues', []):
            report += f"""- **{issue.get('file', 'Unknown')}:{issue.get('line', 'Unknown')}** - {issue.get('description', 'No description')}
  - Recommendation: {issue.get('recommendation', 'No recommendation')}
"""
        
        report += f"""
### Medium Issues ({len(results.get('medium_issues', []))})
"""
        
        for issue in results.get('medium_issues', []):
            report += f"""- **{issue.get('file', 'Unknown')}:{issue.get('line', 'Unknown')}** - {issue.get('description', 'No description')}
  - Recommendation: {issue.get('recommendation', 'No recommendation')}
"""
        
        # Compliance section
        if results.get('compliance_results'):
            report += """
## 📋 Compliance Analysis
"""
            for framework, compliance in results.get('compliance_results', {}).items():
                status = "✅ Compliant" if compliance.get('overall_compliant') else "❌ Non-Compliant"
                report += f"""
### {compliance.get('name', framework.upper())} - {status}
"""
                for req in compliance.get('requirements', []):
                    req_status = "✅" if req.get('compliant') else "❌"
                    report += f"- {req_status} {req.get('requirement', 'Unknown requirement')}\n"
        
        # Recommendations section
        if results.get('recommendations'):
            report += """
## 🛠️ Recommendations
"""
            for rec in results.get('recommendations', []):
                report += f"- {rec}\n"
        
        report += """
---
*Generated by InfraMorph Security Analyzer*
"""
        
        return report 