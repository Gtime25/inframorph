import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from models.database import get_db, engine, Base
from models.auth import create_access_token, get_current_user, User
from models.schemas import UserCreate, UserLogin, AnalysisRequest, AnalysisResponse
from services.iac_analyzer import analyze_terraform
from services.security_analyzer import analyze_security
from services.github_service import create_automated_prs
from services.drift_detector import detect_drift
from services.cloud_provider import get_cloud_resources
import json
from datetime import datetime, timedelta
from jose import JWTError, jwt

# Load environment variables from .env file
load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

app = FastAPI(title="InfraMorph API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "InfraMorph API is running!"}

@app.post("/auth/signup", response_model=dict)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create new user
    user = User(username=user_data.username)
    user.set_password(user_data.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"username": user.username, "id": user.id}
    }

@app.post("/auth/login", response_model=dict)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not user.check_password(user_data.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"username": user.username, "id": user.id}
    }

@app.get("/user/me", response_model=dict)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "id": current_user.id}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_infrastructure(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Analyze the Terraform code
        analysis_result = analyze_terraform(request.code)
        
        # Store analysis in database (you can implement this)
        # For now, we'll just return the analysis result
        
        return AnalysisResponse(
            analysis_id="analysis_" + str(datetime.now().timestamp()),
            issues=analysis_result.get("issues", []),
            recommendations=analysis_result.get("recommendations", []),
            security_issues=analysis_result.get("security_issues", []),
            cost_optimizations=analysis_result.get("cost_optimizations", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/security/analyze")
async def analyze_security_endpoint(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        security_result = analyze_security(request.code)
        return security_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/github/create-automated-prs")
async def create_prs_endpoint(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    try:
        # Extract data from request
        repo_url = request.get("repo_url")
        analysis_results = request.get("analysis_results", {})
        
        if not repo_url:
            raise HTTPException(status_code=400, detail="GitHub repository URL is required")
        
        # Create automated PRs
        pr_result = create_automated_prs(repo_url, analysis_results)
        return pr_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/drift/detect")
async def detect_drift_endpoint(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    try:
        # Extract data from request
        terraform_code = request.get("terraform_code")
        cloud_provider = request.get("cloud_provider", "aws")
        
        if not terraform_code:
            raise HTTPException(status_code=400, detail="Terraform code is required")
        
        # Detect drift
        drift_result = detect_drift(terraform_code, cloud_provider)
        return drift_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cloud/resources")
async def get_cloud_resources_endpoint(
    cloud_provider: str = "aws",
    current_user: User = Depends(get_current_user)
):
    try:
        resources = get_cloud_resources(cloud_provider)
        return resources
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyses")
async def get_analyses(current_user: User = Depends(get_current_user)):
    # Mock data - in a real app, you'd fetch from database
    return [
        {
            "id": "analysis_1",
            "timestamp": "2024-01-15T10:30:00Z",
            "filename": "main.tf",
            "issues_count": 5,
            "status": "completed"
        },
        {
            "id": "analysis_2", 
            "timestamp": "2024-01-14T15:45:00Z",
            "filename": "infrastructure.tf",
            "issues_count": 3,
            "status": "completed"
        }
    ]

@app.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str, current_user: User = Depends(get_current_user)):
    # Mock data - in a real app, you'd fetch from database
    return {
        "id": analysis_id,
        "timestamp": "2024-01-15T10:30:00Z",
        "filename": "main.tf",
        "issues": [
            {
                "type": "security",
                "severity": "high",
                "message": "S3 bucket is publicly accessible",
                "line": 15,
                "suggestion": "Add bucket policy to restrict access"
            }
        ],
        "recommendations": [
            "Use private subnets for sensitive resources",
            "Enable VPC flow logs",
            "Implement proper IAM roles"
        ]
    }

@app.delete("/analyses/{analysis_id}")
async def delete_analysis(analysis_id: str, current_user: User = Depends(get_current_user)):
    # Mock deletion - in a real app, you'd delete from database
    return {"message": f"Analysis {analysis_id} deleted successfully"}

@app.get("/demo-files/{demo_type}")
async def get_demo_file(demo_type: str):
    """Serve demo files for AWS or Azure"""
    try:
        if demo_type == "aws":
            file_path = "Backend/demo_files/aws_demo.tf"
        elif demo_type == "azure":
            file_path = "Backend/demo_files/azure_demo.tf"
        else:
            raise HTTPException(status_code=400, detail="Invalid demo type. Use 'aws' or 'azure'")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Demo file not found")
        
        with open(file_path, 'r') as file:
            content = file.read()
        
        return {"content": content, "filename": f"{demo_type}_demo.tf"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/github/status")
async def get_github_status(current_user: User = Depends(get_current_user)):
    # Mock GitHub connection status
    return {"connected": False, "username": None}

@app.post("/github/connect")
async def connect_github(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    try:
        token = request.get("token")
        if not token:
            raise HTTPException(status_code=400, detail="GitHub token is required")
        
        # Mock GitHub connection
        return {"connected": True, "username": "github_user"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def submit_feedback(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    try:
        feedback = request.get("feedback")
        rating = request.get("rating")
        
        if not feedback:
            raise HTTPException(status_code=400, detail="Feedback is required")
        
        # Mock feedback submission
        return {"message": "Feedback submitted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 