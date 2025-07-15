use serde::{Deserialize, Serialize};
use std::time::Duration;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct WindowInfo {
    pub app_name: String,
    pub window_title: String,
}

#[cfg(target_os = "windows")]
mod windows {
    use super::*;
    use std::ffi::OsString;
    use std::os::windows::ffi::OsStringExt;
    use widestring::U16CString;
    use winapi::shared::windef::HWND;
    use winapi::um::processthreadsapi::{GetCurrentThreadId, OpenProcess};
    use winapi::um::psapi::GetModuleBaseNameW;
    use winapi::um::winnt::PROCESS_QUERY_INFORMATION;
    use winapi::um::winuser::{
        GetForegroundWindow, GetLastInputInfo, GetTickCount, GetWindowTextW, GetWindowThreadProcessId,
        LASTINPUTINFO,
    };

    pub fn get_active_window_info() -> Result<WindowInfo, Box<dyn std::error::Error>> {
        unsafe {
            let hwnd: HWND = GetForegroundWindow();
            if hwnd.is_null() {
                return Err("No foreground window found".into());
            }

            // Get window title
            let mut title_buffer = [0u16; 512];
            let title_len = GetWindowTextW(hwnd, title_buffer.as_mut_ptr(), title_buffer.len() as i32);
            let window_title = if title_len > 0 {
                OsString::from_wide(&title_buffer[..title_len as usize])
                    .to_string_lossy()
                    .to_string()
            } else {
                "Unknown Window".to_string()
            };

            // Get process name
            let mut process_id: u32 = 0;
            GetWindowThreadProcessId(hwnd, &mut process_id);
            
            let process_handle = OpenProcess(PROCESS_QUERY_INFORMATION, 0, process_id);
            let app_name = if !process_handle.is_null() {
                let mut process_name_buffer = [0u16; 256];
                let name_len = GetModuleBaseNameW(
                    process_handle,
                    std::ptr::null_mut(),
                    process_name_buffer.as_mut_ptr(),
                    process_name_buffer.len() as u32,
                );
                
                if name_len > 0 {
                    OsString::from_wide(&process_name_buffer[..name_len as usize])
                        .to_string_lossy()
                        .to_string()
                } else {
                    "Unknown Application".to_string()
                }
            } else {
                "Unknown Application".to_string()
            };

            Ok(WindowInfo {
                app_name,
                window_title,
            })
        }
    }

    pub fn get_idle_time() -> Result<Duration, Box<dyn std::error::Error>> {
        unsafe {
            let mut last_input_info = LASTINPUTINFO {
                cbSize: std::mem::size_of::<LASTINPUTINFO>() as u32,
                dwTime: 0,
            };

            if GetLastInputInfo(&mut last_input_info) != 0 {
                let current_tick = GetTickCount();
                let idle_time_ms = current_tick.saturating_sub(last_input_info.dwTime);
                Ok(Duration::from_millis(idle_time_ms as u64))
            } else {
                Err("Failed to get last input info".into())
            }
        }
    }
}

#[cfg(target_os = "macos")]
mod macos {
    use super::*;
    use cocoa::appkit::{NSRunningApplication, NSWorkspace};
    use cocoa::base::{id, nil};
    use cocoa::foundation::{NSAutoreleasePool, NSString};
    use core_foundation::base::TCFType;
    use core_foundation::dictionary::CFDictionary;
    use core_foundation::number::CFNumber;
    use core_foundation::string::CFString;
    use core_graphics::event::{CGEventSourceStateID, CGEventSourceGetSecondsSinceLastEventType};
    use core_graphics::event_source::CGEventSource;

    pub fn get_active_window_info() -> Result<WindowInfo, Box<dyn std::error::Error>> {
        unsafe {
            let _pool = NSAutoreleasePool::new(nil);
            let workspace: id = NSWorkspace::sharedWorkspace(nil);
            let frontmost_app: id = NSRunningApplication::frontmostApplication(workspace);
            
            if frontmost_app == nil {
                return Err("No frontmost application found".into());
            }
            
            let app_name: id = NSRunningApplication::localizedName(frontmost_app);
            let app_name_str = if app_name != nil {
                let app_name_nsstring = NSString::UTF8String(app_name);
                std::ffi::CStr::from_ptr(app_name_nsstring)
                    .to_string_lossy()
                    .to_string()
            } else {
                "Unknown Application".to_string()
            };

            // Note: Getting window title on macOS requires accessibility permissions
            // and more complex code. For now, we'll use the app name as window title.
            let window_title = app_name_str.clone();

            Ok(WindowInfo {
                app_name: app_name_str,
                window_title,
            })
        }
    }

