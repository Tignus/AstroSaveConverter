import os
import sys
import json
import socket
import webbrowser
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

# Import core packages
from cogs import AstroMicrosoftSaveFolder
from cogs import AstroSteamSaveFolder
from cogs.AstroSave import AstroSave
from cogs.AstroSaveContainer import AstroSaveContainer as Container
import AstroSaveScenario as Scenario
import utils
from cogs import AstroLogging as Logger

# Global state for GUI session
state = {
    "xbox_paths": [],
    "xbox_selected_path": "",
    "steam_path": "",
}

def auto_detect_paths():
    """Detect default Xbox and Steam paths."""
    # 1. Xbox Detection
    try:
        state["xbox_paths"] = AstroMicrosoftSaveFolder.find_microsoft_save_folders()
        if state["xbox_paths"] and not state["xbox_selected_path"]:
            state["xbox_selected_path"] = state["xbox_paths"][0]
    except Exception as e:
        Logger.logPrint(f"Xbox folders auto-detection failed: {e}", "debug")
        state["xbox_paths"] = []
        state["xbox_selected_path"] = ""

    # 2. Steam Detection
    try:
        state["steam_path"] = AstroSteamSaveFolder.get_steam_save_folder()
        # Verify it exists
        if not os.path.exists(state["steam_path"]):
            state["steam_path"] = ""
    except Exception as e:
        Logger.logPrint(f"Steam folder auto-detection failed: {e}", "debug")
        state["steam_path"] = ""

def get_xbox_saves():
    """List saves in the active Xbox path."""
    path = state["xbox_selected_path"]
    if not path or not os.path.exists(path):
        return []
    
    try:
        containers_list = Container.get_containers_list(path)
        if not containers_list:
            return []
        
        # Read the first container file (usually container.1)
        container_url = utils.join_paths(path, containers_list[0])
        container = Container(container_url)
        
        saves_data = []
        for idx, save in enumerate(container.save_list):
            # Extract date from name if possible (format: Name$YYYY.MM.dd-HH.mm.ss)
            parts = save.name.split("$")
            clean_name = parts[0]
            date_str = "Inconnue"
            if len(parts) > 1:
                try:
                    dt = datetime.strptime(parts[1], "%Y.%m.%d-%H.%M.%S")
                    date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    date_str = parts[1]
                    
            saves_data.append({
                "index": idx,
                "name": save.name,
                "clean_name": clean_name,
                "date": date_str,
                "chunks_count": len(save.chunks_names)
            })
        return saves_data
    except Exception as e:
        Logger.logPrint(f"Failed to load Xbox saves: {e}", "error")
        return []

def get_steam_saves():
    """List saves in the active Steam path."""
    path = state["steam_path"]
    if not path or not os.path.exists(path):
        return []
    
    try:
        steamsave_files_list = AstroSave.get_steamsaves_list(path)
        saves_list = AstroSave.init_saves_list_from(steamsave_files_list)
        
        saves_data = []
        for idx, save in enumerate(saves_list):
            full_path = utils.join_paths(path, steamsave_files_list[idx])
            date_str = "Inconnue"
            try:
                mtime = os.path.getmtime(full_path)
                dt = datetime.fromtimestamp(mtime)
                date_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass
                
            saves_data.append({
                "index": idx,
                "name": save.name,
                "date": date_str,
                "filename": steamsave_files_list[idx]
            })
        return saves_data
    except Exception as e:
        Logger.logPrint(f"Failed to load Steam saves: {e}", "error")
        return []

def get_status_json():
    """Assemble current system status."""
    return {
        "xbox_paths": state["xbox_paths"],
        "xbox_selected_path": state["xbox_selected_path"],
        "xbox_saves": get_xbox_saves(),
        "steam_path": state["steam_path"],
        "steam_saves": get_steam_saves()
    }

