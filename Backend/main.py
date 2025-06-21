from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import tempfile
import aiofiles
from typing import List, Optional
import json
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from services.iac_analyzer import IACAnalyzer
from services.github_service import GitHubService
from models.database import init_db, save_analysis
from models.schemas import AnalysisRequest, AnalysisResponse, AnalysisResult
from models.auth import (
    User, UserCreate, UserLogin, Token, 
    authenticate_user, create_user, get_user_by_username,
    create_access_token, verify_token, init_auth_db,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI(
    title="InfraMorph API",
    description="AI-powered infrastructure optimization tool",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize databases
init_db()
init_auth_db()

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    username = verify_token(token)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@app.get("/")
async def root():
    return {"message": "InfraMorph API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/auth/signup", response_model=Token)
async def signup(user_data: UserCreate):
    """Create a new user account"""
    # Check if username already exists
    if get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user
    user = create_user(
        username=user_data.username,
        password=user_data.password,
        email=user_data.email
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user
    )

@app.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    """Authenticate user and return access token"""
    user = authenticate_user(user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=user
    )

@app.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_iac(
    files: List[UploadFile] = File(...),
    github_repo: Optional[str] = Form(None),
    analysis_type: str = Form("comprehensive"),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze uploaded IaC files and return AI-generated optimization suggestions.
    
    Args:
        files: List of uploaded Terraform/Ansible files
        github_repo: Optional GitHub repository URL
        analysis_type: Type of analysis (comprehensive, security, cost, naming)
    
    Returns:
        AnalysisResponse with recommendations and refactored code
    """
    try:
        # Validate file types
        allowed_extensions = {'.tf', '.tfvars', '.hcl', '.yml', '.yaml', '.ansible'}
        for file in files:
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in allowed_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file_ext}. Supported: {allowed_extensions}"
                )
        
        # Save uploaded files to temporary directory
        temp_dir = tempfile.mkdtemp()
        file_paths = []
        
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            file_paths.append(file_path)
        
        # Initialize analyzer
        analyzer = IACAnalyzer()
        
        # Perform analysis
        analysis_result = await analyzer.analyze_files(
            file_paths=file_paths,
            analysis_type=analysis_type,
            github_repo=github_repo
        )
        
        # Save analysis to database
        analysis_id = save_analysis(analysis_result)
        
        # Clean up temporary files
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.rmdir(temp_dir)
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            timestamp=datetime.now().isoformat(),
            summary=analysis_result.summary,
            recommendations=analysis_result.recommendations,
            refactored_code=analysis_result.refactored_code,
            security_issues=analysis_result.security_issues,
            cost_optimizations=analysis_result.cost_optimizations,
            naming_issues=analysis_result.naming_issues
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis/{analysis_id}")
async def get_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user)
):
    """Retrieve a specific analysis by ID"""
    try:
        conn = sqlite3.connect('inframorph.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM analyses WHERE id = ?
        """, (analysis_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {
            "analysis_id": result[0],
            "timestamp": result[1],
            "summary": result[2],
            "recommendations": json.loads(result[3]),
            "refactored_code": json.loads(result[4]),
            "security_issues": json.loads(result[5]),
            "cost_optimizations": json.loads(result[6]),
            "naming_issues": json.loads(result[7])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/github/connect")
async def connect_github_repo(
    repo_url: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """Connect to a GitHub repository and analyze its IaC files"""
    try:
        github_service = GitHubService()
        files = await github_service.get_iac_files(repo_url)
        
        return {
            "message": "Successfully connected to GitHub repository",
            "files_found": len(files),
            "files": files
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/github/create-pr")
async def create_pull_request(
    analysis_id: str = Form(...),
    repo_url: str = Form(...),
    branch_name: str = Form(...),
    current_user: User = Depends(get_current_user)
):
    """Create a GitHub pull request with the suggested changes"""
    try:
        # Get analysis results
        conn = sqlite3.connect('inframorph.db')
        cursor = conn.cursor()
        cursor.execute("SELECT refactored_code FROM analyses WHERE id = ?", (analysis_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        refactored_code = json.loads(result[0])
        
        # Create PR
        github_service = GitHubService()
        pr_url = await github_service.create_pull_request(
            repo_url=repo_url,
            branch_name=branch_name,
            changes=refactored_code
        )
        
        return {
            "message": "Pull request created successfully",
            "pr_url": pr_url
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 