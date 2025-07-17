import { useState, useEffect } from "react";
import { invoke } from "@tauri-apps/api/tauri";
import { listen } from "@tauri-apps/api/event";
import { 
  Play, 
  Pause, 
  Monitor, 
  Clock, 
  Activity, 
  LogOut, 
  Building
} from "lucide-react";

interface Session {
  teamId: string;
  teamName: string;
  userId: string;
  userName: string;
  role: string;
  token: string;
}

interface TrackingViewProps {
  session: Session;
  onLogout: () => void;
}

interface ActivityData {
  active_app: string;
  window_title: string;
  idle_time: number;
  timestamp: number;
}

export function TrackingView({ session, onLogout }: TrackingViewProps) {
  const [isTracking, setIsTracking] = useState(false);
  const [currentActivity, setCurrentActivity] = useState<ActivityData | null>(null);
  const [error, setError] = useState("");
  const [lastSyncTime, setLastSyncTime] = useState<Date | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('disconnected');

  useEffect(() => {
    // Listen for activity updates from the Rust backend
    const unsubscribe = listen<ActivityData>("activity-update", (event) => {
      setCurrentActivity(event.payload);
      setLastSyncTime(new Date());
    });

    return () => {
      unsubscribe.then(fn => fn());
    };
  }, []);

  const handleStartTracking = async () => {
    if (isLoading) return;
    
    setIsLoading(true);
    setError("");
    setConnectionStatus('connecting');
    
    try {
      const result = await invoke<string>("start_tracking", {
        userId: session.userId,
        teamId: session.teamId,
        token: session.token,
      });
      
      setIsTracking(true);
      setConnectionStatus('connected');
      console.log("Tracking started:", result);
    } catch (err: any) {
      console.error("Failed to start tracking:", err);
      setConnectionStatus('disconnected');
      
      // Provide user-friendly error messages
      let errorMessage = "Failed to start tracking. Please try again.";
      if (err.toString().includes('permission')) {
        errorMessage = "Permission denied. Please allow the app to monitor your activity.";
      } else if (err.toString().includes('network')) {
        errorMessage = "Network error. Please check your internet connection.";
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStopTracking = async () => {
    if (isLoading) return;
    
    setIsLoading(true);
    setError("");
    
    try {
      const result = await invoke<string>("stop_tracking");
      setIsTracking(false);
      setCurrentActivity(null);
      setConnectionStatus('disconnected');
      console.log("Tracking stopped:", result);
    } catch (err: any) {
      console.error("Failed to stop tracking:", err);
      setError("Failed to stop tracking. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGetCurrentActivity = async () => {
    try {
      setError("");
      const activity = await invoke<ActivityData>("get_current_activity");
      setCurrentActivity(activity);
      setLastSyncTime(new Date());
    } catch (err: any) {
      console.error("Failed to get current activity:", err);
      // Don't show error for this background operation unless it's critical
    }
  };

  const handleSendActivity = async () => {
    if (!currentActivity) return;
    
    try {
      setError("");
      const result = await invoke<string>("send_activity_data", {
        activity: currentActivity,
      });
      console.log("Activity sent:", result);
      setLastSyncTime(new Date());
    } catch (err: any) {
      console.error("Failed to send activity:", err);
      setError(err.toString());
    }
  };

  const formatIdleTime = (seconds: number) => {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
    return `${Math.round(seconds / 3600)}h`;
  };

  const formatLastSync = (date: Date) => {
    const now = new Date();
    const diff = Math.round((now.getTime() - date.getTime()) / 1000);
    
    if (diff < 60) return "Just now";
    if (diff < 3600) return `${Math.round(diff / 60)}m ago`;
    return `${Math.round(diff / 3600)}h ago`;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Building className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-lg font-semibold">ProductivityFlow Tracker</h1>
                <p className="text-sm text-gray-500">
                  {session.userName} • {session.teamName}
                </p>
              </div>
            </div>
            <button
              onClick={onLogout}
              className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-800 border rounded-md hover:bg-gray-50"
            >
              <LogOut className="h-4 w-4" />
              <span>Logout</span>
            </button>
          </div>
        </div>

        {/* Tracking Control */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium">Activity Tracking</h2>
            <div className="flex items-center space-x-4">
              {/* Connection Status */}
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${
                  connectionStatus === 'connected' ? 'bg-green-500' : 
                  connectionStatus === 'connecting' ? 'bg-yellow-500 animate-pulse' : 
                  'bg-red-500'
                }`} />
                <span className="text-sm text-gray-600 capitalize">
                  {connectionStatus}
                </span>
              </div>
              
              {/* Tracking Status */}
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${isTracking ? 'bg-green-500' : 'bg-gray-400'}`} />
                <span className="text-sm text-gray-600">
                  {isTracking ? 'Tracking' : 'Stopped'}
                </span>
              </div>
            </div>
          </div>

          <div className="flex space-x-3">
            {!isTracking ? (
              <button
                onClick={handleStartTracking}
                disabled={isLoading}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                ) : (
                  <Play className="h-4 w-4" />
                )}
                <span>{isLoading ? 'Starting...' : 'Start Tracking'}</span>
              </button>
            ) : (
              <button
                onClick={handleStopTracking}
                disabled={isLoading}
                className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
                ) : (
                  <Pause className="h-4 w-4" />
                )}
                <span>{isLoading ? 'Stopping...' : 'Stop Tracking'}</span>
              </button>
            )}
            
            <button
              onClick={handleGetCurrentActivity}
              disabled={!isTracking || isLoading}
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Activity className="h-4 w-4" />
              <span>Check Activity</span>
            </button>

            {currentActivity && (
              <button
                onClick={handleSendActivity}
                className="flex items-center space-x-2 px-4 py-2 border border-blue-300 text-blue-700 rounded-md hover:bg-blue-50"
              >
                <Monitor className="h-4 w-4" />
                <span>Send to Server</span>
              </button>
            )}
          </div>

          {error && (
            <div className="mt-4 p-3 rounded-md bg-red-50 border border-red-200">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}
        </div>

        {/* Current Activity */}
        {currentActivity && (
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-lg font-medium mb-4">Current Activity</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Active Application
                  </label>
                  <div className="flex items-center space-x-2 p-3 bg-gray-50 rounded-md">
                    <Monitor className="h-4 w-4 text-gray-500" />
                    <span className="text-sm font-medium">{currentActivity.active_app}</span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Window Title
                  </label>
                  <div className="p-3 bg-gray-50 rounded-md">
                    <span className="text-sm text-gray-800">{currentActivity.window_title}</span>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Idle Time
                  </label>
                  <div className="flex items-center space-x-2 p-3 bg-gray-50 rounded-md">
                    <Clock className="h-4 w-4 text-gray-500" />
                    <span className="text-sm font-medium">
                      {formatIdleTime(currentActivity.idle_time)}
                    </span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Last Updated
                  </label>
                  <div className="p-3 bg-gray-50 rounded-md">
                    <span className="text-sm text-gray-600">
                      {new Date(currentActivity.timestamp * 1000).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {lastSyncTime && (
              <div className="mt-4 pt-4 border-t">
                <p className="text-xs text-gray-500">
                  Last synced: {formatLastSync(lastSyncTime)}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-sm font-medium text-blue-800 mb-2">How it works</h3>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• Click "Start Tracking" to begin monitoring your activity</li>
            <li>• The app tracks your active applications and idle time</li>
            <li>• Data is automatically synced every 30 seconds when tracking is active</li>
            <li>• You can manually check current activity or send data to the server</li>
            <li>• The app runs in the system tray when minimized</li>
          </ul>
        </div>
      </div>
    </div>
  );
}