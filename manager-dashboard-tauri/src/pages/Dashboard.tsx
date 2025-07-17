import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Users, Clock, TrendingUp, Target, AlertCircle, Loader2 } from 'lucide-react';

// Updated to use the correct backend URL
const API_URL = "https://productivityflow-backend.onrender.com";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ComponentType<any>;
  change?: string;
  changeText?: string;
  color: string;
}

interface Analytics {
  totalHours: number;
  avgProductivity: number;
  goalsCompleted: number;
  activeMembers: number;
  totalMembers: number;
  hoursChange?: string;
  productivityChange?: string;
}

interface Performance {
  topPerformers: Array<{
    userName: string;
    overallScore: number;
  }>;
  needsImprovement: Array<{
    userName: string;
    overallScore: number;
  }>;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, change, changeText, color }) => {
  const Icon = icon;
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium text-gray-500">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="text-3xl font-bold text-gray-800">{value}</div>
          <div className={`p-2 rounded-full bg-${color}-100`}>
            <Icon className={`h-6 w-6 text-${color}-600`} />
          </div>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          <span className="text-green-600 font-semibold">{change}</span> {changeText}
        </p>
      </CardContent>
    </Card>
  );
};

export default function DashboardPage() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [performance, setPerformance] = useState<Performance | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    // Fetch analytics for the first team found
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        setError(null);
        console.log("Fetching teams...");
        
        // Add timeout for requests
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);
        
        const teamsResponse = await fetch(`${API_URL}/api/teams`, {
          signal: controller.signal,
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        });
        
        clearTimeout(timeoutId);
        
        if (!teamsResponse.ok) {
          if (teamsResponse.status === 401) {
            throw new Error("Authentication required. Please log in again.");
          } else if (teamsResponse.status >= 500) {
            throw new Error("Server error. Please try again later.");
          } else {
            throw new Error(`Failed to fetch teams (${teamsResponse.status})`);
          }
        }
        
        const teamsData = await teamsResponse.json();
        console.log("Teams data:", teamsData);
        
        // Handle API errors gracefully
        if (teamsData.error) {
          throw new Error(teamsData.error);
        }
        
        const teams = teamsData.teams || [];
        
        if (teams.length === 0) {
          setError("No teams found. Create a team to get started.");
          return;
        }
        
        const firstTeamId = teams[0].id;
        console.log("Fetching stats for team:", firstTeamId);
        
        // Fetch both analytics and performance data with timeout
        const fetchWithTimeout = (url: string) => {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 15000);
          
          return fetch(url, { 
            signal: controller.signal,
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            }
          }).finally(() => clearTimeout(timeoutId));
        };
        
        const [analyticsResponse, performanceResponse] = await Promise.allSettled([
          fetchWithTimeout(`${API_URL}/api/teams/${firstTeamId}/stats`),
          fetchWithTimeout(`${API_URL}/api/teams/${firstTeamId}/performance`)
        ]);
        
        // Handle analytics response
        if (analyticsResponse.status === 'fulfilled' && analyticsResponse.value.ok) {
          const analyticsData = await analyticsResponse.value.json();
          console.log("Analytics data:", analyticsData);
          setAnalytics(analyticsData);
        } else {
          console.error("Failed to fetch analytics:", analyticsResponse);
          // Set default analytics to prevent white screen
          setAnalytics({
            totalHours: 0,
            avgProductivity: 0,
            goalsCompleted: 0,
            activeMembers: 0,
            totalMembers: teams[0]?.memberCount || 0
          });
        }
        
        // Handle performance response
        if (performanceResponse.status === 'fulfilled' && performanceResponse.value.ok) {
          const performanceData = await performanceResponse.value.json();
          console.log("Performance data:", performanceData);
          setPerformance(performanceData);
        } else {
          console.error("Failed to fetch performance:", performanceResponse);
          // Set default performance to prevent white screen
          setPerformance({
            topPerformers: [],
            needsImprovement: []
          });
        }
        
      } catch (error: any) {
        console.error("Error fetching analytics:", error);
        
        let errorMessage = "Failed to load dashboard data. Please try again.";
        
        if (error.name === 'AbortError') {
          errorMessage = "Request timed out. Please check your connection.";
        } else if (error.message.includes('Failed to fetch')) {
          errorMessage = "Cannot connect to server. Please check your internet connection.";
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };
    
    fetchAnalytics();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchAnalytics, 30000);
    
    return () => clearInterval(interval);
  }, [retryCount]);

  const handleRetry = () => {
    setRetryCount(prev => prev + 1);
  };

  const displayValue = (value: number | null | undefined, suffix = '') => {
    if (loading) return '...';
    return value !== null && value !== undefined ? `${value}${suffix}` : '0' + suffix;
  };

  const renderPerformanceSection = () => {
    if (loading) {
      return (
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <h4 className="font-semibold text-green-600 mb-2">🏆 Top Performers (Raise Candidates)</h4>
            <div className="text-sm text-gray-500">Loading...</div>
          </div>
          <div>
            <h4 className="font-semibold text-orange-600 mb-2">⚠️ Needs Improvement</h4>
            <div className="text-sm text-gray-500">Loading...</div>
          </div>
        </div>
      );
    }

    if (!performance || (!performance.topPerformers?.length && !performance.needsImprovement?.length)) {
      return (
        <div className="text-center py-8">
          <p className="text-gray-500">No performance data available yet.</p>
          <p className="text-sm text-gray-400">Add some activity data to see performance analysis.</p>
        </div>
      );
    }

    return (
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <h4 className="font-semibold text-green-600 mb-2">🏆 Top Performers (Raise Candidates)</h4>
          <div className="space-y-2 text-sm">
            {performance.topPerformers?.length > 0 ? (
              performance.topPerformers.map((performer, index) => (
                <div key={index} className="flex justify-between items-center p-2 bg-green-50 rounded">
                  <span>{performer.userName}</span>
                  <span className="text-green-600 font-medium">{performer.overallScore}% score</span>
                </div>
              ))
            ) : (
              <div className="text-gray-500 text-center py-4">
                No top performers yet (need 90%+ score)
              </div>
            )}
          </div>
        </div>
        <div>
          <h4 className="font-semibold text-orange-600 mb-2">⚠️ Needs Improvement</h4>
          <div className="space-y-2 text-sm">
            {performance.needsImprovement?.length > 0 ? (
              performance.needsImprovement.map((performer, index) => (
                <div key={index} className="flex justify-between items-center p-2 bg-orange-50 rounded">
                  <span>{performer.userName}</span>
                  <span className="text-orange-600 font-medium">{performer.overallScore}% score</span>
                </div>
              ))
            ) : (
              <div className="text-gray-500 text-center py-4">
                No underperformers (everyone above 60%)
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Show error state
  if (error && !loading) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-800">Welcome back, Manager!</h1>
          <p className="text-gray-500">Dashboard</p>
        </div>
        
        <Card className="border-red-200">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Unable to Load Dashboard</h3>
            <p className="text-gray-600 text-center mb-4 max-w-md">{error}</p>
            <button
              onClick={handleRetry}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              <span>Try Again</span>
            </button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Show loading state
  if (loading) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-800">Welcome back, Manager!</h1>
          <p className="text-gray-500">Loading your dashboard...</p>
        </div>
        
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardContent className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-gray-400" />
              </CardContent>
            </Card>
          ))}
        </div>
        
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Loading performance data...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-gray-800">Welcome back, Manager!</h1>
        <p className="text-gray-500">Here's what's happening with your team's productivity today.</p>
        <p className="text-xs text-gray-400 mt-1">Auto-refreshing every 30 seconds</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatCard 
          title="Total Team Hours" 
          value={displayValue(analytics?.totalHours, 'h')} 
          icon={Clock} 
          change={analytics?.hoursChange || ""} 
          changeText="from yesterday" 
          color="blue" 
        />
        <StatCard 
          title="Avg Productivity" 
          value={displayValue(analytics?.avgProductivity, '%')} 
          icon={TrendingUp} 
          change={analytics?.productivityChange || ""} 
          changeText="from last week" 
          color="green" 
        />
        <StatCard 
          title="Goals Completed" 
          value={displayValue(analytics?.goalsCompleted)} 
          icon={Target} 
          change="" 
          changeText="" 
          color="orange" 
        />
        <StatCard 
          title="Active Members" 
          value={displayValue(analytics?.activeMembers)} 
          icon={Users} 
          change={analytics?.totalMembers ? `/ ${analytics.totalMembers}` : ""} 
          changeText="currently tracking" 
          color="teal" 
        />
      </div>

      {/* Performance Analysis Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <TrendingUp className="mr-2 h-5 w-5" />
            Performance Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          {renderPerformanceSection()}
          <div className="mt-4 p-3 bg-blue-50 rounded">
            <p className="text-sm text-blue-700">
              <strong>Analysis:</strong> Efficiency calculated as (Productive Hours / Total Hours) × 100. 
              Consider raises for 90%+ efficiency, coaching for &lt;60% efficiency.
            </p>
          </div>
        </CardContent>
      </Card>
      
      {/* Debug info */}
      <Card className="bg-gray-50">
        <CardHeader>
          <CardTitle className="text-sm">Debug Info</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-xs text-gray-600">
            <p>API URL: {API_URL}</p>
            <p>Loading: {loading ? 'Yes' : 'No'}</p>
            <p>Analytics: {analytics ? 'Loaded' : 'Not loaded'}</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}