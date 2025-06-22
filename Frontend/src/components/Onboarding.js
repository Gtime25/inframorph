import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  CheckCircleIcon,
  ArrowRightIcon,
  ArrowLeftIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

const Onboarding = ({ user, onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedSteps, setCompletedSteps] = useState([]);
  const navigate = useNavigate();

  const steps = [
    {
      id: 'welcome',
      title: 'Welcome to InfraMorph!',
      description: 'Your AI-powered infrastructure optimization platform',
      content: (
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
            <span className="text-2xl">🚀</span>
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Let's get you started with InfraMorph
          </h3>
          <p className="text-gray-600">
            In just a few minutes, you'll learn how to analyze your infrastructure, 
            detect security issues, and optimize costs with AI-powered insights.
          </p>
        </div>
      )
    },
    {
      id: 'upload',
      title: 'Upload Your Infrastructure Files',
      description: 'Start with Terraform or Ansible files',
      content: (
        <div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <h4 className="font-semibold text-blue-900 mb-2">What you can upload:</h4>
            <ul className="text-blue-800 space-y-1 text-sm">
              <li>• Terraform files (.tf, .tfvars, .hcl)</li>
              <li>• Ansible playbooks (.yml, .yaml)</li>
              <li>• Infrastructure configuration files</li>
            </ul>
          </div>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 className="font-semibold text-green-900 mb-2">💡 Pro Tip:</h4>
            <p className="text-green-800 text-sm">
              Try our demo files first to see how InfraMorph works! 
              We've created sample infrastructure with common issues for you to test.
            </p>
          </div>
        </div>
      )
    },
    {
      id: 'analysis',
      title: 'AI-Powered Analysis',
      description: 'Get intelligent insights and recommendations',
      content: (
        <div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <div className="text-2xl mb-2">🔒</div>
              <h4 className="font-semibold text-red-900">Security</h4>
              <p className="text-red-800 text-sm">Vulnerability detection & compliance</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl mb-2">💰</div>
              <h4 className="font-semibold text-green-900">Cost</h4>
              <p className="text-green-800 text-sm">Optimization recommendations</p>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl mb-2">📋</div>
              <h4 className="font-semibold text-blue-900">Best Practices</h4>
              <p className="text-blue-800 text-sm">Industry standards & guidelines</p>
            </div>
          </div>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h4 className="font-semibold text-yellow-900 mb-2">🤖 AI Features:</h4>
            <ul className="text-yellow-800 text-sm space-y-1">
              <li>• Intelligent code analysis using OpenAI</li>
              <li>• Automated GitHub pull request creation</li>
              <li>• Multi-cloud support (AWS, Azure, GCP)</li>
              <li>• Infrastructure drift detection</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      id: 'actions',
      title: 'Take Action',
      description: 'Implement improvements automatically',
      content: (
        <div>
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 mb-4">
            <h4 className="font-semibold text-purple-900 mb-2">🚀 Automated Actions:</h4>
            <ul className="text-purple-800 space-y-2">
              <li className="flex items-center">
                <CheckCircleIcon className="w-4 h-4 mr-2 text-green-500" />
                Create GitHub pull requests with fixes
              </li>
              <li className="flex items-center">
                <CheckCircleIcon className="w-4 h-4 mr-2 text-green-500" />
                Generate refactored infrastructure code
              </li>
              <li className="flex items-center">
                <CheckCircleIcon className="w-4 h-4 mr-2 text-green-500" />
                Apply security and cost optimizations
              </li>
            </ul>
          </div>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h4 className="font-semibold text-gray-900 mb-2">📊 What you'll get:</h4>
            <ul className="text-gray-700 text-sm space-y-1">
              <li>• Detailed analysis reports</li>
              <li>• Security scoring (0-100)</li>
              <li>• Cost optimization estimates</li>
              <li>• Compliance framework checking</li>
              <li>• Actionable recommendations</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      id: 'demo',
      title: 'Try Demo Files',
      description: 'Test with our sample infrastructure',
      content: (
        <div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <h4 className="font-semibold text-blue-900 mb-2">🎯 Ready to test?</h4>
            <p className="text-blue-800 mb-4">
              We've created demo infrastructure files with common security and cost issues. 
              Perfect for testing InfraMorph's capabilities!
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white p-3 rounded border">
                <h5 className="font-semibold text-gray-900">AWS Demo</h5>
                <p className="text-gray-600 text-sm">Contains security groups, S3 buckets, RDS instances with issues</p>
              </div>
              <div className="bg-white p-3 rounded border">
                <h5 className="font-semibold text-gray-900">Azure Demo</h5>
                <p className="text-gray-600 text-sm">Contains VMs, storage accounts, SQL databases with issues</p>
              </div>
            </div>
          </div>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 className="font-semibold text-green-900 mb-2">✅ Next Steps:</h4>
            <ol className="text-green-800 text-sm space-y-1">
              <li>1. Upload demo files or your own infrastructure</li>
              <li>2. Run analysis to see security and cost insights</li>
              <li>3. Review AI-generated recommendations</li>
              <li>4. Create automated pull requests with fixes</li>
            </ol>
          </div>
        </div>
      )
    }
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCompletedSteps([...completedSteps, steps[currentStep].id]);
      setCurrentStep(currentStep + 1);
    } else {
      completeOnboarding();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const completeOnboarding = () => {
    setCompletedSteps([...completedSteps, steps[currentStep].id]);
    localStorage.setItem('inframorph_onboarding_completed', 'true');
    if (onComplete) {
      onComplete();
    } else {
      navigate('/dashboard');
    }
  };

  const skipOnboarding = () => {
    localStorage.setItem('inframorph_onboarding_completed', 'true');
    if (onComplete) {
      onComplete();
    } else {
      navigate('/dashboard');
    }
  };

  const currentStepData = steps[currentStep];
  const progress = ((currentStep + 1) / steps.length) * 100;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {currentStepData.title}
            </h2>
            <p className="text-gray-600">{currentStepData.description}</p>
          </div>
          <button
            onClick={skipOnboarding}
            className="text-gray-400 hover:text-gray-600"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="px-6 py-4">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <div className="flex justify-between text-sm text-gray-600 mt-2">
            <span>Step {currentStep + 1} of {steps.length}</span>
            <span>{Math.round(progress)}% complete</span>
          </div>
        </div>

        {/* Content */}
        <div className="px-6 py-4">
          {currentStepData.content}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 0}
            className="flex items-center px-4 py-2 text-gray-600 hover:text-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ArrowLeftIcon className="w-4 h-4 mr-2" />
            Previous
          </button>

          <div className="flex space-x-2">
            <button
              onClick={skipOnboarding}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Skip
            </button>
            <button
              onClick={handleNext}
              className="flex items-center px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              {currentStep === steps.length - 1 ? (
                <>
                  Get Started
                  <CheckCircleIcon className="w-4 h-4 ml-2" />
                </>
              ) : (
                <>
                  Next
                  <ArrowRightIcon className="w-4 h-4 ml-2" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Onboarding; 