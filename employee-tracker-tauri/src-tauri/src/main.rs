// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};
use tauri::{CustomMenuItem, Manager, SystemTray, SystemTrayEvent, SystemTrayMenu, SystemTrayMenuItem};

mod system_monitor;
use system_monitor::{get_active_window_info, get_idle_time, WindowInfo};

#[derive(Debug, Serialize, Deserialize, Clone)]
struct ActivityData {
    active_app: String,
    window_title: String,
    idle_time: f64,
    timestamp: i64,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
struct AppState {
    is_tracking: bool,
    user_id: Option<String>,
    team_id: Option<String>,
    token: Option<String>,
    last_activity: Option<ActivityData>,
}

impl Default for AppState {
    fn default() -> Self {
        Self {
            is_tracking: false,
            user_id: None,
            team_id: None,
            token: None,
            last_activity: None,
        }
    }
}

// Tauri commands
#[tauri::command]
async fn start_tracking(
    state: tauri::State<'_, Arc<Mutex<AppState>>>,
    user_id: String,
    team_id: String,
    token: String,
) -> Result<String, String> {
    let mut app_state = state.lock().map_err(|e| e.to_string())?;
    app_state.is_tracking = true;
    app_state.user_id = Some(user_id);
    app_state.team_id = Some(team_id);
    app_state.token = Some(token);
    
    Ok("Tracking started".to_string())
}

#[tauri::command]
async fn stop_tracking(state: tauri::State<'_, Arc<Mutex<AppState>>>) -> Result<String, String> {
    let mut app_state = state.lock().map_err(|e| e.to_string())?;
    app_state.is_tracking = false;
    app_state.user_id = None;
    app_state.team_id = None;
    app_state.token = None;
    
    Ok("Tracking stopped".to_string())
}

#[tauri::command]
async fn get_current_activity() -> Result<ActivityData, String> {
    let window_info = get_active_window_info().map_err(|e| e.to_string())?;
    let idle_time = get_idle_time().map_err(|e| e.to_string())?;
    
    Ok(ActivityData {
        active_app: window_info.app_name,
        window_title: window_info.window_title,
        idle_time: idle_time.as_secs_f64(),
        timestamp: chrono::Utc::now().timestamp(),
    })
}

#[tauri::command]
async fn send_activity_data(
    state: tauri::State<'_, Arc<Mutex<AppState>>>,
    activity: ActivityData,
) -> Result<String, String> {
    let app_state = state.lock().map_err(|e| e.to_string())?;
    
    if !app_state.is_tracking {
        return Err("Tracking is not active".to_string());
    }
    
    let user_id = app_state.user_id.as_ref().ok_or("User ID not set")?;
    let team_id = app_state.team_id.as_ref().ok_or("Team ID not set")?;
    let token = app_state.token.as_ref().ok_or("Token not set")?;
    
    // Create HTTP client
    let client = reqwest::Client::new();
    
    // Prepare the data payload
    let payload = serde_json::json!({
        "userId": user_id,
        "activeApp": activity.active_app,
        "windowTitle": activity.window_title,
        "idleTime": activity.idle_time,
        "productiveHours": 0.0, // Will be calculated on frontend
        "unproductiveHours": 0.0, // Will be calculated on frontend
        "goalsCompleted": 0
    });
    
    // Send to backend
    let response = client
        .post(&format!("https://productivityflow-backend.onrender.com/api/teams/{}/activity", team_id))
        .header("Authorization", &format!("Bearer {}", token))
        .header("Content-Type", "application/json")
        .json(&payload)
        .send()
        .await
        .map_err(|e| e.to_string())?;
    
    if response.status().is_success() {
        Ok("Activity data sent successfully".to_string())
    } else {
        Err(format!("Failed to send activity data: {}", response.status()))
    }
}

fn create_system_tray() -> SystemTray {
    let show = CustomMenuItem::new("show".to_string(), "Show");
    let hide = CustomMenuItem::new("hide".to_string(), "Hide");
    let quit = CustomMenuItem::new("quit".to_string(), "Quit");
    
    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_item(hide)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(quit);
    
    SystemTray::new().with_menu(tray_menu)
}

async fn start_activity_monitoring(app_handle: tauri::AppHandle, state: Arc<Mutex<AppState>>) {
    let mut interval = tokio::time::interval(Duration::from_secs(30)); // Check every 30 seconds
    
    loop {
        interval.tick().await;
        
        let should_track = {
            let app_state = state.lock().unwrap();
            app_state.is_tracking
        };
        
        if should_track {
            match get_current_activity().await {
                Ok(activity) => {
                    // Update the last activity in state
                    {
                        let mut app_state = state.lock().unwrap();
                        app_state.last_activity = Some(activity.clone());
                    }
                    
                    // Emit event to frontend
                    let _ = app_handle.emit_all("activity-update", &activity);
                    
                    // Optionally send to backend automatically
                    // let _ = send_activity_data(tauri::State::from(&state), activity).await;
                }
                Err(e) => {
                    eprintln!("Error getting activity: {}", e);
                }
            }
        }
    }
}

fn main() {
    let state = Arc::new(Mutex::new(AppState::default()));
    let state_clone = state.clone();
    
    tauri::Builder::default()
        .manage(state)
        .system_tray(create_system_tray())
        .on_system_tray_event(|app, event| match event {
            SystemTrayEvent::LeftClick { .. } => {
                let window = app.get_window("main").unwrap();
                window.show().unwrap();
                window.set_focus().unwrap();
            }
            SystemTrayEvent::MenuItemClick { id, .. } => {
                match id.as_str() {
                    "show" => {
                        let window = app.get_window("main").unwrap();
                        window.show().unwrap();
                        window.set_focus().unwrap();
                    }
                    "hide" => {
                        let window = app.get_window("main").unwrap();
                        window.hide().unwrap();
                    }
                    "quit" => {
                        std::process::exit(0);
                    }
                    _ => {}
                }
            }
            _ => {}
        })
        .invoke_handler(tauri::generate_handler![
            start_tracking,
            stop_tracking,
            get_current_activity,
            send_activity_data
        ])
        .setup(|app| {
            let app_handle = app.handle();
            
            // Start the activity monitoring in a background task
            tauri::async_runtime::spawn(async move {
                start_activity_monitoring(app_handle, state_clone).await;
            });
            
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}