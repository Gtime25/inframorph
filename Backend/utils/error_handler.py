import logging
import traceback
from typing import Dict, Any, Optional
from fastapi import HTTPException
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('inframorph.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class InfraMorphError(Exception):
    """Base exception for InfraMorph application"""
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class FileProcessingError(InfraMorphError):
    """Raised when file processing fails"""
    pass

class AnalysisError(InfraMorphError):
    """Raised when analysis fails"""
    pass

class CloudProviderError(InfraMorphError):
    """Raised when cloud provider operations fail"""
    pass

class SecurityAnalysisError(InfraMorphError):
    """Raised when security analysis fails"""
    pass

class DriftDetectionError(InfraMorphError):
    """Raised when drift detection fails"""
    pass

def handle_analysis_error(error: Exception, context: str = "analysis") -> Dict[str, Any]:
    """Handle analysis errors and return user-friendly response"""
    error_id = f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Log the error
    logger.error(f"Error ID: {error_id}, Context: {context}, Error: {str(error)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Determine error type and provide appropriate message
    if isinstance(error, FileProcessingError):
        user_message = "There was an issue processing your files. Please check that your files are valid Terraform or Ansible files."
        error_type = "file_processing"
    elif isinstance(error, AnalysisError):
        user_message = "The analysis encountered an issue. Please try again or contact support if the problem persists."
        error_type = "analysis"
    elif isinstance(error, CloudProviderError):
        user_message = "Unable to connect to cloud provider. Please check your credentials and try again."
        error_type = "cloud_provider"
    elif isinstance(error, SecurityAnalysisError):
        user_message = "Security analysis failed. Please check your files and try again."
        error_type = "security_analysis"
    elif isinstance(error, DriftDetectionError):
        user_message = "Drift detection failed. Please check your cloud credentials and try again."
        error_type = "drift_detection"
    else:
        user_message = "An unexpected error occurred. Please try again or contact support."
        error_type = "unknown"
    
    return {
        "error": True,
        "error_id": error_id,
        "message": user_message,
        "error_type": error_type,
        "timestamp": datetime.now().isoformat(),
        "context": context
    }

def validate_file_upload(files: list, allowed_extensions: set) -> Dict[str, Any]:
    """Validate uploaded files and return validation result"""
    if not files:
        return {
            "valid": False,
            "error": "No files were uploaded. Please select at least one file."
        }
    
    invalid_files = []
    total_size = 0
    max_size = 10 * 1024 * 1024  # 10MB limit
    
    for file in files:
        # Check file extension
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            invalid_files.append(f"{file.filename} (unsupported format)")
        
        # Check file size
        if hasattr(file, 'size') and file.size > max_size:
            invalid_files.append(f"{file.filename} (file too large)")
        
        total_size += getattr(file, 'size', 0)
    
    if invalid_files:
        return {
            "valid": False,
            "error": f"Invalid files: {', '.join(invalid_files)}"
        }
    
    if total_size > max_size:
        return {
            "valid": False,
            "error": "Total file size exceeds 10MB limit"
        }
    
    return {"valid": True}

def create_progress_tracker(total_steps: int) -> Dict[str, Any]:
    """Create a progress tracker for long-running operations"""
    return {
        "total_steps": total_steps,
        "current_step": 0,
        "status": "initializing",
        "progress_percentage": 0,
        "start_time": datetime.now().isoformat(),
        "steps": []
    }

def update_progress(tracker: Dict[str, Any], step: str, status: str = "in_progress") -> Dict[str, Any]:
    """Update progress tracker"""
    tracker["current_step"] += 1
    tracker["status"] = status
    tracker["progress_percentage"] = int((tracker["current_step"] / tracker["total_steps"]) * 100)
    tracker["steps"].append({
        "step": step,
        "timestamp": datetime.now().isoformat(),
        "status": status
    })
    return tracker

def format_error_response(error: Exception, context: str = "general") -> HTTPException:
    """Format error for HTTP response"""
    error_info = handle_analysis_error(error, context)
    
    return HTTPException(
        status_code=500,
        detail={
            "error": True,
            "message": error_info["message"],
            "error_id": error_info["error_id"],
            "error_type": error_info["error_type"]
        }
    ) 