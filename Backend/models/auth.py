import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key-change-in-production"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

class User(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    created_at: str
    is_active: bool = True

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class TokenData(BaseModel):
    username: Optional[str] = None

def init_auth_db():
    """Initialize the authentication database tables"""
    conn = sqlite3.connect('inframorph.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            hashed_password TEXT NOT NULL,
            created_at TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    conn.commit()
    conn.close()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None

def get_user_by_username(username: str) -> Optional[User]:
    """Get a user by username"""
    conn = sqlite3.connect('inframorph.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, username, email, created_at, is_active 
        FROM users WHERE username = ?
    """, (username,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return User(
            id=result[0],
            username=result[1],
            email=result[2],
            created_at=result[3],
            is_active=result[4]
        )
    return None

def get_user_by_id(user_id: str) -> Optional[User]:
    """Get a user by ID"""
    conn = sqlite3.connect('inframorph.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, username, email, created_at, is_active 
        FROM users WHERE id = ?
    """, (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return User(
            id=result[0],
            username=result[1],
            email=result[2],
            created_at=result[3],
            is_active=result[4]
        )
    return None

def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate a user with username and password"""
    conn = sqlite3.connect('inframorph.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, username, email, hashed_password, created_at, is_active 
        FROM users WHERE username = ?
    """, (username,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return None
    
    user_id, username, email, hashed_password, created_at, is_active = result
    
    if not verify_password(password, hashed_password):
        return None
    
    return User(
        id=user_id,
        username=username,
        email=email,
        created_at=created_at,
        is_active=is_active
    )

def create_user(username: str, password: str, email: Optional[str] = None) -> Optional[User]:
    """Create a new user"""
    try:
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(password)
        created_at = datetime.now().isoformat()
        
        conn = sqlite3.connect('inframorph.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (id, username, email, hashed_password, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, email, hashed_password, created_at))
        
        conn.commit()
        conn.close()
        
        return User(
            id=user_id,
            username=username,
            email=email,
            created_at=created_at,
            is_active=True
        )
    except sqlite3.IntegrityError:
        # Username already exists
        return None

def username_exists(username: str) -> bool:
    """Check if a username already exists"""
    conn = sqlite3.connect('inframorph.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    return result is not None 