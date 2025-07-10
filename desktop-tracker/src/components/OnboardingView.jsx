import React, { useState } from "react";
import { Loader2 } from "lucide-react";

const Card = ({ children }) => <div className="bg-white border rounded-lg shadow-sm">{children}</div>;
const CardHeader = ({ children }) => <div className="p-6 border-b">{children}</div>;
const CardTitle = ({ children }) => <h3 className="text-lg text-center font-semibold">{children}</h3>;
const CardContent = ({ children }) => <div className="p-6">{children}</div>;
const Button = ({ children, ...props }) => <button className="w-full inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium bg-black text-white hover:bg-gray-800 disabled:opacity-50" {...props}>{children}</button>;
const Input = (props) => <input className="flex h-10 w-full rounded-md border border-gray-300 bg-transparent px-3 py-2 text-sm" {...props} />;

const API_URL = "";

export function OnboardingView({ onTeamJoin }) {
    const [teamCode, setTeamCode] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!teamCode.trim()) {
            setError("Please enter a team code.");
            return;
        };

        setIsLoading(true);
        setError("");

        try {
            const response = await fetch(`${API_URL}/api/teams/join`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ team_code: teamCode.trim() })
            });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.error || "An unknown error occurred.");
            }
            onTeamJoin(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Card>
            <CardHeader><CardTitle>Join Your Team</CardTitle></CardHeader>
            <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label htmlFor="teamCode" className="text-sm font-medium">Team Code</label>
                        <Input id="teamCode" value={teamCode} onChange={(e) => setTeamCode(e.target.value.toUpperCase())} placeholder="Enter Code from Manager" />
                    </div>
                    {error && <p className="text-red-500 text-sm">{error}</p>}
                    <Button type="submit" disabled={isLoading}>
                        {isLoading ? <Loader2 className="animate-spin h-5 w-5" /> : "Join Team & Start Tracking"}
                    </Button>
                </form>
            </CardContent>
        </Card>
    );
}