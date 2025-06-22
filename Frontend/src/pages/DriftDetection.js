import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { 
  CloudIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  DocumentTextIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline';

const DriftDetection = ({ user, token }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [cloudProvider, setCloudProvider] = useState('aws');
  const [isDetecting, setIsDetecting] = useState(false);
  const [driftResults, setDriftResults] = useState(null);
  const navigate = useNavigate();

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    setSelectedFiles(files);
  };

  const handleDetectDrift = async (e) => {
    e.preventDefault();
    
    if (selectedFiles.length === 0) {
      toast.error('Please select Terraform files to analyze');
      return;
    }

    setIsDetecting(true);
    
    try {
      const formData = new FormData();
      
      // Add files
      selectedFiles.forEach(file => {
        formData.append('files', file);
      });
      
      // Add cloud provider
      formData.append('cloud_provider', cloudProvider);

      const response = await fetch('http://localhost:8000/drift/detect', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Drift detection failed');
      }

      const data = await response.json();
      setDriftResults(data);
      
      if (data.drift_results.drift_detected) {
        toast.error(`Drift detected! Found ${data.drift_results.drifted_resources} drifted resources`);
      } else {
        toast.success('No infrastructure drift detected!');
      }
      
    } catch (error) {
      console.error('Drift detection error:', error);
      toast.error(error.message || 'Drift detection failed. Please try again.');
    } finally {
      setIsDetecting(false);
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

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-6xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Infrastructure Drift Detection</h1>
            <p className="text-gray-600">
              Detect differences between your Terraform code and deployed infrastructure
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
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload Terraform Files</h2>
          
          <form onSubmit={handleDetectDrift} className="space-y-6">
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
              <p className="text-sm text-gray-500 mt-1">
                Select the cloud provider where your infrastructure is deployed
              </p>
            </div>

            {/* File Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Terraform Files
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <input
                  type="file"
                  multiple
                  accept=".tf,.tfvars,.hcl"
                  onChange={handleFileSelect}
                  className="hidden"
                  id="file-upload"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  <CloudIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <p className="mt-2 text-sm text-gray-600">
                    Click to upload Terraform files
                  </p>
                  <p className="text-xs text-gray-500">
                    Supports .tf, .tfvars, and .hcl files
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
              disabled={isDetecting || selectedFiles.length === 0}
              className="w-full inline-flex justify-center items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isDetecting ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Detecting Drift...
                </>
              ) : (
                <>
                  <ExclamationTriangleIcon className="w-5 h-5 mr-2" />
                  Detect Infrastructure Drift
                </>
              )}
            </button>
          </form>
        </div>

        {/* Drift Results */}
        {driftResults && (
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Drift Detection Results</h2>
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500">
                  {driftResults.cloud_provider.toUpperCase()}
                </span>
                <span className="text-sm text-gray-500">
                  {new Date(driftResults.timestamp).toLocaleString()}
                </span>
              </div>
            </div>

            {/* Summary */}
            <div className="mb-6">
              {driftResults.drift_results.drift_detected ? (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <ExclamationTriangleIcon className="w-6 h-6 text-red-600 mr-3" />
                    <div>
                      <h3 className="text-lg font-semibold text-red-900">
                        Infrastructure Drift Detected!
                      </h3>
                      <p className="text-red-700">
                        {driftResults.drift_results.drift_summary}
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center">
                    <CheckCircleIcon className="w-6 h-6 text-green-600 mr-3" />
                    <div>
                      <h3 className="text-lg font-semibold text-green-900">
                        No Drift Detected
                      </h3>
                      <p className="text-green-700">
                        Your infrastructure matches your Terraform code perfectly!
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {driftResults.drift_results.total_resources || 0}
                </div>
                <div className="text-sm text-gray-600">Total Resources</div>
              </div>
              <div className="text-center p-4 bg-red-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">
                  {driftResults.drift_results.drifted_resources || 0}
                </div>
                <div className="text-sm text-gray-600">Drifted Resources</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-600">
                  {driftResults.drift_results.resources?.length || 0}
                </div>
                <div className="text-sm text-gray-600">Issues Found</div>
              </div>
            </div>

            {/* Detailed Results */}
            {driftResults.drift_results.resources && driftResults.drift_results.resources.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Drift Details</h3>
                <div className="space-y-4">
                  {driftResults.drift_results.resources.map((resource, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-semibold text-gray-900">
                          {resource.resource_type.replace('_', ' ').toUpperCase()}
                        </h4>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getSeverityColor(resource.severity)}`}>
                          {resource.severity}
                        </span>
                      </div>
                      <p className="text-gray-700 mb-2">{resource.description}</p>
                      <div className="text-sm text-gray-600">
                        <strong>Resource ID:</strong> {resource.resource_id}
                      </div>
                      <div className="text-sm text-gray-600 mt-1">
                        <strong>Recommendation:</strong> {resource.recommendation}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Drift Report */}
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Detailed Report</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                  {driftResults.drift_report}
                </pre>
              </div>
            </div>
          </div>
        )}

        {/* Info Section */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">How Drift Detection Works</h3>
          <ul className="text-blue-800 space-y-1">
            <li>• Upload your Terraform files to analyze your infrastructure code</li>
            <li>• InfraMorph connects to your cloud provider to check deployed resources</li>
            <li>• Compares code definitions with actual infrastructure state</li>
            <li>• Identifies resources that exist in cloud but not in code (unmanaged)</li>
            <li>• Provides recommendations for resolving drift issues</li>
            <li>• Helps maintain infrastructure as code best practices</li>
          </ul>
        </div>
      </main>
    </div>
  );
};

export default DriftDetection; 