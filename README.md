# InfraMorph - AI-Powered Infrastructure Optimization

InfraMorph is an AI-powered infrastructure optimization tool for DevOps engineers. It analyzes Terraform and Ansible code to identify unused resources, security misconfigurations, inconsistent naming, and cost-saving opportunities, then generates AI-refactored code snippets and GitHub pull requests.

## Features

- 🔐 **User Authentication**: Secure login/signup system with JWT tokens
- 🤖 **AI-Powered Analysis**: Uses OpenAI GPT-4 for intelligent infrastructure analysis
- 🔒 **Security Scanning**: Identifies security vulnerabilities and misconfigurations
- 💰 **Cost Optimization**: Finds opportunities to reduce cloud infrastructure costs
- 📝 **Code Quality**: Analyzes naming conventions and best practices
- 🔄 **Auto Refactoring**: Generates improved code with suggested changes
- 🔗 **GitHub Integration**: Connect repositories and create pull requests
- 📊 **Comprehensive Reports**: Detailed analysis with actionable recommendations

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLite**: Lightweight database for user data and analysis history
- **OpenAI GPT-4**: AI analysis engine
- **JWT**: Secure authentication tokens
- **bcrypt**: Password hashing
- **PyGithub**: GitHub API integration

### Frontend
- **React**: Modern JavaScript framework
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **React Dropzone**: File upload functionality
- **React Hot Toast**: Toast notifications

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key (optional - will use mock data if not provided)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd Backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key (optional)
   ```

5. **Start the backend server:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd Frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

4. **Open your browser:**
   Navigate to `http://localhost:3000`

## Authentication System

InfraMorph now includes a complete authentication system:

### Features
- **User Registration**: Create new accounts with username/password
- **User Login**: Secure authentication with JWT tokens
- **Protected Routes**: All analysis features require authentication
- **Session Management**: Automatic token refresh and logout
- **Password Security**: Bcrypt hashing for secure password storage

### How to Use

1. **First Time Users:**
   - Navigate to the signup page
   - Create a username and password
   - Optionally provide an email address
   - You'll be automatically logged in after signup

2. **Returning Users:**
   - Use your username and password to log in
   - Your session will be maintained across browser sessions
   - Use the logout button to end your session

3. **Protected Features:**
   - File analysis requires authentication
   - GitHub integration requires authentication
   - All analysis history is tied to your user account

## API Endpoints

### Authentication
- `POST /auth/signup` - Create new user account
- `POST /auth/login` - Authenticate user
- `GET /auth/me` - Get current user info

### Analysis
- `POST /analyze` - Analyze uploaded IaC files (requires auth)
- `GET /analysis/{id}` - Get specific analysis results (requires auth)

### GitHub Integration
- `POST /github/connect` - Connect to GitHub repository (requires auth)
- `POST /github/create-pr` - Create pull request (requires auth)

## Environment Variables

Create a `.env` file in the Backend directory:

```env
# OpenAI API (optional - will use mock data if not provided)
OPENAI_API_KEY=your_openai_api_key_here

# GitHub Personal Access Token (optional)
GITHUB_TOKEN=your_github_token_here

# JWT Secret (change in production!)
JWT_SECRET_KEY=your-secret-key-change-in-production
```

## Usage

1. **Sign up or log in** to your account
2. **Upload Terraform/Ansible files** or connect a GitHub repository
3. **Choose analysis type**: Comprehensive, Security, or Cost-focused
4. **Review AI-generated recommendations** for security, cost, and best practices
5. **Apply suggested improvements** or create GitHub pull requests

## Sample Infrastructure File

A sample Terraform file with various issues is included as `sample_infrastructure.tf` for testing the analysis features.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub. 