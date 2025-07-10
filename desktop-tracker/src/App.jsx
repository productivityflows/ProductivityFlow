import React, { useState, useEffect } from "react";
import { OnboardingView } from "./components/OnboardingView";
import { MainTrackingView } from "./components/MainTrackingView";

export default function App() {
    const [session, setSession] = useState(null);

    useEffect(() => {
        const savedSession = localStorage.getItem("tracker_session");
        if (savedSession) {
            setSession(JSON.parse(savedSession));
        }
    }, []);

    const handleTeamJoin = (sessionData) => {
        setSession(sessionData);
        localStorage.setItem("tracker_session", JSON.stringify(sessionData));
    };

    const handleLogout = () => {
        setSession(null);
        localStorage.removeItem("tracker_session");
    };

    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
            <div className="w-full max-w-sm">
                {!session ? (
                    <OnboardingView onTeamJoin={handleTeamJoin} />
                ) : (
                    <MainTrackingView session={session} onLogout={handleLogout} />
                )}
            </div>
        </div>
    );
}