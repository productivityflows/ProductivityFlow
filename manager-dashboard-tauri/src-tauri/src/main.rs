// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::sync::{Arc, Mutex};


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
async fn fetch_team_data() -> Result<String, String> {
    // Simulate fetching team data from a server
    tokio::time::sleep(tokio::time::Duration::from_millis(500)).await;
    Ok("Team data fetched successfully".to_string())
}

#[tauri::command]
async fn check_for_updates() -> Result<String, String> {
    // Simulate checking for updates
    tokio::time::sleep(tokio::time::Duration::from_millis(300)).await;
    Ok("No updates available".to_string())
}

fn main() {
    let state = Arc::new(Mutex::new(AppState::default()));
    
    tauri::Builder::default()
        .manage(state)
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