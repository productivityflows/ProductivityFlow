import React, { useState } from "react";
import { Loader2, User, Shield, Building } from "lucide-react";

interface OnboardingViewProps {
  onTeamJoin: (sessionData: {
    teamId: string;
    teamName: string;
    userId: string;
    userName: string;
    role: string;
    token: string;
  }) => void;
}

const API_URL = "https://productivityflow-backend-v3.onrender.com";

export function OnboardingView({ onTeamJoin }: OnboardingViewProps) {
  const [name, setName] = useState("");
  const [teamCode, setTeamCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Input validation
    if (!name.trim()) {
      setError("Please enter your name.");
      return;
    }
    
    if (!teamCode.trim()) {
      setError("Please enter your team code.");
      return;
    }
    
    if (name.trim().length < 2) {
      setError("Name must be at least 2 characters long.");
      return;
    }
    
    if (teamCode.trim().length < 4) {
      setError("Team code must be at least 4 characters long.");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      console.log(`Making request to: ${API_URL}/api/teams/join`);
      console.log(`Request data:`, { name: name.trim(), team_code: teamCode.trim() });
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
      
      const response = await fetch(`${API_URL}/api/teams/join`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "Accept": "application/json" 
        },
        body: JSON.stringify({ 
          employee_name: name.trim(), 
          team_code: teamCode.trim() 
        }),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      console.log(`Response status:`, response.status);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log(`Response data:`, data);

      // Validate required response fields
      if (!data.team?.id || !data.user?.id || !data.token) {
        throw new Error("Invalid response from server. Please try again.");
      }

      // Convert the response to the expected format
      const sessionData = {
        teamId: data.team.id,
        teamName: data.team.name || "Unknown Team",
        userId: data.user.id,
        userName: data.user.name || name.trim(),
        role: data.user.role || "employee",
        token: data.token
      };

      onTeamJoin(sessionData);
    } catch (err: any) {
      console.error(`Error joining team:`, err);
      
      // Provide user-friendly error messages
      let errorMessage = "An unexpected error occurred. Please try again.";
      
      if (err.name === 'AbortError') {
        errorMessage = "Request timed out. Please check your connection and try again.";
      } else if (err.message.includes('Failed to fetch')) {
        errorMessage = "Cannot connect to server. Please check your internet connection.";
      } else if (err.message.includes('404')) {
        errorMessage = "Team code not found. Please check your team code.";
      } else if (err.message.includes('400')) {
        errorMessage = "Invalid team code or name. Please check your information.";
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white border rounded-lg shadow-sm">
          <div className="p-6 border-b">
            <div className="flex items-center justify-center mb-4">
              <Building className="h-8 w-8 text-blue-600" />
            </div>
            <h3 className="text-lg text-center font-semibold">Join Your Team</h3>
            <p className="text-sm text-gray-500 text-center mt-1">
              Enter your details to begin tracking
            </p>
            <p className="text-xs text-gray-400 text-center mt-1">
              Employee Tracker • {API_URL}
            </p>
          </div>
          <div className="p-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="name" className="text-sm font-medium text-gray-700">
                  Full Name
                </label>
                <div className="relative mt-1">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="name"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Enter your full name"
                    className="flex h-10 w-full rounded-md border border-gray-300 bg-transparent pl-10 pr-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              <div>
                <label htmlFor="teamCode" className="text-sm font-medium text-gray-700">
                  Employee Team Code
                </label>
                <div className="relative mt-1">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Shield className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="teamCode"
                    type="text"
                    value={teamCode}
                    onChange={(e) => setTeamCode(e.target.value.toUpperCase())}
                    placeholder="Enter your employee team code"
                    className="flex h-10 w-full rounded-md border border-gray-300 bg-transparent pl-10 pr-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  This is the 6-character code provided by your manager
                </p>
              </div>
              {error && (
                <div className="p-3 rounded-md bg-red-50 border border-red-200">
                  <p className="text-red-600 text-sm">{error}</p>
                </div>
              )}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <Loader2 className="animate-spin h-5 w-5" />
                ) : (
                  "Join Team"
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}