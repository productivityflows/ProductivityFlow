import React, { useState, useEffect } from "react";
import { Activity, Pause, LogOut } from "lucide-react";

const Card = ({ children }) => <div className="bg-white border rounded-lg shadow-sm">{children}</div>;
const CardHeader = ({ children }) => <div className="p-6 border-b">{children}</div>;
const CardTitle = ({ children }) => <h3 className="text-lg font-semibold">{children}</h3>;
const CardContent = ({ children }) => <div className="p-6">{children}</div>;
const Button = ({ children, ...props }) => <button className="inline-flex items-center justify-center rounded-md px-3 py-1.5 text-sm font-medium bg-red-600 text-white hover:bg-red-700" {...props}>{children}</button>;
const Switch = ({ checked, onCheckedChange }) => (
    <button onClick={() => onCheckedChange(!checked)} className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${checked ? 'bg-green-600' : 'bg-gray-300'}`}>
        <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${checked ? 'translate-x-6' : 'translate-x-1'}`} />
    </button>
);

class ActivityTracker {
    constructor(session) {
        this.session = session;
        this.intervalId = null;
    }

    start() {
        console.log("▶️ Tracking STARTED for user:", this.session.userId);
        this.intervalId = setInterval(() => {
            const activityPayload = {
                userId: this.session.userId,
                activities: [{
                    type: "simulated_activity",
                    appName: "Demo App",
                    timestamp: new Date().toISOString()
                }]
            };
            fetch("http://localhost:8888/api/activity", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(activityPayload)
            });
        }, 10000); 
    }

    stop() {
        console.log("⏹️ Tracking STOPPED for user:", this.session.userId);
        if (this.intervalId) {
            clearInterval(this.intervalId);
        }
    }
}

export function MainTrackingView({ session, onLogout }) {
    const [isTracking, setIsTracking] = useState(false);
    const [tracker, setTracker] = useState(null);

    const handleTrackingToggle = (checked) => {
        setIsTracking(checked);
        if (checked) {
            const newTracker = new ActivityTracker(session);
            newTracker.start();
            setTracker(newTracker);
        } else {
            if (tracker) tracker.stop();
            setTracker(null);
        }
    };

    useEffect(() => {
        return () => {
            if (tracker) tracker.stop();
        };
    }, [tracker]);


    return (
        <Card>
            <CardHeader>
                <CardTitle>Productivity Tracker</CardTitle>
                <p className="text-sm text-gray-500">Team: {session.teamName}</p>
            </CardHeader>
            <CardContent className="space-y-4 text-center">
                <div className="flex items-center space-x-3 justify-center bg-gray-100 p-4 rounded-lg">
                    <Switch checked={isTracking} onCheckedChange={handleTrackingToggle} />
                    <label className="text-lg font-medium">{isTracking ? "Tracking ON" : "Tracking OFF"}</label>
                </div>
                <Button onClick={onLogout}><LogOut className="h-4 w-4 mr-2" />Log Out</Button>
            </CardContent>
        </Card>
    );
}