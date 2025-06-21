from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class AnalysisRequest(BaseModel):
    github_repo: Optional[str] = None
    analysis_type: str = Field(default="comprehensive", description="Type of analysis to perform")
    
class SecurityIssue(BaseModel):
    severity: str = Field(..., description="High, Medium, Low")
    title: str = Field(..., description="Issue title")
    description: str = Field(..., description="Detailed description")
    file_path: str = Field(..., description="File where issue was found")
    line_number: Optional[int] = None
    recommendation: str = Field(..., description="How to fix the issue")
    
class CostOptimization(BaseModel):
    resource_type: str = Field(..., description="Type of resource (e.g., EC2, S3)")
    current_cost: Optional[str] = None
    potential_savings: Optional[str] = None
    recommendation: str = Field(..., description="Cost optimization suggestion")
    file_path: str = Field(..., description="File where resource is defined")
    
class NamingIssue(BaseModel):
    issue_type: str = Field(..., description="Type of naming issue")
    current_name: str = Field(..., description="Current resource name")
    suggested_name: str = Field(..., description="Suggested better name")
    file_path: str = Field(..., description="File where issue was found")
    reason: str = Field(..., description="Why this change is recommended")
    
class Recommendation(BaseModel):
    category: str = Field(..., description="Category of recommendation")
    title: str = Field(..., description="Recommendation title")
    description: str = Field(..., description="Detailed description")
    priority: str = Field(..., description="High, Medium, Low")
    impact: str = Field(..., description="Impact of implementing this change")
    
class RefactoredCode(BaseModel):
    file_path: str = Field(..., description="Path to the file")
    original_content: str = Field(..., description="Original code content")
    refactored_content: str = Field(..., description="Refactored code content")
    changes_summary: str = Field(..., description="Summary of changes made")
    
class AnalysisResult(BaseModel):
    summary: str = Field(..., description="Overall analysis summary")
    recommendations: List[Recommendation] = Field(default_factory=list)
    refactored_code: List[RefactoredCode] = Field(default_factory=list)
    security_issues: List[SecurityIssue] = Field(default_factory=list)
    cost_optimizations: List[CostOptimization] = Field(default_factory=list)
    naming_issues: List[NamingIssue] = Field(default_factory=list)
    
class AnalysisResponse(BaseModel):
    analysis_id: str = Field(..., description="Unique analysis ID")
    timestamp: str = Field(..., description="Analysis timestamp")
    summary: str = Field(..., description="Overall analysis summary")
    recommendations: List[Recommendation] = Field(default_factory=list)
    refactored_code: List[RefactoredCode] = Field(default_factory=list)
    security_issues: List[SecurityIssue] = Field(default_factory=list)
    cost_optimizations: List[CostOptimization] = Field(default_factory=list)
    naming_issues: List[NamingIssue] = Field(default_factory=list)
    
class GitHubPRRequest(BaseModel):
    analysis_id: str = Field(..., description="Analysis ID to create PR for")
    repo_url: str = Field(..., description="GitHub repository URL")
    branch_name: str = Field(..., description="Branch name for the PR")
    title: Optional[str] = Field(None, description="PR title")
    description: Optional[str] = Field(None, description="PR description") 