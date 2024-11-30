import socket
import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import scrolledtext
import time
import threading

CONFIG_FILE = "config.json"

def save_config(server_ip, server_port, username):
    config = {"server_ip": server_ip, "server_port": server_port, "username": username}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return None

def fetch_server_files():
    """Fetch the list of uploaded files from the server."""
    try:
        config = load_config()
        if not config:
            raise ValueError("Server configuration is missing.")

        host = config["server_ip"]
        port = int(config["server_port"])

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((host, port))
            client_socket.sendall(b"LIST_FILES")
            data = client_socket.recv(4096).decode('utf-8')
            return data.split("\n") if data else []

    except Exception as e:
        messagebox.showerror("Error", f"Could not fetch server files: {e}")
        return []

# def download_file(filename):
#     """Download a selected file from the server."""
#     def download():
#         try:
#             messagebox.showinfo("Download", f"Starting download for '{filename}'...")
            
#             config = load_config()
#             if not config:
#                 raise ValueError("Server configuration is missing.")

#             host = config["server_ip"]
#             port = int(config["server_port"])

#             with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
#                 client_socket.connect((host, port))
#                 client_socket.sendall(f"DOWNLOAD|{filename}".encode('utf-8'))

#                 save_path = filedialog.asksaveasfilename(initialfile=filename, title="Save As")
#                 if not save_path:
#                     return

#                 with open(save_path, 'wb') as f:
#                     while True:
#                         chunk = client_socket.recv(1024)
#                         if not chunk:
#                             break
#                         f.write(chunk)

#                 messagebox.showinfo("Success", f"File '{filename}' downloaded successfully!")

#         except Exception as e:
#             messagebox.showerror("Error", f"File download failed: {e}")

#     threading.Thread(target=download, daemon=True).start()
def download_file(filename):
    """Download a selected file from the server with real-time feedback and immediate completion."""
    def download():
        try:
            config = load_config()
            if not config:
                raise ValueError("Server configuration is missing.")

            host = config["server_ip"]
            port = int(config["server_port"])

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((host, port))
                client_socket.sendall(f"DOWNLOAD|{filename}".encode('utf-8'))

                save_path = filedialog.asksaveasfilename(initialfile=filename, title="Save As")
                if not save_path:
                    return

                with open(save_path, 'wb') as f:
                    total_received = 0
                    while True:
                        chunk = client_socket.recv(1024)
                        if not chunk:
                            break
                        f.write(chunk)
                        total_received += len(chunk)

                        # Update the progress bar in the main thread
                        root.after(0, progress_var.set, total_received)
                        root.after(0, progress_bar.update_idletasks)

                messagebox.showinfo("Success", f"File '{filename}' downloaded successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"File download failed: {e}")
        finally:
            # Ensure progress bar is hidden after download
            client_socket.close()  # Ensure the socket is closed
            root.after(0, progress_bar.grid_remove)

    # Initialize progress bar and launch the download thread
    progress_var.set(0)
    progress_bar.grid()
    threading.Thread(target=download, daemon=True).start()

def refresh_file_list(file_list):
    """Refresh the list of files from the server."""
    files = fetch_server_files()
    file_list.delete(0, tk.END)
    for file in files:
        file_list.insert(tk.END, file)

def upload_file(progress_var, progress_bar, file_list):
    """Upload a file to the server."""
    filepath = filedialog.askopenfilename(title="Select File")
    if not filepath:
        return

    messagebox.showinfo("Upload", "Starting file upload...")

    config = load_config()
    if not config:
        messagebox.showerror("Error", "Server configuration is missing.")
        return

    server_ip = config["server_ip"]
    server_port = int(config["server_port"])

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((server_ip, server_port))
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)

            client_socket.sendall(f"UPLOAD|{filesize}|{filename}".encode('utf-8'))

            # Show progress bar
            progress_var.set(0)
            progress_bar.grid()
            progress_bar.update_idletasks()

            with open(filepath, 'rb') as f:
                sent_size = 0
                while (chunk := f.read(1024)):
                    client_socket.sendall(chunk)
                    sent_size += len(chunk)
                    progress_var.set((sent_size / filesize) * 100)
                    progress_bar.update_idletasks()

            messagebox.showinfo("Success", f"File '{filename}' uploaded successfully!")
            refresh_file_list(file_list)

    except Exception as e:
        messagebox.showerror("Error", f"File upload failed: {e}")
    finally:
        progress_bar.grid_remove()

