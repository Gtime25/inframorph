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
from datetime import datetime

class GitHubService:
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required. Please set your GitHub personal access token in the .env file.")
        
        try:
            self.github = Github(self.github_token)
            # Test the token by getting the authenticated user
            self.github.get_user()
        except Exception as e:
            raise ValueError(f"Invalid or expired GitHub token: {str(e)}. Please check your GITHUB_TOKEN in the .env file.")
    
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
    
    async def create_automated_prs(
        self, 
        repo_url: str, 
        analysis_results: Dict[str, Any],
        create_separate_prs: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Create automated pull requests based on analysis results.
        
        Args:
            repo_url: GitHub repository URL
            analysis_results: Results from the analysis
            create_separate_prs: Whether to create separate PRs for different categories
            
        Returns:
            List of created PR information
        """
        try:
            owner, repo_name = self._parse_github_url(repo_url)
            repo = self.github.get_repo(f"{owner}/{repo_name}")
            
            prs_created = []
            
            # Debug: Check what we have in analysis_results
            print(f"Debug - Analysis results keys: {list(analysis_results.keys())}")
            print(f"Debug - Security issues: {len(analysis_results.get('security_issues', []))}")
            print(f"Debug - Cost optimizations: {len(analysis_results.get('cost_optimizations', []))}")
            print(f"Debug - Recommendations: {len(analysis_results.get('recommendations', []))}")
            print(f"Debug - Naming issues: {len(analysis_results.get('naming_issues', []))}")
            print(f"Debug - Refactored code: {len(analysis_results.get('refactored_code', []))}")
            
            if create_separate_prs:
                # Create separate PRs for different categories
                categories = {
                    'security': {
                        'title': '🔒 Security Fixes',
                        'description': 'Critical security vulnerabilities and fixes',
                        'issues': analysis_results.get('security_issues', []),
                        'priority': 'high'
                    },
                    'cost': {
                        'title': '💰 Cost Optimizations',
                        'description': 'Cost optimization opportunities',
                        'issues': analysis_results.get('cost_optimizations', []),
                        'priority': 'medium'
                    },
                    'best_practices': {
                        'title': '📋 Best Practices',
                        'description': 'Infrastructure best practices and improvements',
                        'issues': analysis_results.get('recommendations', []),
                        'priority': 'medium'
                    },
                    'naming': {
                        'title': '🏷️ Naming Conventions',
                        'description': 'Naming convention improvements',
                        'issues': analysis_results.get('naming_issues', []),
                        'priority': 'low'
                    }
                }
                
                for category, config in categories.items():
                    print(f"Debug - Processing category {category} with {len(config['issues'])} issues")
                    if config['issues']:
                        pr_info = await self._create_category_pr(
                            repo, category, config, analysis_results
                        )
                        if pr_info:
                            prs_created.append(pr_info)
                        else:
                            print(f"Debug - No PR created for category {category}")
                    else:
                        print(f"Debug - No issues found for category {category}")
            else:
                # Create one comprehensive PR
                pr_info = await self._create_comprehensive_pr(
                    repo, analysis_results
                )
                if pr_info:
                    prs_created.append(pr_info)
                else:
                    print("Debug - No comprehensive PR created")
            
            print(f"Debug - Total PRs created: {len(prs_created)}")
            return prs_created
            
        except Exception as e:
            raise Exception(f"Error creating automated PRs: {str(e)}")
    
    async def _create_category_pr(
        self, 
        repo, 
        category: str, 
        config: Dict[str, Any], 
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a PR for a specific category of issues"""
        try:
            print(f"Debug - Creating PR for category: {category}")
            
            # Generate branch name
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            branch_name = f"inframorph-{category}-{timestamp}"
            
            # Create branch
            base_branch = repo.default_branch
            base_ref = repo.get_branch(base_branch)
            repo.create_git_ref(f"refs/heads/{branch_name}", base_ref.commit.sha)
            
            # Apply changes for this category
            changes_applied = []
            refactored_files = analysis_results.get('refactored_code', [])
            
            print(f"Debug - Found {len(refactored_files)} refactored files")
            
            for file_info in refactored_files:
                file_path = file_info.get('file_path')
                print(f"Debug - Processing file: {file_path}")
                if file_path and self._should_apply_changes(file_path, category, config['issues']):
                    try:
                        # Try to get current file content
                        try:
                            file_content = repo.get_contents(file_path, ref=branch_name)
                            file_exists = True
                        except Exception as e:
                            if "404" in str(e):
                                print(f"Debug - File {file_path} doesn't exist, will create it")
                                file_exists = False
                            else:
                                raise e
                        
                        if file_exists:
                            # Update existing file
                            repo.update_file(
                                path=file_path,
                                message=f"InfraMorph {category}: {file_info.get('changes_summary', 'Improvements')}",
                                content=file_info.get('refactored_content', ''),
                                sha=file_content.sha,
                                branch=branch_name
                            )
                        else:
                            # Create new file
                            repo.create_file(
                                path=file_path,
                                message=f"InfraMorph {category}: {file_info.get('changes_summary', 'Create new file with improvements')}",
                                content=file_info.get('refactored_content', ''),
                                branch=branch_name
                            )
                        
                        changes_applied.append({
                            'file_path': file_path,
                            'changes_summary': file_info.get('changes_summary', 'Improvements')
                        })
                        
                        print(f"Debug - Successfully {'updated' if file_exists else 'created'} file: {file_path}")
                        
                    except Exception as e:
                        print(f"Error updating file {file_path}: {e}")
                else:
                    print(f"Debug - Skipping file {file_path} (should_apply_changes returned False)")
            
            print(f"Debug - Changes applied: {len(changes_applied)}")
            
            if not changes_applied:
                print(f"Debug - No changes applied for category {category}, returning None")
                return None  # No changes to apply
            
            # Create PR
            pr_title = f"InfraMorph: {config['title']}"
            pr_body = self._create_category_pr_description(
                category, config, changes_applied, analysis_results
            )
            
            # Add labels based on priority
            labels = [f"inframorph-{category}", f"priority-{config['priority']}"]
            
            pr = repo.create_pull(
                title=pr_title,
                body=pr_body,
                base=base_branch,
                head=branch_name
            )
            
            # Add labels
            pr.add_to_labels(*labels)
            
            print(f"Debug - Successfully created PR: {pr.html_url}")
            
            return {
                'pr_url': pr.html_url,
                'pr_number': pr.number,
                'title': pr_title,
                'category': category,
                'priority': config['priority'],
                'changes_count': len(changes_applied),
                'branch_name': branch_name
            }
            
        except Exception as e:
            print(f"Error creating category PR for {category}: {e}")
            return None
    
    async def _create_comprehensive_pr(
        self, 
        repo, 
        analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create one comprehensive PR with all changes"""
        try:
            # Generate branch name
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            branch_name = f"inframorph-comprehensive-{timestamp}"
            
            # Create branch
            base_branch = repo.default_branch
            base_ref = repo.get_branch(base_branch)
            repo.create_git_ref(f"refs/heads/{branch_name}", base_ref.commit.sha)
            
            # Apply all changes
            changes_applied = []
            refactored_files = analysis_results.get('refactored_code', [])
            
            for file_info in refactored_files:
                file_path = file_info.get('file_path')
                if file_path:
                    try:
                        # Try to get current file content
                        try:
                            file_content = repo.get_contents(file_path, ref=branch_name)
                            file_exists = True
                        except Exception as e:
                            if "404" in str(e):
                                print(f"Debug - File {file_path} doesn't exist, will create it")
                                file_exists = False
                            else:
                                raise e
                        
                        if file_exists:
                            # Update existing file
                            repo.update_file(
                                path=file_path,
                                message=f"InfraMorph comprehensive: {file_info.get('changes_summary', 'Improvements')}",
                                content=file_info.get('refactored_content', ''),
                                sha=file_content.sha,
                                branch=branch_name
                            )
                        else:
                            # Create new file
                            repo.create_file(
                                path=file_path,
                                message=f"InfraMorph comprehensive: {file_info.get('changes_summary', 'Create new file with improvements')}",
                                content=file_info.get('refactored_content', ''),
                                branch=branch_name
                            )
                        
                        changes_applied.append({
                            'file_path': file_path,
                            'changes_summary': file_info.get('changes_summary', 'Improvements')
                        })
                        
                        print(f"Debug - Successfully {'updated' if file_exists else 'created'} file: {file_path}")
                        
                    except Exception as e:
                        print(f"Error updating file {file_path}: {e}")
            
            if not changes_applied:
                return None  # No changes to apply
            
            # Create PR
            pr_title = "InfraMorph: Comprehensive Infrastructure Optimization"
            pr_body = self._create_comprehensive_pr_description(
                changes_applied, analysis_results
            )
            
            # Add labels
            labels = ["inframorph-comprehensive", "priority-high"]
            
            pr = repo.create_pull(
                title=pr_title,
                body=pr_body,
                base=base_branch,
                head=branch_name
            )
            
            # Add labels
            pr.add_to_labels(*labels)
            
            return {
                'pr_url': pr.html_url,
                'pr_number': pr.number,
                'title': pr_title,
                'category': 'comprehensive',
                'priority': 'high',
                'changes_count': len(changes_applied),
                'branch_name': branch_name
            }
            
        except Exception as e:
            print(f"Error creating comprehensive PR: {e}")
            return None
    
    def _should_apply_changes(self, file_path: str, category: str, issues: List[Dict]) -> bool:
        """Determine if changes should be applied to a file based on category and issues"""
        # This is a simplified logic - in a real implementation, you'd have more sophisticated
        # mapping between issues and files
        return True  # For now, apply all changes
    
    def _create_category_pr_description(
        self, 
        category: str, 
        config: Dict[str, Any], 
        changes_applied: List[Dict], 
        analysis_results: Dict[str, Any]
    ) -> str:
        """Create detailed PR description for a specific category"""
        
        category_icons = {
            'security': '🔒',
            'cost': '💰',
            'best_practices': '📋',
            'naming': '🏷️'
        }
        
        icon = category_icons.get(category, '📝')
        
        description = f"""# {icon} InfraMorph: {config['title']}

{config['description']}

## 📊 Analysis Summary

This PR addresses **{len(config['issues'])} issues** identified by InfraMorph's AI analysis.

## 🔧 Changes Applied

"""
        
        for change in changes_applied:
            description += f"### {change['file_path']}\n"
            description += f"- **Summary**: {change['changes_summary']}\n\n"
        
        description += f"""## 📋 Detailed Issues

"""
        
        for i, issue in enumerate(config['issues'][:5], 1):  # Show first 5 issues
            if category == 'security':
                description += f"### {i}. {issue.get('title', 'Security Issue')}\n"
                description += f"- **Severity**: {issue.get('severity', 'Unknown')}\n"
                description += f"- **Description**: {issue.get('description', 'No description')}\n"
                description += f"- **Recommendation**: {issue.get('recommendation', 'No recommendation')}\n\n"
            elif category == 'cost':
                description += f"### {i}. {issue.get('resource_type', 'Cost Optimization')}\n"
                description += f"- **Current Cost**: {issue.get('current_cost', 'Unknown')}\n"
                description += f"- **Potential Savings**: {issue.get('potential_savings', 'Unknown')}\n"
                description += f"- **Recommendation**: {issue.get('recommendation', 'No recommendation')}\n\n"
            elif category == 'best_practices':
                description += f"### {i}. {issue.get('title', 'Best Practice')}\n"
                description += f"- **Priority**: {issue.get('priority', 'Unknown')}\n"
                description += f"- **Description**: {issue.get('description', 'No description')}\n"
                description += f"- **Impact**: {issue.get('impact', 'No impact specified')}\n\n"
            elif category == 'naming':
                description += f"### {i}. {issue.get('issue_type', 'Naming Issue')}\n"
                description += f"- **Current**: `{issue.get('current_name', 'Unknown')}`\n"
                description += f"- **Suggested**: `{issue.get('suggested_name', 'Unknown')}`\n"
                description += f"- **Reason**: {issue.get('reason', 'No reason specified')}\n\n"
        
        if len(config['issues']) > 5:
            description += f"*... and {len(config['issues']) - 5} more issues*\n\n"
        
        description += f"""## 🚀 Next Steps

1. **Review Changes**: Carefully review each modification
2. **Test**: Deploy to a staging environment first
3. **Monitor**: Watch for any issues after deployment
4. **Iterate**: Use feedback to improve future analyses

## 📈 Impact Assessment

- **Risk Level**: {config['priority'].title()}
- **Estimated Time**: 15-30 minutes to review
- **Rollback**: Easy - all changes are in separate branch

---
*Generated by InfraMorph - AI-powered infrastructure optimization tool*
"""
        
        return description
    
    def _create_comprehensive_pr_description(
        self, 
        changes_applied: List[Dict], 
        analysis_results: Dict[str, Any]
    ) -> str:
        """Create comprehensive PR description with all changes"""
        
        description = """# 🚀 InfraMorph: Comprehensive Infrastructure Optimization

This pull request contains a comprehensive set of improvements for your infrastructure code, addressing security, cost, best practices, and naming conventions.

## 📊 Analysis Overview

"""
        
        # Add summary statistics
        security_count = len(analysis_results.get('security_issues', []))
        cost_count = len(analysis_results.get('cost_optimizations', []))
        recommendations_count = len(analysis_results.get('recommendations', []))
        naming_count = len(analysis_results.get('naming_issues', []))
        
        description += f"""
- 🔒 **Security Issues**: {security_count} vulnerabilities addressed
- 💰 **Cost Optimizations**: {cost_count} opportunities identified
- 📋 **Best Practices**: {recommendations_count} improvements suggested
- 🏷️ **Naming Issues**: {naming_count} convention improvements

## 🔧 Changes Applied

"""
        
        for change in changes_applied:
            description += f"### {change['file_path']}\n"
            description += f"- **Summary**: {change['changes_summary']}\n\n"
        
        description += """## 🎯 Priority Categories

### 🔒 Security (High Priority)
Critical security vulnerabilities and misconfigurations that should be addressed immediately.

### 💰 Cost Optimization (Medium Priority)
Opportunities to reduce infrastructure costs without impacting performance.

### 📋 Best Practices (Medium Priority)
Architectural improvements and best practice implementations.

### 🏷️ Naming Conventions (Low Priority)
Consistency improvements for better resource management.

## 🚀 Implementation Guide

1. **Review**: Go through each change carefully
2. **Test**: Deploy to staging environment
3. **Validate**: Ensure all functionality works as expected
4. **Deploy**: Apply to production during maintenance window
5. **Monitor**: Watch for any issues post-deployment

## 📈 Expected Benefits

- **Security**: Reduced attack surface and compliance improvements
- **Cost**: Potential 10-30% cost savings
- **Maintainability**: Better code organization and consistency
- **Performance**: Optimized resource configurations

---
*Generated by InfraMorph - AI-powered infrastructure optimization tool*
"""
        
        return description 