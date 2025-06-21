import sqlite3
import json
import uuid
from datetime import datetime
from typing import Dict, Any
from models.schemas import AnalysisResult

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
            naming_issues TEXT NOT NULL
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
    
    conn.commit()
    conn.close()

def save_analysis(analysis_result: AnalysisResult) -> str:
    """Save analysis result to database and return analysis ID"""
    analysis_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    conn = sqlite3.connect('inframorph.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO analyses (
            id, timestamp, summary, recommendations, refactored_code,
            security_issues, cost_optimizations, naming_issues
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        analysis_id,
        timestamp,
        analysis_result.summary,
        json.dumps([rec.dict() for rec in analysis_result.recommendations]),
        json.dumps([code.dict() for code in analysis_result.refactored_code]),
        json.dumps([issue.dict() for issue in analysis_result.security_issues]),
        json.dumps([opt.dict() for opt in analysis_result.cost_optimizations]),
        json.dumps([issue.dict() for issue in analysis_result.naming_issues])
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
        "naming_issues": json.loads(result[7])
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