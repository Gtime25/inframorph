import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, Any
from models.schemas import AnalysisResult
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

def init_db():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect('inframorph.db')
    cursor = conn.cursor()
    
    # Create analyses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            summary TEXT NOT NULL,
            recommendations TEXT NOT NULL,
            refactored_code TEXT NOT NULL,
            security_issues TEXT NOT NULL,
            cost_optimizations TEXT NOT NULL,
            naming_issues TEXT NOT NULL,
            github_repo TEXT
        )
    ''')
    
    # Create github_connections table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS github_connections (
            id TEXT PRIMARY KEY,
            repo_url TEXT NOT NULL,
            access_token TEXT,
            last_analyzed TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Create feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            feedback_type TEXT NOT NULL,
            rating INTEGER,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT,
            metadata TEXT,
            created_at TEXT NOT NULL,
            status TEXT DEFAULT 'open'
        )
    ''')
    
    # Migrate existing tables if needed
    migrate_database(cursor)
    
    conn.commit()
    conn.close()

def migrate_database(cursor):
    """Migrate existing database schema if needed"""
    try:
        # Check if github_repo column exists in analyses table
        cursor.execute("PRAGMA table_info(analyses)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'github_repo' not in columns:
            print("Adding github_repo column to analyses table...")
            cursor.execute('ALTER TABLE analyses ADD COLUMN github_repo TEXT')
            print("Migration completed successfully!")
            
    except Exception as e:
        print(f"Migration error: {e}")
        # Continue anyway, the table might not exist yet

def save_analysis(analysis_result: Dict[str, Any], github_repo: str = None) -> str:
    """Save analysis result to database and return analysis ID"""
    analysis_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    conn = sqlite3.connect('inframorph.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO analyses (
            id, timestamp, summary, recommendations, refactored_code,
            security_issues, cost_optimizations, naming_issues, github_repo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        analysis_id,
        timestamp,
        analysis_result["summary"],
        json.dumps(analysis_result["recommendations"]),
        json.dumps(analysis_result["refactored_code"]),
        json.dumps(analysis_result["security_issues"]),
        json.dumps(analysis_result["cost_optimizations"]),
        json.dumps(analysis_result["naming_issues"]),
        github_repo
    ))
    
    conn.commit()
    conn.close()
    
    return analysis_id

def get_analysis(analysis_id: str) -> Dict[str, Any]:
    """Retrieve analysis result from database"""
    conn = sqlite3.connect('inframorph.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM analyses WHERE id = ?
    ''', (analysis_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return None
    
    return {
        "analysis_id": result[0],
        "timestamp": result[1],
        "summary": result[2],
        "recommendations": json.loads(result[3]),
        "refactored_code": json.loads(result[4]),
        "security_issues": json.loads(result[5]),
        "cost_optimizations": json.loads(result[6]),
        "naming_issues": json.loads(result[7]),
        "github_repo": result[8] if len(result) > 8 else None
    }

def get_all_analyses() -> list:
    """Retrieve all analyses from database"""
    conn = sqlite3.connect('inframorph.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, timestamp, summary FROM analyses 
        ORDER BY timestamp DESC
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            "analysis_id": row[0],
            "timestamp": row[1],
            "summary": row[2]
        }
        for row in results
    ]

def delete_analysis(analysis_id: str) -> bool:
    """Delete analysis from database"""
    conn = sqlite3.connect('inframorph.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM analyses WHERE id = ?
    ''', (analysis_id,))
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted_count > 0

def save_github_connection(repo_url: str, access_token: str = None) -> str:
    """Save GitHub repository connection"""
    connection_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    
    conn = sqlite3.connect('inframorph.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO github_connections (
            id, repo_url, access_token, created_at
        ) VALUES (?, ?, ?, ?)
    ''', (connection_id, repo_url, access_token, created_at))
    
    conn.commit()
    conn.close()
    
    return connection_id

def save_feedback(feedback_data: Dict[str, Any]) -> int:
    """Save user feedback to database"""
    conn = sqlite3.connect('inframorph.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO feedback (
            user_id, feedback_type, rating, title, description, 
            category, metadata, created_at, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        feedback_data["user_id"],
        feedback_data["feedback_type"],
        feedback_data.get("rating"),
        feedback_data["title"],
        feedback_data["description"],
        feedback_data.get("category"),
        json.dumps(feedback_data.get("metadata", {})),
        datetime.now().isoformat(),
        "open"
    ))
    
    feedback_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return feedback_id

def get_feedback_by_user(user_id: int) -> list:
    """Get all feedback from a specific user"""
    conn = sqlite3.connect('inframorph.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM feedback WHERE user_id = ? ORDER BY created_at DESC
    ''', (user_id,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "user_id": row[1],
            "feedback_type": row[2],
            "rating": row[3],
            "title": row[4],
            "description": row[5],
            "category": row[6],
            "metadata": json.loads(row[7]) if row[7] else {},
            "created_at": row[8],
            "status": row[9]
        }
        for row in results
    ]

def get_all_feedback() -> list:
    """Get all feedback (for admin purposes)"""
    conn = sqlite3.connect('inframorph.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM feedback ORDER BY created_at DESC
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": row[0],
            "user_id": row[1],
            "feedback_type": row[2],
            "rating": row[3],
            "title": row[4],
            "description": row[5],
            "category": row[6],
            "metadata": json.loads(row[7]) if row[7] else {},
            "created_at": row[8],
            "status": row[9]
        }
        for row in results
    ] 