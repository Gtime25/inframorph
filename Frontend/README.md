# InfraMorph Frontend

Modern React frontend for the AI-powered infrastructure optimization tool.

## Features

- 🎨 **Modern UI**: Clean, responsive design built with Tailwind CSS
- 📁 **File Upload**: Drag & drop interface for IaC files
- 🔗 **GitHub Integration**: Connect to repositories and analyze files
- 📊 **Results Dashboard**: Comprehensive analysis results with tabs
- 💻 **Code Highlighting**: Syntax highlighting for Terraform and Ansible code
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile devices

## Tech Stack

- **React 18** - Modern React with hooks
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls
- **React Dropzone** - File upload component
- **React Hot Toast** - Toast notifications
- **React Syntax Highlighter** - Code syntax highlighting
- **Heroicons** - Beautiful SVG icons

## Setup

### Prerequisites

- Node.js 16+ and npm
- Backend API running on `http://localhost:8000`

### Installation

1. **Navigate to frontend directory**
   ```bash
   cd Frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000`

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

## Project Structure

```
Frontend/
├── public/                 # Static files
│   └── index.html         # Main HTML file
├── src/                   # Source code
│   ├── components/        # Reusable components
│   │   └── Header.js     # Navigation header
│   ├── pages/            # Page components
│   │   ├── Dashboard.js  # Home page
│   │   ├── Analysis.js   # File upload & analysis
│   │   ├── GitHubConnect.js # GitHub integration
│   │   └── Results.js    # Analysis results
│   ├── App.js            # Main app component
│   ├── index.js          # React entry point
│   └── index.css         # Global styles
├── package.json          # Dependencies and scripts
├── tailwind.config.js    # Tailwind configuration
└── postcss.config.js     # PostCSS configuration
```

## Pages

### Dashboard (`/`)
- Overview of InfraMorph features
- Quick action buttons
- Statistics and analytics
- Getting started guide

### Analysis (`/analysis`)
- File upload interface with drag & drop
- Analysis type selection (comprehensive, security, cost)
- Optional GitHub repository URL
- File validation and preview

### GitHub Connect (`/github`)
- Repository URL input
- Repository information display
- IaC file discovery
- Direct analysis from repository

### Results (`/results/:analysisId`)
- Comprehensive analysis results
- Tabbed interface for different result types
- Code comparison (original vs refactored)
- Security issues, cost optimizations, and recommendations

## Components

### Header
- Navigation menu
- Responsive design
- Active page highlighting

### File Upload
- Drag & drop interface
- File type validation
- Progress indicators
- File preview and removal

### Results Display
- Tabbed interface
- Syntax highlighting
- Priority/severity badges
- Code comparison tools

## Styling

The application uses Tailwind CSS with a custom color palette:

- **Primary**: Blue shades for main actions
- **Success**: Green shades for positive actions
- **Warning**: Yellow/Orange shades for warnings
- **Danger**: Red shades for errors and security issues

### Custom Components

The following custom CSS classes are available:

- `.btn-primary` - Primary button styling
- `.btn-secondary` - Secondary button styling
- `.btn-danger` - Danger button styling
- `.card` - Card container styling
- `.input-field` - Form input styling
- `.badge` - Badge component styling

## API Integration

The frontend communicates with the backend API through Axios. The API base URL is configured via the `proxy` field in `package.json`.

### Key API Endpoints

- `POST /analyze` - Upload and analyze IaC files
- `GET /analysis/{id}` - Get analysis results
- `POST /github/connect` - Connect to GitHub repository
- `POST /github/create-pr` - Create pull request

## Development

### Adding New Pages

1. Create a new component in `src/pages/`
2. Add the route to `src/App.js`
3. Add navigation link to `src/components/Header.js`

### Adding New Components

1. Create component file in `src/components/`
2. Export the component
3. Import and use in pages as needed

### Styling Guidelines

- Use Tailwind CSS utility classes
- Follow the established color scheme
- Maintain responsive design
- Use consistent spacing and typography

## Environment Variables

The frontend uses the following environment variables:

- `REACT_APP_API_URL` - Backend API URL (defaults to proxy)
- `REACT_APP_ENVIRONMENT` - Environment (development/production)

## Building for Production

1. **Build the application**
   ```bash
   npm run build
   ```

2. **Serve the build**
   ```bash
   npx serve -s build
   ```

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Ensure backend is running on port 8000
   - Check CORS configuration
   - Verify API endpoints

2. **File Upload Issues**
   - Check file size limits
   - Verify supported file types
   - Ensure proper file permissions

3. **Styling Issues**
   - Clear browser cache
   - Restart development server
   - Check Tailwind configuration

### Development Tips

- Use React Developer Tools for debugging
- Check browser console for errors
- Use Network tab to monitor API calls
- Test on different screen sizes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License. 