import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  CloudArrowUpIcon, 
  ShieldCheckIcon, 
  CurrencyDollarIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  ChatBubbleLeftRightIcon,
  TrashIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import Onboarding from '../components/Onboarding';
import FeedbackModal from '../components/FeedbackModal';
import AnalysisHistoryModal from '../components/AnalysisHistoryModal';
import GitHubIcon from '../components/GitHubIcon';

const Dashboard = ({ user, token }) => {
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [showAnalysisHistory, setShowAnalysisHistory] = useState(false);
  const [recentAnalyses, setRecentAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    // Check if user needs onboarding
    const onboardingCompleted = localStorage.getItem('inframorph_onboarding_completed');
    if (!onboardingCompleted && user) {
      setShowOnboarding(true);
    }

    // Load recent analyses
    loadRecentAnalyses();
  }, [user, token]);

  const loadRecentAnalyses = async () => {
    try {
      const response = await fetch('http://localhost:8000/analyses', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setRecentAnalyses(data.analyses || []);
      }
    } catch (error) {
      console.error('Error loading analyses:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAnalysis = async (analysisId) => {
    if (!window.confirm('Are you sure you want to delete this analysis? This action cannot be undone.')) {
      return;
    }

    try {
      setDeletingId(analysisId);
      const response = await fetch(`http://localhost:8000/analyses/${analysisId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        // Remove from local state
        setRecentAnalyses(recentAnalyses.filter(analysis => analysis.analysis_id !== analysisId));
      } else {
        alert('Failed to delete analysis');
      }
    } catch (error) {
      console.error('Error deleting analysis:', error);
      alert('Error deleting analysis');
    } finally {
      setDeletingId(null);
    }
  };

  const handleOnboardingComplete = () => {
    setShowOnboarding(false);
    localStorage.setItem('inframorph_onboarding_completed', 'true');
  };

  const features = [
    {
      title: "Upload Infrastructure",
      description: "Analyze Terraform and Ansible files",
      icon: CloudArrowUpIcon,
      link: "/analysis",
      color: "bg-blue-500",
      hoverColor: "hover:bg-blue-600"
    },
    {
      title: "GitHub Integration",
      description: "Connect repositories for automated analysis",
      icon: GitHubIcon,
      link: "/github-connect",
      color: "bg-gray-700",
      hoverColor: "hover:bg-gray-800"
    },
    {
      title: "Security Analysis",
      description: "Advanced security vulnerability detection",
      icon: ShieldCheckIcon,
      link: "/security-analysis",
      color: "bg-red-500",
      hoverColor: "hover:bg-red-600"
    },
    {
      title: "Drift Detection",
      description: "Monitor infrastructure changes",
      icon: ExclamationTriangleIcon,
      link: "/drift-detection",
      color: "bg-yellow-500",
      hoverColor: "hover:bg-yellow-600"
    },
    {
      title: "Cost Optimization",
      description: "Identify cost-saving opportunities",
      icon: CurrencyDollarIcon,
      link: "/analysis",
      color: "bg-green-500",
      hoverColor: "hover:bg-green-600"
    },
    {
      title: "Multi-Cloud Support",
      description: "AWS, Azure, and GCP analysis",
      icon: ChartBarIcon,
      link: "/analysis",
      color: "bg-purple-500",
      hoverColor: "hover:bg-purple-600"
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Welcome back, {user?.username}!
              </h1>
              <p className="text-gray-600 mt-1">
                Ready to optimize your infrastructure with AI-powered insights
              </p>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => setShowFeedback(true)}
                className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
              >
                <ChatBubbleLeftRightIcon className="w-5 h-5 mr-2" />
                Feedback
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-lg">
                <ChartBarIcon className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Analyses</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {recentAnalyses.length}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <ShieldCheckIcon className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Security Score</p>
                <p className="text-2xl font-semibold text-gray-900">85</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <CurrencyDollarIcon className="w-6 h-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Cost Savings</p>
                <p className="text-2xl font-semibold text-gray-900">$2.4K</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <ExclamationTriangleIcon className="w-6 h-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Issues Found</p>
                <p className="text-2xl font-semibold text-gray-900">12</p>
              </div>
            </div>
          </div>
        </div>

        {/* Features Grid */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            What would you like to do?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <Link
                key={index}
                to={feature.link}
                className="group block bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-all duration-200"
              >
                <div className="p-6">
                  <div className="flex items-center">
                    <div className={`p-3 rounded-lg ${feature.color} ${feature.hoverColor} transition-colors`}>
                      <feature.icon className="w-6 h-6 text-white" />
                    </div>
                    <div className="ml-4">
                      <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                        {feature.title}
                      </h3>
                      <p className="text-gray-600 mt-1">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Recent Analyses */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900">
              Recent Analyses
            </h3>
            {recentAnalyses.length > 5 && (
              <button
                onClick={() => setShowAnalysisHistory(true)}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                Show More
              </button>
            )}
          </div>
          <div className="p-6">
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="text-gray-600 mt-2">Loading recent analyses...</p>
              </div>
            ) : recentAnalyses.length > 0 ? (
              <div className="space-y-4">
                {recentAnalyses.slice(0, 5).map((analysis) => (
                  <div
                    key={analysis.analysis_id}
                    className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div>
                      <h4 className="font-medium text-gray-900">
                        Analysis {analysis.analysis_id.slice(0, 8)}...
                      </h4>
                      <p className="text-sm text-gray-600">
                        {new Date(analysis.timestamp).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Link
                        to={`/results/${analysis.analysis_id}`}
                        className="flex items-center text-blue-600 hover:text-blue-800 font-medium"
                      >
                        <EyeIcon className="w-4 h-4 mr-1" />
                        View
                      </Link>
                      <button
                        onClick={() => handleDeleteAnalysis(analysis.analysis_id)}
                        disabled={deletingId === analysis.analysis_id}
                        className="flex items-center text-red-600 hover:text-red-800 font-medium disabled:opacity-50"
                      >
                        <TrashIcon className="w-4 h-4 mr-1" />
                        {deletingId === analysis.analysis_id ? 'Deleting...' : 'Delete'}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <CloudArrowUpIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h4 className="text-lg font-medium text-gray-900 mb-2">
                  No analyses yet
                </h4>
                <p className="text-gray-600 mb-4">
                  Start by uploading your infrastructure files for analysis
                </p>
                <Link
                  to="/analysis"
                  className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                >
                  <CloudArrowUpIcon className="w-5 h-5 mr-2" />
                  Upload Files
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Demo Files Section */}
        <div className="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            🎯 Try Our Demo Files
          </h3>
          <p className="text-gray-600 mb-4">
            Not sure where to start? We've created sample infrastructure files with common security and cost issues for you to test InfraMorph's capabilities.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white p-4 rounded-lg border">
              <h4 className="font-semibold text-gray-900 mb-2">AWS Demo</h4>
              <p className="text-gray-600 text-sm mb-3">
                Contains security groups, S3 buckets, RDS instances with various issues
              </p>
              <Link
                to="/analysis?demo=aws"
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                Use Demo File →
              </Link>
            </div>
            <div className="bg-white p-4 rounded-lg border">
              <h4 className="font-semibold text-gray-900 mb-2">Azure Demo</h4>
              <p className="text-gray-600 text-sm mb-3">
                Contains VMs, storage accounts, SQL databases with security issues
              </p>
              <Link
                to="/analysis?demo=azure"
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                Use Demo File →
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Onboarding Modal */}
      {showOnboarding && (
        <Onboarding
          user={user}
          onComplete={handleOnboardingComplete}
        />
      )}

      {/* Feedback Modal */}
      {showFeedback && (
        <FeedbackModal
          isOpen={showFeedback}
          onClose={() => setShowFeedback(false)}
          user={user}
          token={token}
        />
      )}

      {/* Analysis History Modal */}
      {showAnalysisHistory && (
        <AnalysisHistoryModal
          isOpen={showAnalysisHistory}
          onClose={() => setShowAnalysisHistory(false)}
          token={token}
        />
      )}
    </div>
  );
};

export default Dashboard; 