class WebGUIHandler(BaseHTTPRequestHandler):
    """Zero-dependency HTTP Handler for Web GUI."""
    
    def log_message(self, format, *args):
        # Prevent default stdout pollution, redirect to debug logs
        Logger.logPrint(format % args, "debug")

    def send_json(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def is_request_secure(self) -> bool:
        """Validate request headers to prevent CSRF and DNS-rebinding attacks."""
        host = self.headers.get("Host", "")
        if not (host.startswith("127.0.0.1:") or host == "127.0.0.1" or
                host.startswith("localhost:") or host == "localhost"):
            Logger.logPrint(f"Security Warning: Blocked request with invalid Host header: {host}", "warning")
            return False

        origin = self.headers.get("Origin")
        if origin:
            if not (origin.startswith("http://127.0.0.1:") or origin == "http://127.0.0.1" or
                    origin.startswith("http://localhost:") or origin == "http://localhost"):
                Logger.logPrint(f"Security Warning: Blocked request with invalid Origin header: {origin}", "warning")
                return False

        referer = self.headers.get("Referer")
        if referer:
            if not (referer.startswith("http://127.0.0.1:") or referer == "http://127.0.0.1" or
                    referer.startswith("http://localhost:") or referer == "http://localhost"):
                Logger.logPrint(f"Security Warning: Blocked request with invalid Referer header: {referer}", "warning")
                return False

        return True

    def send_forbidden(self):
        self.send_response(403)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Forbidden: Request origin validation failed.")

    def do_GET(self):
        if not self.is_request_secure():
            self.send_forbidden()
            return
            
        # 1. API Endpoints
        if self.path == "/api/status":
            self.send_json(get_status_json())
            return
            
        # 2. Static Files
        if self.path in ("/", "/index.html"):
            # Resolve directory bundle logic (PyInstaller compatibility)
            if hasattr(sys, '_MEIPASS'):
                web_dir = os.path.join(sys._MEIPASS, 'web')
            else:
                web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')
                
            html_path = os.path.join(web_dir, 'index.html')
            
            if os.path.exists(html_path):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(html_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Frontend files missing")
            return

        if self.path == "/logo.ico":
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, 'astroconverterlogo.ico')
            else:
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'astroconverterlogo.ico')
                
            if os.path.exists(icon_path):
                self.send_response(200)
                self.send_header("Content-Type", "image/x-icon")
                self.end_headers()
                with open(icon_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Logo file not found")
            return
            
        self.send_error(404, "Not Found")

    def do_POST(self):
        if not self.is_request_secure():
            self.send_forbidden()
            return
            
        # Parse JSON body
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b""
        
        try:
            body = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            body = {}

        if self.path == "/api/select_path":
            folder_type = body.get("type")
            folder_path = body.get("path")
            
            if not folder_path or not os.path.exists(folder_path):
                self.send_json({"success": False, "error": "The specified folder does not exist."}, 400)
                return
                
            if folder_type == "xbox":
                state["xbox_selected_path"] = folder_path
                # Add to xbox_paths if not already there
                if folder_path not in state["xbox_paths"]:
                    state["xbox_paths"].append(folder_path)
            elif folder_type == "steam":
                state["steam_path"] = folder_path
            else:
                self.send_json({"success": False, "error": "Unknown folder type."}, 400)
                return
                
            self.send_json({"success": True, "status": get_status_json()})
            return

        elif self.path == "/api/browse_path":
            folder_type = body.get("type")
            
            # Open native OS folder selector using Tkinter
            try:
                import tkinter as tk
                from tkinter import filedialog
                
                root = tk.Tk()
                root.withdraw() # hide root
                root.attributes('-topmost', True) # force to front
                
                initial_dir = state["xbox_selected_path"] if folder_type == "xbox" else state["steam_path"]
                if not initial_dir or not os.path.exists(initial_dir):
                    initial_dir = os.path.expanduser("~")
                    
                selected_dir = filedialog.askdirectory(
                    title="Select the Astroneer saves folder",
                    initialdir=initial_dir
                )
                root.destroy()
                
                if selected_dir:
                    selected_dir = os.path.normpath(selected_dir)
                    if folder_type == "xbox":
                        state["xbox_selected_path"] = selected_dir
                        if selected_dir not in state["xbox_paths"]:
                            state["xbox_paths"].append(selected_dir)
                    else:
                        state["steam_path"] = selected_dir
                    self.send_json({"success": True, "path": selected_dir, "status": get_status_json()})
                else:
                    self.send_json({"success": False, "error": "Selection cancelled."})
            except Exception as e:
                Logger.logPrint(f"Failed browsing directory: {e}", "error")
                self.send_json({"success": False, "error": f"Error opening folder selector: {str(e)}"}, 500)
            return

        elif self.path == "/api/detect_single":
            folder_type = body.get("type") # 'xbox' or 'steam'
            
            if folder_type == "xbox":
                try:
                    paths = AstroMicrosoftSaveFolder.find_microsoft_save_folders()
                    if paths:
                        selected_path = paths[0]
                        state["xbox_selected_path"] = selected_path
                        state["xbox_paths"] = paths
                        self.send_json({"success": True, "path": selected_path, "status": get_status_json()})
                    else:
                        self.send_json({"success": False, "error": "No Microsoft save folder detected automatically."})
                except Exception as e:
                    self.send_json({"success": False, "error": "No Microsoft save folder detected automatically."})
            elif folder_type == "steam":
                try:
                    steam_path = AstroSteamSaveFolder.get_steam_save_folder()
                    if steam_path and os.path.exists(steam_path):
                        state["steam_path"] = steam_path
                        self.send_json({"success": True, "path": steam_path, "status": get_status_json()})
                    else:
                        self.send_json({"success": False, "error": "No Steam save folder detected automatically."})
                except Exception as e:
                    self.send_json({"success": False, "error": "No Steam save folder detected automatically."})
            else:
                self.send_json({"success": False, "error": "Invalid type."}, 400)
            return

        elif self.path == "/api/convert":
            direction = body.get("direction")
            save_indexes = body.get("save_indexes", [])
            renames = body.get("renames", {})
            
            if not save_indexes:
                self.send_json({"success": False, "error": "No saves selected."}, 400)
                return

            try:
                if direction == "win2steam":
                    # Xbox -> Steam
                    xbox_path = state["xbox_selected_path"]
                    steam_path = state["steam_path"]
                    
                    if not xbox_path or not steam_path:
                        self.send_json({"success": False, "error": "Invalid save folders."}, 400)
                        return
                        
                    try:
                        containers_list = Container.get_containers_list(xbox_path)
                    except FileNotFoundError:
                        self.send_json({"success": False, "error": "No Xbox save container found in the selected folder."}, 400)
                        return
                        
                    if not containers_list:
                        self.send_json({"success": False, "error": "No Xbox save profiles found in the selected folder."}, 400)
                        return
                    container_url = utils.join_paths(xbox_path, containers_list[0])
                    container = Container(container_url)
                    
                    utils.make_dir_if_doesnt_exists(steam_path)
                    
                    for idx in save_indexes:
                        if idx < 0 or idx >= len(container.save_list):
                            self.send_json({"success": False, "error": f"Invalid Xbox save index: {idx}"}, 400)
                            return
                        save = container.save_list[idx]
                        # Apply rename if requested
                        if str(idx) in renames:
                            save.rename(renames[str(idx)])
                            
                        # Convert and export
                        Scenario.export_save_to_steam(save, xbox_path, steam_path)
                        Logger.logPrint(f"Xbox Save {save.name} exported to Steam successfully.")
                        
                elif direction == "steam2win":
                    # Steam -> Xbox
                    xbox_path = state["xbox_selected_path"]
                    steam_path = state["steam_path"]
                    
                    if not xbox_path or not steam_path:
                        self.send_json({"success": False, "error": "Invalid save folders."}, 400)
                        return
                        
                    # 1. Perform safety backup of Xbox folder
                    desktop = utils.get_windows_desktop_path()
                    backup_root = utils.join_paths(desktop, utils.create_folder_name("MicrosoftAstroneerSavesBackup"))
                    
                    # Search all xbox folders to backup everything
                    try:
                        folders = AstroMicrosoftSaveFolder.find_microsoft_save_folders()
                        AstroMicrosoftSaveFolder.backup_microsoft_save_folders(folders, backup_root)
                        Logger.logPrint(f"Xbox saves backed up to Desktop: {backup_root}")
                    except Exception as e:
                        # Continue even if backup fails but log it
                        Logger.logPrint(f"Backup warning: {e}", "warning")
                        
                    # 2. Convert each steam save
                    try:
                        steamsave_files_list = AstroSave.get_steamsaves_list(steam_path)
                    except FileNotFoundError:
                        self.send_json({"success": False, "error": "No Steam save files found in the selected folder."}, 400)
                        return
                    saves_list = AstroSave.init_saves_list_from(steamsave_files_list)
                    
                    for idx in save_indexes:
                        if idx < 0 or idx >= len(saves_list):
                            self.send_json({"success": False, "error": f"Invalid Steam save index: {idx}"}, 400)
                            return
                        save = saves_list[idx]
                        if str(idx) in renames:
                            save.rename(renames[str(idx)])
                            
                        original_save_full_path = utils.join_paths(steam_path, steamsave_files_list[idx])
                        Scenario.export_save_to_xbox(save, original_save_full_path, xbox_path)
                        Logger.logPrint(f"Steam Save {save.name} exported to Xbox successfully.")
                else:
                    self.send_json({"success": False, "error": "Invalid conversion direction."}, 400)
                    return
                    
                self.send_json({"success": True})
            except Exception as e:
                Logger.logPrint(f"Conversion failed: {e}", "error")
                Logger.logPrint("", "exception")
                self.send_json({"success": False, "error": f"Error during conversion: {str(e)}"}, 500)
            return

        elif self.path == "/api/shutdown":
            self.send_json({"success": True})
            
            # Shut down server process gracefully after 500ms
            def self_destruct():
                time.sleep(0.5)
                Logger.logPrint("Shutdown requested by GUI. Closing server.")
                os._exit(0)
                
            threading.Thread(target=self_destruct).start()
            return
            
        self.send_error(404, "Not Found")

def start_gui():
    """Launch HTTP Server and open browser."""
    # Auto detect folders first
    auto_detect_paths()
    
    host = "127.0.0.1"
    try:
        server = HTTPServer((host, 0), WebGUIHandler)
    except Exception as e:
        Logger.logPrint(f"Could not bind to {host}, falling back to localhost: {e}", "warning")
        host = "localhost"
        server = HTTPServer((host, 0), WebGUIHandler)
        
    port = server.server_address[1]
    url = f"http://{host}:{port}"
    
    # Print clean instructions to console
    print("\n" + "=" * 70)
    print(" The AstroSaveConverter application will open in your web browser.")
    print(" If the page does not open automatically, please visit this link:")
    print(f"   {url}")
    print("\n Once finished, you can close this window to exit.")
    print("=" * 70 + "\n")
    
    # Open default browser
    webbrowser.open(url)
    
    # Run server (this blocks until process terminates or /api/shutdown is triggered)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
