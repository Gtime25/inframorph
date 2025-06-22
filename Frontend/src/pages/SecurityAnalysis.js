import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { 
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  DocumentTextIcon,
  ArrowLeftIcon,
  LockClosedIcon
} from '@heroicons/react/24/outline';

const SecurityAnalysis = ({ user, token }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [cloudProvider, setCloudProvider] = useState('aws');
  const [complianceFrameworks, setComplianceFrameworks] = useState(['cis', 'pci']);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [securityResults, setSecurityResults] = useState(null);
  const navigate = useNavigate();

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    setSelectedFiles(files);
  };

  const handleFrameworkChange = (framework) => {
    setComplianceFrameworks(prev => {
      if (prev.includes(framework)) {
        return prev.filter(f => f !== framework);
      } else {
        return [...prev, framework];
      }
    });
  };

  const handleSecurityAnalysis = async (e) => {
    e.preventDefault();
    
    if (selectedFiles.length === 0) {
      toast.error('Please select files to analyze');
      return;
    }

    setIsAnalyzing(true);
    
    try {
      const formData = new FormData();
      
      // Add files
      selectedFiles.forEach(file => {
        formData.append('files', file);
      });
      
      // Add parameters
      formData.append('cloud_provider', cloudProvider);
      formData.append('compliance_frameworks', complianceFrameworks.join(','));

      const response = await fetch('http://localhost:8000/security/analyze', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Security analysis failed');
      }

      const data = await response.json();
      setSecurityResults(data);
      
      const score = data.security_results.overall_security_score;
      if (score >= 80) {
        toast.success(`Security analysis complete! Score: ${score}/100`);
      } else if (score >= 60) {
        toast.warning(`Security analysis complete! Score: ${score}/100 - Some issues found`);
      } else {
        toast.error(`Security analysis complete! Score: ${score}/100 - Critical issues found`);
      }
      
    } catch (error) {
      console.error('Security analysis error:', error);
      toast.error(error.message || 'Security analysis failed. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'text-red-600 bg-red-100';
      case 'high':
        return 'text-orange-600 bg-orange-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'low':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-6xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Security Analysis</h1>
            <p className="text-gray-600">
              Comprehensive security analysis with compliance framework checking
            </p>
          </div>
          <button
            onClick={() => navigate('/dashboard')}
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            <ArrowLeftIcon className="w-5 h-5 mr-2" />
            Back to Dashboard
          </button>
        </div>

        {/* Upload Form */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload Infrastructure Files</h2>
          
          <form onSubmit={handleSecurityAnalysis} className="space-y-6">
            {/* Cloud Provider Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Cloud Provider
              </label>
              <select
                value={cloudProvider}
                onChange={(e) => setCloudProvider(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="aws">AWS</option>
                <option value="azure">Azure</option>
                <option value="gcp">Google Cloud Platform</option>
              </select>
            </div>

            {/* Compliance Frameworks */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Compliance Frameworks
              </label>
              <div className="space-y-2">
                {[
                  { id: 'cis', name: 'CIS Benchmarks', description: 'Center for Internet Security benchmarks' },
                  { id: 'pci', name: 'PCI DSS', description: 'Payment Card Industry Data Security Standard' },
                  { id: 'hipaa', name: 'HIPAA', description: 'Health Insurance Portability and Accountability Act' }
                ].map(framework => (
                  <label key={framework.id} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={complianceFrameworks.includes(framework.id)}
                      onChange={() => handleFrameworkChange(framework.id)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <div className="ml-3">
                      <div className="text-sm font-medium text-gray-900">{framework.name}</div>
                      <div className="text-sm text-gray-500">{framework.description}</div>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* File Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Infrastructure Files
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <input
                  type="file"
                  multiple
                  accept=".tf,.tfvars,.hcl,.yml,.yaml"
                  onChange={handleFileSelect}
                  className="hidden"
                  id="file-upload"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <ShieldCheckIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <p className="mt-2 text-sm text-gray-600">
                    Click to upload infrastructure files
                  </p>
                  <p className="text-xs text-gray-500">
                    Supports Terraform, Ansible, and YAML files
                  </p>
                </label>
              </div>
              
              {selectedFiles.length > 0 && (
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Selected Files:</h4>
                  <div className="space-y-1">
                    {selectedFiles.map((file, index) => (
                      <div key={index} className="flex items-center text-sm text-gray-600">
                        <DocumentTextIcon className="w-4 h-4 mr-2" />
                        {file.name} ({(file.size / 1024).toFixed(1)} KB)
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isAnalyzing || selectedFiles.length === 0}
              className="w-full inline-flex justify-center items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isAnalyzing ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Analyzing Security...
                </>
              ) : (
                <>
                  <LockClosedIcon className="w-5 h-5 mr-2" />
                  Analyze Security
                </>
              )}
            </button>
          </form>
        </div>

        {/* Security Results */}
        {securityResults && (
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Security Analysis Results</h2>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500">
                  {securityResults.cloud_provider.toUpperCase()}
                </span>
                <span className="text-sm text-gray-500">
                  {new Date(securityResults.timestamp).toLocaleString()}
                </span>
              </div>
            </div>

            {/* Security Score */}
            <div className="mb-6">
              <div className="text-center p-6 bg-gray-50 rounded-lg">
                <div className={`text-4xl font-bold ${getScoreColor(securityResults.security_results.overall_security_score)}`}>
                  {securityResults.security_results.overall_security_score}/100
                </div>
                <div className="text-lg text-gray-600 mt-2">Overall Security Score</div>
                {securityResults.security_results.overall_security_score >= 80 ? (
                  <div className="text-green-600 mt-2">✅ Good security posture</div>
                ) : securityResults.security_results.overall_security_score >= 60 ? (
                  <div className="text-yellow-600 mt-2">⚠️ Some security issues found</div>
                ) : (
                  <div className="text-red-600 mt-2">🚨 Critical security issues found</div>
                )}
              </div>
            </div>

            {/* Issue Summary */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">
                  {securityResults.security_results.critical_issues?.length || 0}
                </div>
                <div className="text-sm text-gray-600">Critical Issues</div>
              </div>
              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">
                  {securityResults.security_results.high_issues?.length || 0}
                </div>
                <div className="text-sm text-gray-600">High Issues</div>
              </div>
              <div className="text-center p-4 bg-yellow-50 rounded-lg">
                <div className="text-2xl font-bold text-yellow-600">
                  {securityResults.security_results.medium_issues?.length || 0}
                </div>
                <div className="text-sm text-gray-600">Medium Issues</div>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {securityResults.security_results.low_issues?.length || 0}
                </div>
                <div className="text-sm text-gray-600">Low Issues</div>
              </div>
            </div>

            {/* Critical Issues */}
            {securityResults.security_results.critical_issues && securityResults.security_results.critical_issues.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-red-900 mb-4 flex items-center">
                  <ExclamationTriangleIcon className="w-5 h-5 mr-2" />
                  Critical Security Issues
                </h3>
                <div className="space-y-4">
                  {securityResults.security_results.critical_issues.map((issue, index) => (
                    <div key={index} className="border border-red-200 rounded-lg p-4 bg-red-50">
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-semibold text-red-900">
                          {issue.file}:{issue.line}
                        </h4>
                        <span className="px-2 py-1 text-xs font-medium rounded-full text-red-600 bg-red-100">
                          Critical
                        </span>
                      </div>
                      <p className="text-red-800 mb-2">{issue.description}</p>
                      <div className="text-sm text-red-700">
                        <strong>Recommendation:</strong> {issue.recommendation}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* High Issues */}
            {securityResults.security_results.high_issues && securityResults.security_results.high_issues.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-orange-900 mb-4">High Priority Issues</h3>
                <div className="space-y-4">
                  {securityResults.security_results.high_issues.map((issue, index) => (
                    <div key={index} className="border border-orange-200 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-semibold text-gray-900">
                          {issue.file}:{issue.line}
                        </h4>
                        <span className="px-2 py-1 text-xs font-medium rounded-full text-orange-600 bg-orange-100">
                          High
                        </span>
                      </div>
                      <p className="text-gray-700 mb-2">{issue.description}</p>
                      <div className="text-sm text-gray-600">
                        <strong>Recommendation:</strong> {issue.recommendation}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Compliance Results */}
            {securityResults.security_results.compliance_results && Object.keys(securityResults.security_results.compliance_results).length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Compliance Analysis</h3>
                <div className="space-y-4">
                  {Object.entries(securityResults.security_results.compliance_results).map(([framework, compliance]) => (
                    <div key={framework} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-semibold text-gray-900">{compliance.name}</h4>
                        {compliance.overall_compliant ? (
                          <span className="px-2 py-1 text-xs font-medium rounded-full text-green-600 bg-green-100">
                            Compliant
                          </span>
                        ) : (
                          <span className="px-2 py-1 text-xs font-medium rounded-full text-red-600 bg-red-100">
                            Non-Compliant
                          </span>
                        )}
                      </div>
                      <div className="space-y-2">
                        {compliance.requirements.map((req, index) => (
                          <div key={index} className="flex items-center text-sm">
                            {req.compliant ? (
                              <CheckCircleIcon className="w-4 h-4 text-green-500 mr-2" />
                            ) : (
                              <ExclamationTriangleIcon className="w-4 h-4 text-red-500 mr-2" />
                            )}
                            <span className={req.compliant ? 'text-gray-600' : 'text-red-600'}>
                              {req.requirement}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations */}
            {securityResults.security_results.recommendations && securityResults.security_results.recommendations.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Security Recommendations</h3>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <ul className="space-y-2">
                    {securityResults.security_results.recommendations.map((rec, index) => (
                      <li key={index} className="text-blue-800 flex items-start">
                        <span className="mr-2">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {/* Detailed Report */}
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Detailed Security Report</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                  {securityResults.security_report}
                </pre>
              </div>
            </div>
          </div>
        )}

        {/* Info Section */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">Security Analysis Features</h3>
          <ul className="text-blue-800 space-y-1">
            <li>• Pattern-based security vulnerability detection</li>
            <li>• AI-powered security analysis and recommendations</li>
            <li>• Compliance framework checking (CIS, PCI DSS, HIPAA)</li>
            <li>• Security scoring and risk assessment</li>
            <li>• Detailed remediation recommendations</li>
            <li>• Multi-cloud security analysis support</li>
          </ul>
        </div>
      </main>
    </div>
  );
};

export default SecurityAnalysis; 