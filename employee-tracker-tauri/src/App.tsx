import { useState, useEffect } from "react";
import { OnboardingView } from "./components/OnboardingView";
import { TrackingView } from "./components/TrackingView";

interface Session {
  teamId: string;
  teamName: string;
  userId: string;
  userName: string;
  role: string;
  token: string;
}

export default function App() {
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Load saved session on app start
    const loadSession = async () => {
      try {
        const savedSession = localStorage.getItem("tracker_session");
        if (savedSession) {
          const sessionData = JSON.parse(savedSession);
          setSession(sessionData);
        }
      } catch (error) {
        console.error("Error loading session:", error);
        localStorage.removeItem("tracker_session");
      } finally {
        setIsLoading(false);
      }
    };

    loadSession();
  }, []);

  const handleTeamJoin = (sessionData: Session) => {
    setSession(sessionData);
    localStorage.setItem("tracker_session", JSON.stringify(sessionData));
  };

  const handleLogout = () => {
    setSession(null);
    localStorage.removeItem("tracker_session");
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {!session ? (
        <OnboardingView onTeamJoin={handleTeamJoin} />
      ) : (
        <TrackingView session={session} onLogout={handleLogout} />
      )}
    </div>
  );
}