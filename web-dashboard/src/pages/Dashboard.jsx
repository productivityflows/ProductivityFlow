import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Progress } from '../components/ui/Progress';
import { Users, Clock, TrendingUp, Target, Plus } from 'lucide-react';

// Updated to use the correct backend URL
const API_URL = "https://productivityflow-backend-v3.onrender.com";

const StatCard = ({ title, value, icon, change, changeText, color }) => {
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
  const [analytics, setAnalytics] = useState(null);
  const [performance, setPerformance] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch analytics for the first team found
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        console.log("Fetching teams...");
        
        const teamsResponse = await fetch(`${API_URL}/api/teams`);
        
        if (!teamsResponse.ok) {
          throw new Error(`Teams API error: ${teamsResponse.status}`);
        }
        
        const teamsData = await teamsResponse.json();
        console.log("Teams data:", teamsData);
        
        // Handle API errors gracefully
        if (teamsData.error) {
          console.error("Teams API error:", teamsData.error);
          return;
        }
        
        const teams = teamsData.teams || [];
        
        if (teams.length > 0) {
          const firstTeamId = teams[0].id;
          console.log("Fetching stats for team:", firstTeamId);
          
          // Fetch both analytics and performance data
          const [analyticsResponse, performanceResponse] = await Promise.all([
            fetch(`${API_URL}/api/teams/${firstTeamId}/stats`),
            fetch(`${API_URL}/api/teams/${firstTeamId}/performance`)
          ]);
          
          // Check if responses are OK
          if (analyticsResponse.ok) {
            const analyticsData = await analyticsResponse.json();
            console.log("Analytics data:", analyticsData);
            setAnalytics(analyticsData);
          } else {
            console.error("Analytics API error:", analyticsResponse.status);
          }
          
          if (performanceResponse.ok) {
            const performanceData = await performanceResponse.json();
            console.log("Performance data:", performanceData);
            setPerformance(performanceData);
          } else {
            console.error("Performance API error:", performanceResponse.status);
          }
        } else {
          console.log("No teams found");
        }
      } catch (error) {
        console.error("Error fetching analytics:", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchAnalytics();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchAnalytics, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const displayValue = (value, suffix = '') => {
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

      {/* Other components like Activity and Goals would be built out here */}
      
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