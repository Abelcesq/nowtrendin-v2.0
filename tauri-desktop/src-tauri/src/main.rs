// Now TrendIn desktop shell — loads the Expo web bundle (frontendDist) in a
// native WebView2 window. All app logic lives in the web bundle; this binary
// only provides the window.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    tauri::Builder::default()
        .run(tauri::generate_context!())
        .expect("error while running Now TrendIn desktop");
}
