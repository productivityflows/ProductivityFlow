import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Progress } from '../components/ui/Progress';
import { Users, Clock, TrendingUp, Target, Plus } from 'lucide-react';

const API_URL = "/api";

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

  useEffect(() => {
    // We fetch analytics for the first team found, for this demo
    const fetchAnalytics = async () => {
        const teamsResponse = await fetch(`${API_URL}/teams`);
        const teamsData = await teamsResponse.json();
        if (teamsData.teams && teamsData.teams.length > 0) {
            const firstTeamId = teamsData.teams[0].id;
            const analyticsResponse = await fetch(`${API_URL}/teams/${firstTeamId}/analytics`);
            const analyticsData = await analyticsResponse.json();
            setAnalytics(analyticsData);
        }
    };
    fetchAnalytics();
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-gray-800">Welcome back, Alex!</h1>
        <p className="text-gray-500">Here's what's happening with your team's productivity today.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatCard title="Total Team Hours" value={analytics ? `${analytics.totalHours}h` : '...'} icon={Clock} change="+12%" changeText="from yesterday" color="blue" />
        <StatCard title="Avg Productivity" value={analytics ? `${analytics.avgTeamProductivity}%` : '...'} icon={TrendingUp} change="+5%" changeText="from last week" color="green" />
        <StatCard title="Goals Completed" value={analytics ? `${analytics.goalsCompleted}/30` : '...'} icon={Target} change="" changeText="" color="orange" />
        <StatCard title="Active Members" value={analytics ? analytics.activeMembers : '...'} icon={Users} change="" changeText="currently tracking" color="teal" />
      </div>

      {/* Other components like Activity and Goals would be built out here */}
    </div>
  );
}