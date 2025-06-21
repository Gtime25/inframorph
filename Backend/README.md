# InfraMorph Backend

AI-powered infrastructure optimization tool backend built with FastAPI.

## Features

- 🔍 **IaC Analysis**: Analyze Terraform and Ansible files using AI
- 🔒 **Security Scanning**: Identify security vulnerabilities and misconfigurations
- 💰 **Cost Optimization**: Find opportunities to reduce cloud costs
- 🏷️ **Naming Consistency**: Check for naming conventions and consistency
- 🔗 **GitHub Integration**: Connect to repositories and create pull requests
- 📊 **Comprehensive Reports**: Generate detailed analysis reports

## Setup

### Prerequisites

- Python 3.8+
- Git
- OpenAI API key OR Anthropic API key
- GitHub Personal Access Token

### Installation

1. **Clone the repository**
   ```bash
   cd Backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

5. **Set up environment variables**
   - `OPENAI_API_KEY`: Your OpenAI API key (or use `ANTHROPIC_API_KEY`)
   - `GITHUB_TOKEN`: Your GitHub Personal Access Token

### Running the Application

1. **Start the server**
   ```bash
   python main.py
   ```

2. **Or use uvicorn directly**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## API Endpoints

### Core Analysis

- `POST /analyze` - Analyze uploaded IaC files
- `GET /analysis/{analysis_id}` - Get specific analysis results

### GitHub Integration

- `POST /github/connect` - Connect to GitHub repository
- `POST /github/create-pr` - Create pull request with changes

### Health & Status

- `GET /` - Root endpoint
- `GET /health` - Health check

## Usage Examples

### Analyze Uploaded Files

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@main.tf" \
  -F "files=@variables.tf" \
  -F "analysis_type=comprehensive"
```

### Connect to GitHub Repository

```bash
curl -X POST "http://localhost:8000/github/connect" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "repo_url=https://github.com/username/repo-name"
```

### Create Pull Request

```bash
curl -X POST "http://localhost:8000/github/create-pr" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "analysis_id=uuid-here&repo_url=https://github.com/username/repo-name&branch_name=optimization"
```

## Project Structure

```
Backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── env.example            # Environment variables template
├── models/                # Data models and schemas
│   ├── __init__.py
│   ├── schemas.py         # Pydantic schemas
│   └── database.py        # Database operations
└── services/              # Business logic services
    ├── __init__.py
    ├── iac_analyzer.py    # AI-powered IaC analysis
    └── github_service.py  # GitHub integration
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | Yes* |
| `ANTHROPIC_API_KEY` | Anthropic API key | Yes* |
| `GITHUB_TOKEN` | GitHub Personal Access Token | Yes |
| `DATABASE_URL` | Database connection string | No |
| `HOST` | Server host | No |
| `PORT` | Server port | No |

*Either OpenAI or Anthropic API key is required

### GitHub Token Permissions

Your GitHub Personal Access Token needs the following permissions:
- `repo` - Full control of private repositories
- `workflow` - Update GitHub Action workflows (optional)

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Code Formatting

```bash
# Install formatting tools
pip install black isort

# Format code
black .
isort .
```

### Database

The application uses SQLite by default. The database file (`inframorph.db`) will be created automatically on first run.

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure your API keys are correctly set in the `.env` file
   - Verify the API keys are valid and have sufficient credits

2. **GitHub Access Issues**
   - Check that your GitHub token has the required permissions
   - Ensure the repository is accessible with your token

3. **File Upload Issues**
   - Verify file extensions are supported (`.tf`, `.tfvars`, `.hcl`, `.yml`, `.yaml`, `.ansible`)
   - Check file size limits

### Logs

Enable debug logging by setting `DEBUG=true` in your `.env` file.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License. 