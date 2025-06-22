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

IMPORTANT: You MUST generate refactored_code with the EXACT same file names as the original files. Use the file names from the "File:" lines above.

Please provide a comprehensive analysis in the following JSON format:
{{
    "summary": "Brief overview of the infrastructure and main findings",
    "recommendations": [
        {{
            "category": "security|cost|best_practice|naming",
            "title": "Short title",
            "description": "Detailed description",
            "priority": "high|medium|low",
            "impact": "What this means for the infrastructure"
        }}
    ],
    "refactored_code": [
        {{
            "file_path": "EXACT_ORIGINAL_FILENAME.tf",
            "original_content": "Original code content",
            "refactored_content": "Complete refactored version of the file with all improvements applied",
            "changes_summary": "Summary of changes made"
        }}
    ],
    "security_issues": [
        {{
            "severity": "high|medium|low",
            "title": "Security vulnerability title",
            "description": "Detailed description of the security issue",
            "file_path": "EXACT_ORIGINAL_FILENAME.tf",
            "recommendation": "How to fix this security issue"
        }}
    ],
    "cost_optimizations": [
        {{
            "resource_type": "EC2|S3|RDS|etc",
            "current_cost": "Current estimated cost",
            "potential_savings": "Estimated cost savings",
            "recommendation": "How to implement this optimization",
            "file_path": "EXACT_ORIGINAL_FILENAME.tf"
        }}
    ],
    "naming_issues": [
        {{
            "issue_type": "inconsistent_naming|missing_prefix|etc",
            "current_name": "Current problematic name",
            "suggested_name": "Better naming suggestion",
            "file_path": "EXACT_ORIGINAL_FILENAME.tf",
            "reason": "Why this naming is better"
        }}
    ]
}}

CRITICAL REQUIREMENTS:
1. Use the EXACT file names from the original files (e.g., if the file is "aws_demo.tf", use "aws_demo.tf" in all file_path fields)
2. Generate complete refactored_code entries with the full improved file content
3. Ensure refactored_content is a complete, valid Terraform file
4. Make sure all file_path references match the original file names exactly
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
                "refactored_code": parsed.get("refactored_code", []),
                "security_issues": parsed.get("security_issues", []),
                "cost_optimizations": parsed.get("cost_optimizations", []),
                "naming_issues": parsed.get("naming_issues", [])
            }
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing AI response: {e}")
            return self._generate_mock_analysis(analysis_type, [])
    
    def _generate_mock_analysis(self, analysis_type: str, file_paths: List[str]) -> Dict[str, Any]:
        """Generate mock analysis data for testing."""
        
        # Use actual file names from the analysis
        file_name = "main.tf"  # Default fallback
        if file_paths:
            # Get the first file name, or use the most common Terraform file
            file_name = Path(file_paths[0]).name if file_paths else "main.tf"
        
        mock_data = {
            "summary": f"Mock {analysis_type} analysis completed for {len(file_paths)} files. This is sample data for demonstration purposes.",
            "recommendations": [
                {
                    "category": "security",
                    "title": "Enable encryption at rest",
                    "description": "Storage resources should have encryption enabled to protect data at rest",
                    "priority": "high",
                    "impact": "Data could be exposed if storage is compromised"
                },
                {
                    "category": "cost",
                    "title": "Optimize instance sizing",
                    "description": "Current instance types may be oversized for workload requirements",
                    "priority": "medium",
                    "impact": "Unnecessary costs for unused resources"
                },
                {
                    "category": "best_practice",
                    "title": "Add resource tagging",
                    "description": "Implement consistent tagging strategy for better resource management",
                    "priority": "medium",
                    "impact": "Improved resource organization and cost tracking"
                }
            ],
            "refactored_code": [
                {
                    "file_path": file_name,
                    "original_content": "# Original Terraform configuration",
                    "refactored_content": """
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
""",
                    "changes_summary": "Added encryption, optimized instance size, and improved tagging"
                }
            ],
            "security_issues": [
                {
                    "severity": "high",
                    "title": "Missing encryption configuration",
                    "description": "Storage resources lack encryption at rest",
                    "file_path": file_name,
                    "recommendation": "Enable encryption for all storage resources"
                }
            ],
            "cost_optimizations": [
                {
                    "resource_type": "EC2",
                    "current_cost": "$100/month",
                    "potential_savings": "$50/month",
                    "recommendation": "Change instance type from t3.large to t3.micro",
                    "file_path": file_name
                }
            ],
            "naming_issues": [
                {
                    "issue_type": "inconsistent_naming",
                    "current_name": "my-instance",
                    "suggested_name": "prod-web-server-01",
                    "file_path": file_name,
                    "reason": "Follows environment-resource-type-number pattern"
                }
            ]
        }
        
        return mock_data 