import os
import json
import tempfile
from typing import List, Dict, Any, Optional
from pathlib import Path
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class IACAnalyzer:
    def __init__(self):
        # Initialize OpenAI client
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Fallback to mock data if no API key
        self.use_mock = not openai.api_key
        
        if self.use_mock:
            print("Warning: No OpenAI API key found. Using mock data for analysis.")
    
    async def analyze_files(
        self, 
        file_paths: List[str], 
        analysis_type: str = "comprehensive",
        github_repo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze IaC files and return AI-generated recommendations.
        
        Args:
            file_paths: List of paths to IaC files
            analysis_type: Type of analysis (comprehensive, security, cost, naming)
            github_repo: Optional GitHub repository URL for context
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Read and combine file contents
            file_contents = []
            for file_path in file_paths:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    file_contents.append(f"File: {Path(file_path).name}\n{content}\n")
            
            combined_content = "\n".join(file_contents)
            
            if self.use_mock:
                return self._generate_mock_analysis(analysis_type, file_paths)
            
            # Generate analysis prompt based on type
            prompt = self._create_analysis_prompt(combined_content, analysis_type, github_repo)
            
            # Call OpenAI API
            response = await self._call_openai_api(prompt)
            
            # Parse and structure the response
            return self._parse_analysis_response(response, analysis_type)
            
        except Exception as e:
            print(f"Error during analysis: {e}")
            return self._generate_mock_analysis(analysis_type, file_paths)
    
    def _create_analysis_prompt(self, content: str, analysis_type: str, github_repo: Optional[str] = None) -> str:
        """Create a prompt for the AI analysis."""
        
        base_prompt = f"""
You are an expert DevOps engineer and infrastructure specialist. Analyze the following Infrastructure as Code (IaC) files and provide detailed recommendations.

Infrastructure Code:
{content}

Analysis Type: {analysis_type.title()}

Please provide a comprehensive analysis in the following JSON format:
{{
    "summary": "Brief overview of the infrastructure and main findings",
    "recommendations": [
        {{
            "category": "security|cost|best_practice|naming",
            "severity": "high|medium|low",
            "title": "Short title",
            "description": "Detailed description",
            "impact": "What this means for the infrastructure",
            "suggestion": "How to fix or improve this"
        }}
    ],
    "refactored_code": {{
        "file_name": "Refactored version of the code with improvements"
    }},
    "security_issues": [
        {{
            "issue": "Security vulnerability description",
            "severity": "high|medium|low",
            "recommendation": "How to fix this security issue"
        }}
    ],
    "cost_optimizations": [
        {{
            "optimization": "Cost optimization opportunity",
            "potential_savings": "Estimated cost savings",
            "implementation": "How to implement this optimization"
        }}
    ],
    "naming_issues": [
        {{
            "issue": "Naming convention violation",
            "current_name": "Current problematic name",
            "suggested_name": "Better naming suggestion",
            "reason": "Why this naming is better"
        }}
    ]
}}
"""
        
        if github_repo:
            base_prompt += f"\nGitHub Repository Context: {github_repo}"
        
        if analysis_type == "security":
            base_prompt += "\n\nFocus specifically on security vulnerabilities, misconfigurations, and compliance issues."
        elif analysis_type == "cost":
            base_prompt += "\n\nFocus specifically on cost optimization opportunities, resource sizing, and efficiency improvements."
        
        return base_prompt
    
    async def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API and return the response."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert DevOps engineer specializing in infrastructure optimization and security."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=4000,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise
    
    def _parse_analysis_response(self, response: str, analysis_type: str) -> Dict[str, Any]:
        """Parse the AI response and structure it properly."""
        try:
            # Try to extract JSON from the response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                # Try to find JSON in the response
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
            
            parsed = json.loads(json_str)
            
            return {
                "summary": parsed.get("summary", "Analysis completed"),
                "recommendations": parsed.get("recommendations", []),
                "refactored_code": parsed.get("refactored_code", {}),
                "security_issues": parsed.get("security_issues", []),
                "cost_optimizations": parsed.get("cost_optimizations", []),
                "naming_issues": parsed.get("naming_issues", [])
            }
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing AI response: {e}")
            return self._generate_mock_analysis(analysis_type, [])
    
    def _generate_mock_analysis(self, analysis_type: str, file_paths: List[str]) -> Dict[str, Any]:
        """Generate mock analysis data for testing."""
        
        mock_data = {
            "summary": f"Mock {analysis_type} analysis completed for {len(file_paths)} files. This is sample data for demonstration purposes.",
            "recommendations": [
                {
                    "category": "security",
                    "severity": "high",
                    "title": "Enable encryption at rest",
                    "description": "Storage resources should have encryption enabled",
                    "impact": "Data could be exposed if storage is compromised",
                    "suggestion": "Add encryption configuration to storage resources"
                },
                {
                    "category": "cost",
                    "severity": "medium",
                    "title": "Optimize instance sizing",
                    "description": "Current instance types may be oversized for workload",
                    "impact": "Unnecessary costs for unused resources",
                    "suggestion": "Consider smaller instance types or auto-scaling"
                }
            ],
            "refactored_code": {
                "main.tf": """
# Refactored Terraform configuration
resource "aws_instance" "example" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"  # Optimized size
  
  tags = {
    Name = "example-instance"
    Environment = "production"
  }
  
  # Added encryption
  root_block_device {
    encrypted = true
  }
}
"""
            },
            "security_issues": [
                {
                    "issue": "Missing encryption configuration",
                    "severity": "high",
                    "recommendation": "Enable encryption for all storage resources"
                }
            ],
            "cost_optimizations": [
                {
                    "optimization": "Reduce instance size",
                    "potential_savings": "$50-100/month",
                    "implementation": "Change instance type from t3.large to t3.micro"
                }
            ],
            "naming_issues": [
                {
                    "issue": "Inconsistent naming convention",
                    "current_name": "my-instance",
                    "suggested_name": "prod-web-server-01",
                    "reason": "Follows environment-resource-type-number pattern"
                }
            ]
        }
        
        return mock_data 