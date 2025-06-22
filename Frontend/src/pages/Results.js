import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { 
  ShieldCheckIcon,
  CurrencyDollarIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  CodeBracketIcon,
  ArrowLeftIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';

const Results = ({ user, token }) => {
  const { analysisId } = useParams();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('summary');
  const [showOriginal, setShowOriginal] = useState({});
  const [creatingPRs, setCreatingPRs] = useState(false);
  const [prsCreated, setPrsCreated] = useState(null);
  const [githubStatus, setGithubStatus] = useState(null);

  useEffect(() => {
    fetchResults();
    checkGitHubStatus();
  }, [analysisId]);

  const checkGitHubStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/github/status', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setGithubStatus(data);
      }
    } catch (error) {
      console.error('Error checking GitHub status:', error);
    }
  };

  const fetchResults = async () => {
    try {
      const response = await fetch(`http://localhost:8000/analysis/${analysisId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load analysis results');
      }

      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error fetching results:', error);
      toast.error('Failed to load analysis results.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePRs = async (createSeparate = true) => {
    if (!results) {
      toast.error('No analysis results available');
      return;
    }

    // Check if GitHub is configured first
    if (!githubStatus?.configured) {
      toast.error('GitHub is not configured. Please set up GitHub integration first.');
      return;
    }

    setCreatingPRs(true);
    
    try {
      const formData = new FormData();
      formData.append('analysis_id', analysisId);
      formData.append('repo_url', results.github_repo || '');
      formData.append('create_separate_prs', createSeparate);

      const response = await fetch('http://localhost:8000/github/create-automated-prs', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        let errorMessage = 'Failed to create pull requests';
        try {
          const errorData = await response.json();
          // Handle different types of error responses
          if (typeof errorData === 'object') {
            errorMessage = errorData.detail || errorData.message || errorData.error || 'GitHub configuration error';
          } else {
            errorMessage = String(errorData);
          }
        } catch (parseError) {
          // If we can't parse the error as JSON, try to get the text
          try {
            const errorText = await response.text();
            errorMessage = errorText || 'GitHub configuration error';
          } catch (textError) {
            console.error('Could not parse error response:', textError);
            errorMessage = 'GitHub configuration error. Please check your GitHub setup.';
          }
        }
        
        // Provide specific error messages for common issues
        if (errorMessage.includes('configuration') || errorMessage.includes('token')) {
          errorMessage = 'GitHub is not properly configured. Please set up your GitHub token in the environment.';
        } else if (errorMessage.includes('repository') || errorMessage.includes('repo') || errorMessage.includes('URL')) {
          errorMessage = 'Repository URL is required. Please provide a valid GitHub repository URL or connect a repository first.';
        } else if (response.status === 422) {
          errorMessage = 'Invalid request. Please check that all required fields are provided correctly.';
        }
        
        throw new Error(errorMessage);
      }

      const data = await response.json();
      setPrsCreated(data);
      toast.success(`Successfully created ${data.pull_requests.length} pull request(s)!`);
      
    } catch (error) {
      console.error('Error creating PRs:', error);
      const errorMessage = error.message || 'Failed to create pull requests. Please check your GitHub configuration.';
      toast.error(errorMessage);
    } finally {
      setCreatingPRs(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return 'text-red-600 bg-red-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'low':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'high':
        return 'text-red-600 bg-red-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'low':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Results Not Found</h2>
          <p className="text-gray-600 mb-4">The analysis results could not be loaded.</p>
          <button
            onClick={() => navigate('/analysis')}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <ArrowLeftIcon className="w-5 h-5 mr-2" />
            Start New Analysis
          </button>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'summary', name: 'Summary', icon: DocumentTextIcon },
    { id: 'recommendations', name: 'Recommendations', icon: CheckCircleIcon },
    { id: 'security', name: 'Security Issues', icon: ShieldCheckIcon },
    { id: 'cost', name: 'Cost Optimizations', icon: CurrencyDollarIcon },
    { id: 'naming', name: 'Naming Issues', icon: ExclamationTriangleIcon },
    { id: 'refactored', name: 'Refactored Code', icon: CodeBracketIcon },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-6xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analysis Results</h1>
            <p className="text-gray-600">Analysis ID: {analysisId}</p>
          </div>
          <div className="flex space-x-3">
            {githubStatus?.configured ? (
              <>
                <button
                  onClick={() => handleCreatePRs(true)}
                  disabled={creatingPRs}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {creatingPRs ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Creating PRs...
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                      </svg>
                      Create PRs
                    </>
                  )}
                </button>
                <button
                  onClick={() => handleCreatePRs(false)}
                  disabled={creatingPRs}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {creatingPRs ? 'Creating...' : 'Create Single PR'}
                </button>
                {!results.github_repo && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-2">
                    <p className="text-xs text-blue-700">
                      💡 <strong>Tip:</strong> No repository URL found. You'll need to provide one when creating PRs.
                    </p>
                  </div>
                )}
              </>
            ) : (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <div className="flex items-center">
                  <svg className="w-5 h-5 text-yellow-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <p className="text-sm text-yellow-800">
                      <strong>GitHub not configured.</strong> To create pull requests, set up your GitHub token in the environment variables.
                    </p>
                    <div className="flex items-center space-x-2 mt-1">
                      <p className="text-xs text-yellow-600">
                        Add GITHUB_TOKEN to your .env file to enable GitHub integration.
                      </p>
                      <Link
                        to="/github-connect"
                        className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                      >
                        Setup GitHub →
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <button
              onClick={() => navigate('/analysis')}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <ArrowLeftIcon className="w-5 h-5 mr-2" />
              New Analysis
            </button>
          </div>
        </div>

        {/* PR Creation Results */}
        {prsCreated && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
            <h3 className="text-lg font-semibold text-green-900 mb-4">
              ✅ Pull Requests Created Successfully!
            </h3>
            <div className="space-y-3">
              {prsCreated.pull_requests.map((pr, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-white rounded-lg border border-green-200">
                  <div>
                    <h4 className="font-medium text-green-900">{pr.title}</h4>
                    <p className="text-sm text-green-700">
                      Category: {pr.category} | Priority: {pr.priority} | Changes: {pr.changes_count}
                    </p>
                  </div>
                  <a
                    href={pr.pr_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-green-700 bg-green-100 hover:bg-green-200"
                  >
                    View PR
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Summary Card */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Analysis Summary</h2>
          <p className="text-gray-700 leading-relaxed">{results.summary}</p>
          <div className="mt-4 text-sm text-gray-500">
            Completed: {new Date(results.timestamp).toLocaleString()}
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white shadow rounded-lg">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  <span>{tab.name}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'summary' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {results.recommendations?.length || 0}
                    </div>
                    <div className="text-sm text-gray-600">Recommendations</div>
                  </div>
                  <div className="text-center p-4 bg-red-50 rounded-lg">
                    <div className="text-2xl font-bold text-red-600">
                      {results.security_issues?.length || 0}
                    </div>
                    <div className="text-sm text-gray-600">Security Issues</div>
                  </div>
                  <div className="text-center p-4 bg-yellow-50 rounded-lg">
                    <div className="text-2xl font-bold text-yellow-600">
                      {results.cost_optimizations?.length || 0}
                    </div>
                    <div className="text-sm text-gray-600">Cost Optimizations</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-gray-600">
                      {results.naming_issues?.length || 0}
                    </div>
                    <div className="text-sm text-gray-600">Naming Issues</div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'recommendations' && (
              <div className="space-y-4">
                {results.recommendations?.map((rec, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold text-gray-900">{rec.title}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(rec.priority)}`}>
                        {rec.priority || 'Medium'}
                      </span>
                    </div>
                    <p className="text-gray-700 mb-2">{rec.description}</p>
                    <div className="text-sm text-gray-600">
                      <strong>Impact:</strong> {rec.impact}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'security' && (
              <div className="space-y-4">
                {results.security_issues?.map((issue, index) => (
                  <div key={index} className="border border-red-200 rounded-lg p-4 bg-red-50">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold text-red-900">{issue.title}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getSeverityColor(issue.severity)}`}>
                        {issue.severity}
                      </span>
                    </div>
                    <p className="text-red-800 mb-2">{issue.description}</p>
                    <div className="text-sm text-red-800">
                      <strong>Recommendation:</strong> {issue.recommendation}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'cost' && (
              <div className="space-y-4">
                {results.cost_optimizations?.map((opt, index) => (
                  <div key={index} className="border border-yellow-200 rounded-lg p-4 bg-yellow-50">
                    <h3 className="font-semibold text-yellow-900 mb-2">{opt.resource_type}</h3>
                    <div className="text-sm text-yellow-800">
                      <strong>Current Cost:</strong> {opt.current_cost || 'Not specified'}
                    </div>
                    <div className="text-sm text-yellow-800 mt-1">
                      <strong>Potential Savings:</strong> {opt.potential_savings}
                    </div>
                    <div className="text-sm text-yellow-800 mt-1">
                      <strong>Recommendation:</strong> {opt.recommendation}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'naming' && (
              <div className="space-y-4">
                {results.naming_issues?.map((issue, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <h3 className="font-semibold text-gray-900 mb-2">{issue.issue_type}</h3>
                    <div className="text-sm text-gray-600 space-y-1">
                      <div><strong>Current:</strong> <code className="bg-gray-100 px-1 rounded">{issue.current_name}</code></div>
                      <div><strong>Suggested:</strong> <code className="bg-green-100 px-1 rounded">{issue.suggested_name}</code></div>
                      <div><strong>Reason:</strong> {issue.reason}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'refactored' && (
              <div className="space-y-4">
                {results.refactored_code?.map((code, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg">
                    <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
                      <h3 className="font-semibold text-gray-900">{code.file_path}</h3>
                      <p className="text-sm text-gray-600 mt-1">{code.changes_summary}</p>
                    </div>
                    <div className="p-4">
                      <h4 className="font-medium text-gray-900 mb-2">Refactored Code:</h4>
                      <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm">
                        <code>{code.refactored_content}</code>
                      </pre>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default Results; 