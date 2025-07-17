// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};
use tauri::{CustomMenuItem, Manager, SystemTray, SystemTrayEvent, SystemTrayMenu, SystemTrayMenuItem};

#[derive(Debug, Serialize, Deserialize, Clone)]
struct AppState {
    is_authenticated: bool,
    user_name: Option<String>,
    organization: Option<String>,
}

impl Default for AppState {
    fn default() -> Self {
        Self {
            is_authenticated: false,
            user_name: None,
            organization: None,
        }
    }
}

// Tauri commands
#[tauri::command]
async fn authenticate_manager(
    state: tauri::State<'_, Arc<Mutex<AppState>>>,
    user_name: String,
    organization: String,
) -> Result<String, String> {
    let mut app_state = state.lock().map_err(|e| e.to_string())?;
    app_state.is_authenticated = true;
    app_state.user_name = Some(user_name);
    app_state.organization = Some(organization);
    
    Ok("Authentication successful".to_string())
}

#[tauri::command]
async fn logout_manager(state: tauri::State<'_, Arc<Mutex<AppState>>>) -> Result<String, String> {
    let mut app_state = state.lock().map_err(|e| e.to_string())?;
    app_state.is_authenticated = false;
    app_state.user_name = None;
    app_state.organization = None;
    
    Ok("Logged out successfully".to_string())
}

#[tauri::command]
async fn get_app_state(state: tauri::State<'_, Arc<Mutex<AppState>>>) -> Result<AppState, String> {
    let app_state = state.lock().map_err(|e| e.to_string())?;
    Ok(app_state.clone())
}

#[tauri::command]
async fn fetch_team_data(team_id: String) -> Result<String, String> {
    // This is a placeholder function for fetching team data
    // In a real implementation, this would make HTTP requests to the backend
    let client = reqwest::Client::new();
    
    let response = client
        .get(&format!("https://productivityflow-backend.onrender.com/api/teams/{}/stats", team_id))
        .send()
        .await
        .map_err(|e| e.to_string())?;
    
    if response.status().is_success() {
        let text = response.text().await.map_err(|e| e.to_string())?;
        Ok(text)
    } else {
        Err(format!("Failed to fetch team data: {}", response.status()))
    }
}

#[tauri::command]
async fn check_for_updates(app_handle: tauri::AppHandle) -> Result<String, String> {
    match app_handle.updater().check().await {
        Ok(update) => {
            if update.is_update_available() {
                match update.download_and_install().await {
                    Ok(_) => {
                        app_handle.restart();
                        Ok("Update installed, restarting application".to_string())
                    }
                    Err(e) => Err(format!("Failed to install update: {}", e)),
                }
            } else {
                Ok("No updates available".to_string())
            }
        }
        Err(e) => Err(format!("Failed to check for updates: {}", e)),
    }
}

fn create_system_tray() -> SystemTray {
    let show = CustomMenuItem::new("show".to_string(), "Show Dashboard");
    let hide = CustomMenuItem::new("hide".to_string(), "Hide Dashboard");
    let quit = CustomMenuItem::new("quit".to_string(), "Quit");
    
    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_item(hide)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(quit);
    
    SystemTray::new().with_menu(tray_menu)
}

fn main() {
    let state = Arc::new(Mutex::new(AppState::default()));
    
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
            authenticate_manager,
            logout_manager,
            get_app_state,
            fetch_team_data,
            check_for_updates
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}