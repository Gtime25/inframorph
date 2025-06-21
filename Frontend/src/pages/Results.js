import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
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
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import axios from 'axios';

const Results = () => {
  const { analysisId } = useParams();
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('summary');
  const [showOriginal, setShowOriginal] = useState({});

  useEffect(() => {
    fetchResults();
  }, [analysisId]);

  const fetchResults = async () => {
    try {
      const response = await axios.get(`/analysis/${analysisId}`);
      setResults(response.data);
    } catch (error) {
      console.error('Error fetching results:', error);
      toast.error('Failed to load analysis results.');
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority.toLowerCase()) {
      case 'high':
        return 'text-danger-600 bg-danger-100';
      case 'medium':
        return 'text-warning-600 bg-warning-100';
      case 'low':
        return 'text-success-600 bg-success-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return 'text-danger-600 bg-danger-100';
      case 'medium':
        return 'text-warning-600 bg-warning-100';
      case 'low':
        return 'text-success-600 bg-success-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Results Not Found</h2>
        <p className="text-gray-600 mb-4">The analysis results could not be loaded.</p>
        <button
          onClick={() => navigate('/analysis')}
          className="btn-primary inline-flex items-center"
        >
          <ArrowLeftIcon className="w-5 h-5 mr-2" />
          Start New Analysis
        </button>
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
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analysis Results</h1>
          <p className="text-gray-600">Analysis ID: {analysisId}</p>
        </div>
        <button
          onClick={() => navigate('/analysis')}
          className="btn-secondary inline-flex items-center"
        >
          <ArrowLeftIcon className="w-5 h-5 mr-2" />
          New Analysis
        </button>
      </div>

      {/* Summary Card */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Analysis Summary</h2>
        <p className="text-gray-700 leading-relaxed">{results.summary}</p>
        <div className="mt-4 text-sm text-gray-500">
          Completed: {new Date(results.timestamp).toLocaleString()}
        </div>
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
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
        <div className="mt-6">
          {activeTab === 'summary' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-primary-50 rounded-lg">
                  <div className="text-2xl font-bold text-primary-600">
                    {results.recommendations?.length || 0}
                  </div>
                  <div className="text-sm text-gray-600">Recommendations</div>
                </div>
                <div className="text-center p-4 bg-danger-50 rounded-lg">
                  <div className="text-2xl font-bold text-danger-600">
                    {results.security_issues?.length || 0}
                  </div>
                  <div className="text-sm text-gray-600">Security Issues</div>
                </div>
                <div className="text-center p-4 bg-warning-50 rounded-lg">
                  <div className="text-2xl font-bold text-warning-600">
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
                    <span className={`badge ${getPriorityColor(rec.priority)}`}>
                      {rec.priority}
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
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">{issue.title}</h3>
                    <span className={`badge ${getSeverityColor(issue.severity)}`}>
                      {issue.severity}
                    </span>
                  </div>
                  <p className="text-gray-700 mb-2">{issue.description}</p>
                  <div className="text-sm text-gray-600 mb-2">
                    <strong>File:</strong> {issue.file_path}
                    {issue.line_number && ` (Line ${issue.line_number})`}
                  </div>
                  <div className="text-sm text-gray-700">
                    <strong>Recommendation:</strong> {issue.recommendation}
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'cost' && (
            <div className="space-y-4">
              {results.cost_optimizations?.map((opt, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">{opt.resource_type}</h3>
                    {opt.potential_savings && (
                      <span className="badge badge-success">{opt.potential_savings}</span>
                    )}
                  </div>
                  <p className="text-gray-700 mb-2">{opt.recommendation}</p>
                  <div className="text-sm text-gray-600">
                    <strong>File:</strong> {opt.file_path}
                    {opt.current_cost && (
                      <span className="ml-4">
                        <strong>Current Cost:</strong> {opt.current_cost}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'naming' && (
            <div className="space-y-4">
              {results.naming_issues?.map((issue, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">{issue.issue_type}</h3>
                    <span className="badge badge-info">{issue.current_name}</span>
                  </div>
                  <p className="text-gray-700 mb-2">{issue.reason}</p>
                  <div className="text-sm text-gray-600 mb-2">
                    <strong>File:</strong> {issue.file_path}
                  </div>
                  <div className="text-sm text-gray-700">
                    <strong>Suggested:</strong> {issue.suggested_name}
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'refactored' && (
            <div className="space-y-6">
              {results.refactored_code?.map((code, index) => (
                <div key={index} className="border border-gray-200 rounded-lg">
                  <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
                    <h3 className="font-semibold text-gray-900">{code.file_path}</h3>
                    <p className="text-sm text-gray-600 mt-1">{code.changes_summary}</p>
                  </div>
                  <div className="p-4">
                    <div className="mb-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-900">Original Code</h4>
                        <button
                          onClick={() => setShowOriginal({ ...showOriginal, [index]: !showOriginal[index] })}
                          className="text-sm text-primary-600 hover:text-primary-700 flex items-center"
                        >
                          {showOriginal[index] ? (
                            <>
                              <EyeSlashIcon className="w-4 h-4 mr-1" />
                              Hide
                            </>
                          ) : (
                            <>
                              <EyeIcon className="w-4 h-4 mr-1" />
                              Show
                            </>
                          )}
                        </button>
                      </div>
                      {showOriginal[index] && (
                        <SyntaxHighlighter
                          language="hcl"
                          style={tomorrow}
                          className="rounded-lg"
                        >
                          {code.original_content}
                        </SyntaxHighlighter>
                      )}
                    </div>
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Refactored Code</h4>
                      <SyntaxHighlighter
                        language="hcl"
                        style={tomorrow}
                        className="rounded-lg"
                      >
                        {code.refactored_content}
                      </SyntaxHighlighter>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Results; 