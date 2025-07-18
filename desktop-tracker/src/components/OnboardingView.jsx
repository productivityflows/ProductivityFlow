import React, { useState } from "react";
import { Loader2, User, Shield } from "lucide-react";

const Card = ({ children }) => <div className="bg-white border rounded-lg shadow-sm">{children}</div>;
const CardHeader = ({ children }) => <div className="p-6 border-b">{children}</div>;
const CardTitle = ({ children }) => <h3 className="text-lg text-center font-semibold">{children}</h3>;
const CardContent = ({ children }) => <div className="p-6">{children}</div>;
const Button = ({ children, ...props }) => <button className="w-full inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium bg-black text-white hover:bg-gray-800 disabled:opacity-50" {...props}>{children}</button>;

const Input = ({ icon, ...props }) => {
    const Icon = icon;
    return (
        <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Icon className="h-5 w-5 text-gray-400" />
            </div>
            <input
                className="flex h-10 w-full rounded-md border border-gray-300 bg-transparent pl-10 pr-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                {...props}
            />
        </div>
    );
};

// Updated to use the correct backend URL
const API_URL = "https://productivityflow-backend-v3.onrender.com";
const VERSION = "2.1.1"; // Version indicator for debugging

export function OnboardingView({ onTeamJoin }) {
    const [name, setName] = useState("");
    const [teamCode, setTeamCode] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!name.trim() || !teamCode.trim()) {
            setError("Name and team code are required.");
            return;
        };

        setIsLoading(true);
        setError("");

        try {
            console.log(`[Tracker v${VERSION}] Making request to: ${API_URL}/api/teams/join`);
            console.log(`[Tracker v${VERSION}] Request data:`, { name: name.trim(), team_code: teamCode.trim() });
            
            const response = await fetch(`${API_URL}/api/teams/join`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    name: name.trim(), 
                    team_code: teamCode.trim() 
                })
            });
            
            console.log(`[Tracker v${VERSION}] Response status:`, response.status);
            
            const data = await response.json();
            console.log(`[Tracker v${VERSION}] Response data:`, data);
            
            if (!response.ok) {
                throw new Error(data.error || "An unknown error occurred.");
            }
            onTeamJoin(data);
        } catch (err) {
            console.error(`[Tracker v${VERSION}] Error:`, err);
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>Join Your Team</CardTitle>
                <p className="text-sm text-gray-500 text-center mt-1">Enter your details to begin tracking</p>
                <p className="text-xs text-gray-400 text-center mt-1">v{VERSION} • API: {API_URL}</p>
            </CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label htmlFor="name" className="text-sm font-medium text-gray-700">Full Name</label>
                        <Input 
                            id="name" 
                            icon={User}
                            type="text"
                            value={name} 
                            onChange={(e) => setName(e.target.value)} 
                            placeholder="Enter your full name" 
                        />
                    </div>
                    <div>
                        <label htmlFor="teamCode" className="text-sm font-medium text-gray-700">Team Code</label>
                        <Input 
                            id="teamCode" 
                            icon={Shield}
                            type="text"
                            value={teamCode} 
                            onChange={(e) => setTeamCode(e.target.value.toUpperCase())} 
                            placeholder="Enter your team code" 
                        />
                    </div>
                    {error && <p className="text-red-500 text-sm text-center">{error}</p>}
                    <Button type="submit" disabled={isLoading}>
                        {isLoading ? <Loader2 className="animate-spin h-5 w-5" /> : "Join Team"}
                    </Button>
                </form>
            </CardContent>
        </Card>
    );
}