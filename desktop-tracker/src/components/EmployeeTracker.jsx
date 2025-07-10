import React, { useState } from 'react';
import { User, Shield, Loader2 } from 'lucide-react';

const Input = ({ icon, ...props }) => {
    const Icon = icon;
    return (
        <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Icon className="h-5 w-5 text-gray-400" />
            </div>
            <input
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
                {...props}
            />
        </div>
    );
};

const API_URL = "http://localhost:8888";

export default function EmployeeTracker({ onTeamJoin }) {
    const [name, setName] = useState('');
    const [teamCode, setTeamCode] = useState('');
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
            const response = await fetch(`${API_URL}/api/teams/join`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    name: name.trim(), 
                    team_code: teamCode.trim() 
                })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error);
            onTeamJoin(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };
    
    return (
        <div className="w-full max-w-sm mx-auto bg-white rounded-2xl shadow-xl p-8 space-y-6">
            <div className="text-center">
                <h1 className="text-2xl font-bold text-gray-800">Join Your Team</h1>
                <p className="text-gray-500">Enter your details to begin tracking</p>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4">
                {/* THIS SECTION CREATES THE "FULL NAME" INPUT */}
                <div>
                    <label className="text-sm font-medium text-gray-700">Full Name</label>
                    <Input icon={User} type="text" placeholder="Enter your full name" value={name} onChange={e => setName(e.target.value)} />
                </div>
                {/* END OF SECTION */}

                <div>
                    <label className="text-sm font-medium text-gray-700">Team Code</label>
                    <Input icon={Shield} type="text" placeholder="Enter your team code" value={teamCode} onChange={e => setTeamCode(e.target.value.toUpperCase())} />
                </div>
                {error && <p className="text-red-500 text-sm text-center">{error}</p>}
                <button type="submit" disabled={isLoading} className="w-full mt-2 py-3 px-4 rounded-lg text-white font-semibold transition-colors bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300 disabled:cursor-not-allowed">
                    {isLoading ? <Loader2 className="mx-auto animate-spin" /> : "Join Team"}
                </button>
            </form>
        </div>
    );
}