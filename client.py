import socket
import os
import time
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

CONFIG_FILE = "config.json"
uploaded_files = []

def save_config(server_ip, server_port, username):
    config = {"server_ip": server_ip, "server_port": server_port, "username": username}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return None

def send_file(client_socket, filepath, progress_var, progress_bar, uploaded_files_list):
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)

    try:
        client_socket.sendall(f"{filesize}|{filename}".encode('utf-8'))
        time.sleep(5)

        with open(filepath, 'rb') as f:
            sent_size = 0
            while (chunk := f.read(1024)):
                client_socket.sendall(chunk)
                sent_size += len(chunk)
                progress = (sent_size / filesize) * 100
                progress_var.set(progress)
                progress_bar.update_idletasks()

        uploaded_files.append(filename)
        uploaded_files_list.insert(tk.END, filename)
        messagebox.showinfo("Success", f"File '{filename}' uploaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"File upload failed: {e}")

def start_client(host, port, filepath, progress_var, progress_bar, uploaded_files_list):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((host, port))
            send_file(client_socket, filepath, progress_var, progress_bar, uploaded_files_list)
    except Exception as e:
        messagebox.showerror("Error", f"Could not connect to server: {e}")
    finally:
        progress_bar.grid_remove()  # Hide progress bar after completion

def upload_file(progress_var, progress_bar, uploaded_files_list):
    filepath = filedialog.askopenfilename(title="Select File")
    if not filepath:
        return

    config = load_config()
    if config:
        server_ip = config["server_ip"]
        server_port = int(config["server_port"])

        progress_var.set(0)
        progress_bar.grid()  # Show progress bar
        progress_bar.update_idletasks()

        start_client(server_ip, server_port, filepath, progress_var, progress_bar, uploaded_files_list)

def prompt_for_server_and_user():
    def save_and_close():
        server_ip = ip_entry.get()
        server_port = port_entry.get()
        username = username_entry.get()

        if not server_ip or not server_port or not username:
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        try:
            int(server_port)  # Validate port is numeric
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

# Build the GUI
root = tk.Tk()
root.title("File Upload Client")
root.geometry("400x400")
root.resizable(False, False)

frame = ttk.Frame(root, padding="20")
frame.pack(fill=tk.BOTH, expand=True)

# Uploaded Files List
ttk.Label(frame, text="Uploaded Files:").grid(column=0, row=0, sticky=tk.W)
uploaded_files_list = tk.Listbox(frame, height=10)
uploaded_files_list.grid(column=0, row=1, columnspan=2, pady=10)

# Upload Button
upload_button = ttk.Button(frame, text="Upload File", command=lambda: upload_file(progress_var, progress_bar, uploaded_files_list))
upload_button.grid(column=0, row=2, columnspan=2, pady=20)

# Progress Bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate", variable=progress_var)
progress_bar.grid(column=0, row=3, columnspan=2, pady=10)
progress_bar.grid_remove()  # Hidden by default

# Prompt for server and user setup if config does not exist
if not load_config():
    prompt_for_server_and_user()

root.mainloop()
