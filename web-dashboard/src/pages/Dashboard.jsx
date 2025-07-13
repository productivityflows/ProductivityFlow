import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Progress } from '../components/ui/Progress';
import { Users, Clock, TrendingUp, Target, Plus } from 'lucide-react';

// Updated to use the correct backend URL
const API_URL = "https://productivityflow-backend-v2.onrender.com";

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
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch analytics for the first team found
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        console.log("Fetching teams...");
        
        const teamsResponse = await fetch(`${API_URL}/api/teams`);
        const teamsData = await teamsResponse.json();
        console.log("Teams data:", teamsData);
        
        if (teamsData.teams && teamsData.teams.length > 0) {
          const firstTeamId = teamsData.teams[0].id;
          console.log("Fetching stats for team:", firstTeamId);
          
          const analyticsResponse = await fetch(`${API_URL}/api/teams/${firstTeamId}/stats`);
          const analyticsData = await analyticsResponse.json();
          console.log("Analytics data:", analyticsData);
          
          setAnalytics(analyticsData);
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