def prompt_for_server_and_user():
    """Prompt the user for server IP, port, and their name."""
    def save_and_close():
        server_ip = ip_entry.get()
        server_port = port_entry.get()
        username = username_entry.get()

        if not server_ip or not server_port or not username:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        try:
            int(server_port)
        except ValueError:
            messagebox.showwarning("Input Error", "Port must be a number.")
            return

        save_config(server_ip, server_port, username)
        config_window.destroy()

    config_window = tk.Toplevel(root)
    config_window.title("Server and User Setup")
    config_window.geometry("300x200")
    config_window.grab_set()

    ttk.Label(config_window, text="Server IP:").grid(column=0, row=0, sticky=tk.W, pady=5)
    ip_entry = ttk.Entry(config_window, width=30)
    ip_entry.grid(column=1, row=0, pady=5)

    ttk.Label(config_window, text="Server Port:").grid(column=0, row=1, sticky=tk.W, pady=5)
    port_entry = ttk.Entry(config_window, width=30)
    port_entry.grid(column=1, row=1, pady=5)

    ttk.Label(config_window, text="Your Name:").grid(column=0, row=2, sticky=tk.W, pady=5)
    username_entry = ttk.Entry(config_window, width=30)
    username_entry.grid(column=1, row=2, pady=5)

    save_button = ttk.Button(config_window, text="Save", command=save_and_close)
    save_button.grid(column=0, row=3, columnspan=2, pady=20)

# GUI Setup
root = tk.Tk()
root.title("File Upload & Download Client")
root.geometry("600x700")

frame = ttk.Frame(root, padding="20")
frame.pack(fill=tk.BOTH, expand=True)

# Greeting
config = load_config()
username = config["username"] if config else "User"
ttk.Label(frame, text=f"Hello, {username}!", font=("Helvetica", 16)).grid(column=0, row=0, sticky=tk.W, pady=10)

# File List with Scrollbar
ttk.Label(frame, text="Files on Server:").grid(column=0, row=1, sticky=tk.W)
file_list_frame = ttk.Frame(frame)
file_list_frame.grid(column=0, row=2, columnspan=2, pady=10)

file_list_scrollbar = ttk.Scrollbar(file_list_frame, orient=tk.VERTICAL)
file_list = tk.Listbox(file_list_frame, height=15, width=60, selectmode=tk.SINGLE, yscrollcommand=file_list_scrollbar.set)
file_list_scrollbar.config(command=file_list.yview)

file_list.pack(side=tk.LEFT, fill=tk.BOTH)
file_list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Buttons
refresh_button = ttk.Button(frame, text="Refresh", command=lambda: refresh_file_list(file_list))
refresh_button.grid(column=0, row=3, pady=10)

download_button = ttk.Button(frame, text="Download", command=lambda: download_file(file_list.get(tk.ACTIVE)))
download_button.grid(column=1, row=3, pady=10)

upload_button = ttk.Button(frame, text="Upload File", command=lambda: upload_file(progress_var, progress_bar, file_list))
upload_button.grid(column=0, row=4, columnspan=2, pady=20)

# Progress Bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate", variable=progress_var)
progress_bar.grid(column=0, row=5, columnspan=2, pady=10)
progress_bar.grid_remove()

if not load_config():
    prompt_for_server_and_user()
else:
    refresh_file_list(file_list)

root.mainloop()