    pub fn get_idle_time() -> Result<Duration, Box<dyn std::error::Error>> {
        let idle_seconds = unsafe {
            CGEventSourceGetSecondsSinceLastEventType(
                CGEventSourceStateID::CombinedSessionState,
                core_graphics::event::CGEventType::Null,
            )
        };
        
        Ok(Duration::from_secs_f64(idle_seconds))
    }
}

#[cfg(target_os = "linux")]
mod linux {
    use super::*;
    use std::ffi::CStr;
    use x11::xlib::*;
    use x11::xss::*;

    pub fn get_active_window_info() -> Result<WindowInfo, Box<dyn std::error::Error>> {
        unsafe {
            let display = XOpenDisplay(std::ptr::null());
            if display.is_null() {
                return Err("Cannot open X11 display".into());
            }

            let mut window: Window = 0;
            let mut revert_to: i32 = 0;
            XGetInputFocus(display, &mut window, &mut revert_to);

            let mut app_name = "Unknown Application".to_string();
            let mut window_title = "Unknown Window".to_string();

            if window != 0 {
                // Get window title
                let mut window_name: *mut i8 = std::ptr::null_mut();
                if XFetchName(display, window, &mut window_name) != 0 && !window_name.is_null() {
                    window_title = CStr::from_ptr(window_name).to_string_lossy().to_string();
                    XFree(window_name as *mut std::ffi::c_void);
                }

                // Get window class (application name)
                let mut class_hint: XClassHint = std::mem::zeroed();
                if XGetClassHint(display, window, &mut class_hint) != 0 {
                    if !class_hint.res_class.is_null() {
                        app_name = CStr::from_ptr(class_hint.res_class).to_string_lossy().to_string();
                        XFree(class_hint.res_class as *mut std::ffi::c_void);
                    }
                    if !class_hint.res_name.is_null() {
                        XFree(class_hint.res_name as *mut std::ffi::c_void);
                    }
                }
            }

            XCloseDisplay(display);

            Ok(WindowInfo {
                app_name,
                window_title,
            })
        }
    }

    pub fn get_idle_time() -> Result<Duration, Box<dyn std::error::Error>> {
        unsafe {
            let display = XOpenDisplay(std::ptr::null());
            if display.is_null() {
                return Err("Cannot open X11 display".into());
            }

            let mut info: *mut XScreenSaverInfo = XScreenSaverAllocInfo();
            if info.is_null() {
                XCloseDisplay(display);
                return Err("Cannot allocate XScreenSaverInfo".into());
            }

            let root = DefaultRootWindow(display);
            let result = XScreenSaverQueryInfo(display, root, info);
            
            let idle_time = if result != 0 {
                let idle_ms = (*info).idle;
                Duration::from_millis(idle_ms as u64)
            } else {
                Duration::from_secs(0)
            };

            XFree(info as *mut std::ffi::c_void);
            XCloseDisplay(display);

            Ok(idle_time)
        }
    }
}

// Platform-specific exports
#[cfg(target_os = "windows")]
pub use windows::*;

#[cfg(target_os = "macos")]
pub use macos::*;

#[cfg(target_os = "linux")]
pub use linux::*;

// Fallback for unsupported platforms
#[cfg(not(any(target_os = "windows", target_os = "macos", target_os = "linux")))]
pub fn get_active_window_info() -> Result<WindowInfo, Box<dyn std::error::Error>> {
    Ok(WindowInfo {
        app_name: "Unsupported Platform".to_string(),
        window_title: "Unsupported Platform".to_string(),
    })
}

#[cfg(not(any(target_os = "windows", target_os = "macos", target_os = "linux")))]
pub fn get_idle_time() -> Result<Duration, Box<dyn std::error::Error>> {
    Ok(Duration::from_secs(0))
}