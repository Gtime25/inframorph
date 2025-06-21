import os
import re
import tempfile
import subprocess
from typing import List, Dict, Any
from github import Github
from github.Repository import Repository
from github.Branch import Branch
from github.PullRequest import PullRequest
import base64

class GitHubService:
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        
        self.github = Github(self.github_token)
    
    async def get_iac_files(self, repo_url: str) -> List[Dict[str, Any]]:
        """Get IaC files from a GitHub repository"""
        try:
            # Extract owner and repo name from URL
            owner, repo_name = self._parse_github_url(repo_url)
            
            # Get repository
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            
            # Find IaC files
            iac_files = []
            allowed_extensions = {'.tf', '.tfvars', '.hcl', '.yml', '.yaml', '.ansible'}
            
            # Search for files recursively
            contents = repo.get_contents("")
            while contents:
                file_content = contents.pop(0)
                
                if file_content.type == "dir":
                    contents.extend(repo.get_contents(file_content.path))
                else:
                    file_ext = self._get_file_extension(file_content.name)
                    if file_ext in allowed_extensions:
                        try:
                            # Get file content
                            content = file_content.decoded_content.decode('utf-8')
                            iac_files.append({
                                "name": file_content.name,
                                "path": file_content.path,
                                "content": content,
                                "size": file_content.size,
                                "sha": file_content.sha
                            })
                        except Exception as e:
                            print(f"Error reading file {file_content.path}: {e}")
            
            return iac_files
            
        except Exception as e:
            raise Exception(f"Error accessing GitHub repository: {str(e)}")
    
    async def create_pull_request(
        self, 
        repo_url: str, 
        branch_name: str, 
        changes: List[Dict[str, Any]]
    ) -> str:
        """Create a pull request with suggested changes"""
        try:
            # Extract owner and repo name
            owner, repo_name = self._parse_github_url(repo_url)
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            
            # Create a new branch
            base_branch = repo.default_branch
            new_branch = f"inframorph-optimization-{branch_name}"
            
            # Get the latest commit from base branch
            base_ref = repo.get_branch(base_branch)
            
            # Create new branch
            repo.create_git_ref(f"refs/heads/{new_branch}", base_ref.commit.sha)
            
            # Apply changes
            commit_messages = []
            for change in changes:
                file_path = change.get("file_path")
                refactored_content = change.get("refactored_content")
                
                if file_path and refactored_content:
                    try:
                        # Get current file content
                        file_content = repo.get_contents(file_path, ref=new_branch)
                        
                        # Update file
                        repo.update_file(
                            path=file_path,
                            message=f"InfraMorph optimization: {change.get('changes_summary', 'Code improvements')}",
                            content=refactored_content,
                            sha=file_content.sha,
                            branch=new_branch
                        )
                        
                        commit_messages.append(change.get('changes_summary', 'Code improvements'))
                        
                    except Exception as e:
                        print(f"Error updating file {file_path}: {e}")
            
            # Create pull request
            pr_title = "InfraMorph: Infrastructure Optimization Suggestions"
            pr_body = self._create_pr_description(changes, commit_messages)
            
            pr = repo.create_pull(
                title=pr_title,
                body=pr_body,
                base=base_branch,
                head=new_branch
            )
            
            return pr.html_url
            
        except Exception as e:
            raise Exception(f"Error creating pull request: {str(e)}")
    
    def _parse_github_url(self, url: str) -> tuple:
        """Parse GitHub URL to extract owner and repository name"""
        # Handle different GitHub URL formats
        patterns = [
            r'https://github\.com/([^/]+)/([^/]+)',
            r'git@github\.com:([^/]+)/([^/]+)\.git'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, url)
            if match:
                owner = match.group(1)
                repo_name = match.group(2)
                return owner, repo_name
        
        raise ValueError(f"Invalid GitHub URL format: {url}")
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension from filename"""
        return os.path.splitext(filename)[1].lower()
    
    def _create_pr_description(self, changes: List[Dict[str, Any]], commit_messages: List[str]) -> str:
        """Create a comprehensive PR description"""
        description = """# InfraMorph Infrastructure Optimization

This pull request contains AI-generated optimizations for your infrastructure code.

## Changes Summary

"""
        
        # Add changes summary
        for i, change in enumerate(changes):
            description += f"### {change.get('file_path', 'Unknown file')}\n"
            description += f"- **Summary**: {change.get('changes_summary', 'Code improvements')}\n"
            description += f"- **Commit**: {commit_messages[i] if i < len(commit_messages) else 'Code improvements'}\n\n"
        
        description += """## What was analyzed

The AI analyzed your infrastructure code for:
- 🔒 Security vulnerabilities and misconfigurations
- 💰 Cost optimization opportunities  
- 🏷️ Naming conventions and consistency
- 🏗️ Resource redundancy and unused resources
- 📋 Best practices and architectural improvements
- 🏷️ Tagging and labeling consistency

## Review Instructions

1. Review each change carefully
2. Test the changes in a staging environment
3. Ensure the changes align with your security and compliance requirements
4. Consider the cost implications of any resource changes

## Next Steps

After merging this PR:
1. Apply the changes to your infrastructure
2. Monitor for any issues
3. Consider implementing additional recommendations from the full analysis report

---
*Generated by InfraMorph - AI-powered infrastructure optimization tool*
"""
        
        return description
    
    async def clone_repository(self, repo_url: str, local_path: str = None) -> str:
        """Clone a GitHub repository to local filesystem"""
        if not local_path:
            local_path = tempfile.mkdtemp()
        
        try:
            # Clone the repository
            subprocess.run([
                "git", "clone", repo_url, local_path
            ], check=True, capture_output=True)
            
            return local_path
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error cloning repository: {e.stderr.decode()}")
    
    async def get_repository_info(self, repo_url: str) -> Dict[str, Any]:
        """Get basic information about a GitHub repository"""
        try:
            owner, repo_name = self._parse_github_url(repo_url)
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            
            return {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "default_branch": repo.default_branch,
                "created_at": repo.created_at.isoformat(),
                "updated_at": repo.updated_at.isoformat(),
                "url": repo.html_url
            }
            
        except Exception as e:
            raise Exception(f"Error getting repository info: {str(e)}")
    
    async def validate_repository_access(self, repo_url: str) -> bool:
        """Validate that we have access to the repository"""
        try:
            owner, repo_name = self._parse_github_url(repo_url)
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            
            # Try to access repository contents
            repo.get_contents("")
            return True
            
        except Exception:
            return False 