import React, { useState, useCallback, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import { 
  CloudArrowUpIcon,
  DocumentTextIcon,
  ShieldCheckIcon,
  CurrencyDollarIcon,
  CogIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';

const Analysis = ({ user, token }) => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [files, setFiles] = useState([]);
  const [analysisType, setAnalysisType] = useState('comprehensive');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [githubRepo, setGithubRepo] = useState('');
  const [loadingDemo, setLoadingDemo] = useState(false);

  // Check for demo parameter and load demo file
  useEffect(() => {
    const demoType = searchParams.get('demo');
    if (demoType && (demoType === 'aws' || demoType === 'azure')) {
      loadDemoFile(demoType);
    }
  }, [searchParams]);

  const loadDemoFile = async (demoType) => {
    setLoadingDemo(true);
    try {
      const response = await fetch(`http://localhost:8000/demo-files/${demoType}`);
      if (!response.ok) {
        throw new Error('Failed to load demo file');
      }
      
      const data = await response.json();
      
      // Create a File object from the demo content
      const demoFile = new File(
        [data.content], 
        data.filename, 
        { type: 'text/plain' }
      );
      
      setFiles([demoFile]);
      toast.success(`${demoType.toUpperCase()} demo file loaded successfully!`);
      
    } catch (error) {
      console.error('Error loading demo file:', error);
      toast.error('Failed to load demo file. Please try again.');
    } finally {
      setLoadingDemo(false);
    }
  };

  const onDrop = useCallback((acceptedFiles) => {
    const validFiles = acceptedFiles.filter(file => {
      const validExtensions = ['.tf', '.tfvars', '.hcl', '.yml', '.yaml', '.ansible'];
      const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      return validExtensions.includes(fileExtension);
    });

    if (validFiles.length !== acceptedFiles.length) {
      toast.error('Some files were skipped. Only .tf, .tfvars, .hcl, .yml, .yaml, and .ansible files are supported.');
    }

    setFiles(validFiles);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.tf', '.tfvars', '.hcl'],
      'application/x-yaml': ['.yml', '.yaml'],
      'text/x-yaml': ['.yml', '.yaml'],
      'text/ansible': ['.ansible']
    },
    multiple: true
  });

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const clearDemoFiles = () => {
    setFiles([]);
    toast.success('Demo files cleared. You can now upload your own files.');
  };

  const handleAnalyze = async () => {
    if (files.length === 0) {
      toast.error('Please upload at least one file to analyze.');
      return;
    }

    setIsAnalyzing(true);
    
    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });
      formData.append('analysis_type', analysisType);
      if (githubRepo) {
        formData.append('github_repo', githubRepo);
      }

      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const data = await response.json();
      toast.success('Analysis completed successfully!');
      navigate(`/results/${data.analysis_id}`);
      
    } catch (error) {
      console.error('Analysis error:', error);
      toast.error(error.message || 'Analysis failed. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const analysisTypes = [
    {
      id: 'comprehensive',
      name: 'Comprehensive',
      description: 'Full analysis including security, cost, and best practices',
      icon: CogIcon,
      color: 'bg-blue-500',
    },
    {
      id: 'security',
      name: 'Security Focus',
      description: 'Focus on security vulnerabilities and misconfigurations',
      icon: ShieldCheckIcon,
      color: 'bg-red-500',
    },
    {
      id: 'cost',
      name: 'Cost Optimization',
      description: 'Focus on cost reduction opportunities',
      icon: CurrencyDollarIcon,
      color: 'bg-yellow-500',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Analyze Infrastructure Code
          </h1>
          <p className="text-gray-600">
            Upload your Terraform or Ansible files to get AI-powered recommendations
          </p>
        </div>

        {/* File Upload */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload Files</h2>
          
          {loadingDemo ? (
            <div className="border-2 border-dashed border-blue-300 rounded-lg p-8 text-center bg-blue-50">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-blue-600 font-medium">Loading demo file...</p>
            </div>
          ) : (
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors duration-200 ${
                isDragActive
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
              }`}
            >
              <input {...getInputProps()} />
              <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              {isDragActive ? (
                <p className="text-blue-600 font-medium">Drop the files here...</p>
              ) : (
                <div>
                  <p className="text-gray-600 mb-2">
                    Drag & drop files here, or <span className="text-blue-600 font-medium">click to select</span>
                  </p>
                  <p className="text-sm text-gray-500">
                    Supports: .tf, .tfvars, .hcl, .yml, .yaml, .ansible
                  </p>
                </div>
              )}
            </div>
          )}

          {/* File List */}
          {files.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-medium text-gray-900 mb-3">Selected Files</h3>
              <div className="space-y-2">
                {files.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      <DocumentTextIcon className="w-5 h-5 text-gray-400" />
                      <div>
                        <div className="flex items-center space-x-2">
                          <p className="font-medium text-gray-900">{file.name}</p>
                          {file.name.includes('demo') && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              Demo File
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-500">
                          {(file.size / 1024).toFixed(1)} KB
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => removeFile(index)}
                      className="text-gray-400 hover:text-red-500 transition-colors duration-200"
                    >
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Demo File Info */}
        {files.length > 0 && files[0].name.includes('demo') && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex items-start justify-between">
              <div className="flex items-start">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-blue-800">
                    Demo File Loaded
                  </h3>
                  <div className="mt-2 text-sm text-blue-700">
                    <p>
                      This is a sample infrastructure file with common security, cost, and best practice issues. 
                      You can analyze it to see how InfraMorph identifies and suggests improvements for various problems.
                    </p>
                  </div>
                </div>
              </div>
              <button
                onClick={clearDemoFiles}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                Clear Demo Files
              </button>
            </div>
          </div>
        )}

        {/* Analysis Type Selection */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Analysis Type</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {analysisTypes.map((type) => (
              <label
                key={type.id}
                className={`relative cursor-pointer rounded-lg border-2 p-4 transition-all duration-200 ${
                  analysisType === type.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <input
                  type="radio"
                  name="analysisType"
                  value={type.id}
                  checked={analysisType === type.id}
                  onChange={(e) => setAnalysisType(e.target.value)}
                  className="sr-only"
                />
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded-lg ${type.color} text-white`}>
                    <type.icon className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{type.name}</h3>
                    <p className="text-sm text-gray-500">{type.description}</p>
                  </div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* GitHub Repository (Optional) */}
        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">GitHub Repository (Optional)</h2>
          <input
            type="text"
            placeholder="https://github.com/username/repository"
            value={githubRepo}
            onChange={(e) => setGithubRepo(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <p className="text-sm text-gray-500 mt-2">
            If provided, the analysis will include repository-specific context and recommendations.
          </p>
        </div>

        {/* Analyze Button */}
        <div className="text-center">
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing || files.length === 0}
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isAnalyzing ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Analyzing...
              </>
            ) : (
              <>
                <CogIcon className="w-5 h-5 mr-2" />
                Analyze Files
                <ArrowRightIcon className="w-5 h-5 ml-2" />
              </>
            )}
          </button>
        </div>
      </main>
    </div>
  );
};

export default Analysis; 