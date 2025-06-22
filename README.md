# InfraMorph - AI-Powered Infrastructure Optimization

InfraMorph is an intelligent infrastructure optimization platform that analyzes Terraform and Ansible code to identify security vulnerabilities, cost optimization opportunities, and best practice improvements, then generates automated pull requests with AI-refactored code.

## 🚀 Features

### Core Analysis
- **Security Analysis**: Detect vulnerabilities, misconfigurations, and compliance issues
- **Cost Optimization**: Identify resource sizing and efficiency improvements
- **Best Practices**: Architectural improvements and consistency checks
- **Naming Conventions**: Standardize resource naming and tagging

### Advanced Features
- **Automated PR Creation**: Generate categorized pull requests with improvements
- **GitHub Integration**: Connect repositories and analyze existing code
- **Multi-Cloud Support**: AWS, Azure, and GCP resource analysis
- **Drift Detection**: Compare code vs deployed infrastructure
- **Security Scoring**: Comprehensive security assessment with compliance frameworks

## 🛠️ Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- GitHub Personal Access Token
- OpenAI API Key

### Backend Setup
```bash
cd Backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your API keys
```

### Frontend Setup
```bash
cd Frontend
npm install
npm start
```

### Environment Variables
Create a `.env` file in the Backend directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
GITHUB_TOKEN=your_github_personal_access_token_here
SECRET_KEY=your_secret_key_here
```

## 📖 Usage Guide

### 1. Authentication
- Sign up with username and password
- No email verification required for pilot

### 2. Analysis Workflow
1. **Upload Files**: Upload Terraform/Ansible files directly
2. **Connect GitHub**: Or connect to existing GitHub repository
3. **Run Analysis**: AI analyzes code for issues and improvements
4. **Review Results**: View detailed analysis with recommendations
5. **Create PRs**: Generate automated pull requests with fixes

### 3. GitHub Integration
- Connect your repository for seamless analysis
- Automated PR creation with categorized improvements
- Support for both existing and new files

## 🔧 API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user info

### Analysis
- `POST /analyze` - Analyze IaC files
- `GET /analysis/{id}` - Get analysis results
- `GET /analyses` - List all analyses

### GitHub Integration
- `POST /github/connect` - Connect GitHub repository
- `POST /github/create-automated-prs` - Create pull requests
- `GET /github/status` - Check GitHub configuration

### Advanced Features
- `POST /drift/detect` - Detect infrastructure drift
- `POST /security/analyze` - Security analysis
- `GET /cloud/resources/{provider}` - Cloud resource discovery

## 🏗️ Architecture

### Backend (FastAPI)
- **Authentication**: JWT-based with bcrypt
- **Database**: SQLite with SQLAlchemy ORM
- **AI Integration**: OpenAI GPT-4 for analysis
- **GitHub API**: PyGithub for repository operations
- **Rate Limiting**: Built-in rate limiting middleware

### Frontend (React)
- **UI Framework**: React with Tailwind CSS
- **State Management**: React hooks and context
- **Routing**: React Router with protected routes
- **Notifications**: React Hot Toast for user feedback

## 🔒 Security Features

- JWT authentication with secure token storage
- Rate limiting to prevent abuse
- Input validation and sanitization
- Secure API key management
- CORS configuration for frontend-backend communication

## 📊 Pilot Metrics

Track these key metrics during pilot:
- **Analysis Success Rate**: % of successful analyses
- **PR Creation Rate**: % of analyses that generate PRs
- **User Engagement**: Time spent in analysis workflow
- **Issue Detection**: Number of issues found per analysis
- **User Feedback**: Satisfaction scores and feature requests

## 🐛 Troubleshooting

### Common Issues

1. **GitHub Token Issues**
   - Ensure token has `repo` and `workflow` scopes
   - Check token expiration (24-hour default)
   - Verify repository access permissions

2. **Analysis Failures**
   - Check OpenAI API key configuration
   - Verify file format (Terraform/Ansible)
   - Check file size limits

3. **PR Creation Issues**
   - Ensure repository exists and is accessible
   - Check branch permissions
   - Verify file paths in analysis results

### Debug Mode
Enable debug logging in backend console to see detailed error information.

## 🚀 Deployment

### Development
```bash
# Backend
cd Backend && python main.py

# Frontend  
cd Frontend && npm start
```

### Production (Recommended)
- Use production-grade database (PostgreSQL)
- Set up proper SSL/TLS certificates
- Configure environment variables securely
- Use reverse proxy (nginx) for frontend
- Set up monitoring and logging

## 📈 Roadmap

### Phase 2 Features (In Progress)
- [ ] Multi-cloud drift detection
- [ ] Advanced security compliance frameworks
- [ ] Cost estimation and forecasting
- [ ] Team collaboration features

### Phase 3 Features (Planned)
- [ ] CI/CD pipeline integration
- [ ] Custom rule engine
- [ ] Advanced reporting and analytics
- [ ] Enterprise SSO integration

## 🤝 Contributing

This is a pilot version. Feedback and bug reports are welcome!

## 📄 License

MIT License - see LICENSE file for details.

---

**InfraMorph** - Making infrastructure optimization intelligent and automated. 