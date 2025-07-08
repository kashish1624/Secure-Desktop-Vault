# 📁 dashboard.py - Secure Vault Dashboard

# ================= Imports =================
import tkinter as tk  # GUI components
from tkinter import ttk, filedialog, messagebox  # GUI widgets, file chooser, popup alerts
import os, sys, shutil, sqlite3, subprocess  # OS handling, file ops, DB, open files
from datetime import datetime  # For file timestamps
import humanize  # To display file sizes in readable format
from PIL import Image, ImageTk  # For displaying file icons
from crypto_util import encrypt_file, decrypt_file  # Encryption functions

# ========== Helper Functions ==========
def resource_path(relative_path):
    # Returns correct path of file (for .exe compatibility)
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ========== File Icon Handling ==========
ICON_SIZE = (18, 18)  # Icon size for files
icon_cache = {}  # Store loaded icons to avoid reloading

def get_file_icon(extension):
    # Returns appropriate icon based on file extension
    if extension in icon_cache:
        return icon_cache[extension]

    icon_path = {
        "pdf": "icons/pdf.png",
        "doc": "icons/doc.png",
        "docx": "icons/doc.png",
        "xlsx": "icons/excel.png",
        "mp4": "icons/video.png",
        "mp3": "icons/audio.png",
        "zip": "icons/zip.png",
        "enc": "icons/lock.png",
    }.get(extension, "icons/file.png")

    try:
        image = Image.open(resource_path(icon_path))
        image = image.resize(ICON_SIZE, Image.Resampling.LANCZOS)
        icon = ImageTk.PhotoImage(image)
        icon_cache[extension] = icon
        return icon
    except Exception as e:
        print(f"[Icon Load Error] {extension}: {e}")
        return None

# ========== Main Dashboard Window ==========
def open_dashboard_window(username):
    global dashboard, VAULT_FOLDER, file_table, search_var, top_toolbar, bottom_toolbar, search_frame

    current_user = username
    VAULT_FOLDER = os.path.join("vault", current_user)  # User's personal folder
    os.makedirs(VAULT_FOLDER, exist_ok=True)  # Create if doesn't exist

    dashboard = tk.Tk()
    dashboard.title("\U0001F510 Secure Desktop Vault")
    dashboard.geometry("950x600")

    try:
        dashboard.iconbitmap(resource_path("icons/vault.ico"))  # Set app icon
    except Exception as e:
        print("[Window Icon Error]:", e)

    # ===== Top Toolbar =====
    top_toolbar = tk.Frame(dashboard)
    top_toolbar.pack(pady=5)

    tk.Button(top_toolbar, text="\U0001F510 Upload & Encrypt", command=lambda: upload_file()).pack(side=tk.LEFT, padx=5)
    tk.Button(top_toolbar, text="\U0001F513 Decrypt", command=lambda: decrypt_selected()).pack(side=tk.LEFT, padx=5)
    tk.Button(top_toolbar, text="\U0001F4C2 Open", command=lambda: open_selected()).pack(side=tk.LEFT, padx=5)
    tk.Button(top_toolbar, text="\U0001F5D1\uFE0F Delete", command=lambda: delete_selected()).pack(side=tk.LEFT, padx=5)
    tk.Button(top_toolbar, text="\u2B07\uFE0F Download", command=lambda: download_selected()).pack(side=tk.LEFT, padx=5)

    # ===== Search Bar =====
    search_var = tk.StringVar()
    search_var.trace("w", lambda *args: view_files())  # Auto update when text typed

    search_frame = tk.Frame(dashboard)
    search_frame.pack(pady=2)
    tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
    tk.Entry(search_frame, textvariable=search_var, width=50).pack(side=tk.LEFT, padx=5)

    # ===== Sort Dropdown =====
    bottom_toolbar = tk.Frame(dashboard)
    bottom_toolbar.pack(pady=2)

    sort_options = [
        "Name (A-Z)", "Name (Z-A)",
        "Date Modified (Newest)", "Date Modified (Oldest)",
        "Size (Largest)", "Size (Smallest)",
        "Type (A-Z)", "Type (Z-A)"
    ]
    sort_by_var = tk.StringVar()
    sort_by_var.set("\u2B07\uFE0F Sort By")
    sort_menu = ttk.Combobox(bottom_toolbar, textvariable=sort_by_var, values=sort_options, state="readonly", width=20)
    sort_menu.pack(side=tk.RIGHT, padx=5)
    sort_menu.bind("<<ComboboxSelected>>", lambda event: sort_files(sort_by_var.get()))

    # ===== File Display Table =====
    file_table = ttk.Treeview(dashboard, columns=("Type", "Modified", "Size"))
    file_table.heading("#0", text="Name", anchor="w")
    file_table.heading("Type", text="Type")
    file_table.heading("Modified", text="Date Modified")
    file_table.heading("Size", text="Size")

    file_table.column("#0", anchor="w", width=320)
    file_table.column("Type", anchor="center", width=100)
    file_table.column("Modified", anchor="center", width=140)
    file_table.column("Size", anchor="center", width=100)
    file_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # ===== Bottom Buttons =====
    tk.Button(bottom_toolbar, text="\U0001F3A8 Theme", command=lambda: toggle_theme()).pack(side=tk.LEFT, padx=5)
    tk.Button(bottom_toolbar, text="\U0001F501 Refresh", command=lambda: view_files()).pack(side=tk.LEFT, padx=5)
    tk.Button(bottom_toolbar, text="\U0001F512 Logout", command=lambda: logout()).pack(side=tk.RIGHT, padx=5)

    # ===== Functional Logic =====

    def upload_file():
        filepath = filedialog.askopenfilename()  # Let user pick file
        if filepath:
            filename = os.path.basename(filepath)
            enc_filename = filename.replace(" ", "_") + ".enc"
            destination = os.path.join(VAULT_FOLDER, enc_filename)
            try:
                shutil.copy(filepath, destination)  # Copy file to vault
                encrypt_file(destination)  # Encrypt it
                messagebox.showinfo("Success", f"Encrypted: {enc_filename}")
                view_files()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def decrypt_selected():
        selected = file_table.selection()
        if selected:
            enc_file = file_table.item(selected[0])['text']
            if not enc_file.endswith(".enc"):
                messagebox.showwarning("Warning", "Not an encrypted file.")
                return
            decrypted_name = enc_file[:-4]  # Remove .enc
            enc_path = os.path.join(VAULT_FOLDER, enc_file)
            decrypted_path = os.path.join(VAULT_FOLDER, decrypted_name)
            if os.path.exists(decrypted_path):
                messagebox.showwarning("Exists", f"{decrypted_name} already exists.")
                return
            try:
                decrypt_file(enc_path, decrypted_path)
                messagebox.showinfo("Decrypted", f"Saved as: {decrypted_name}")
                view_files()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def delete_selected():
        selected = file_table.selection()
        for item in selected:
            file = file_table.item(item)['text']
            try:
                os.remove(os.path.join(VAULT_FOLDER, file))
            except Exception as e:
                messagebox.showerror("Error", str(e))
        view_files()

    def open_selected():
        selected = file_table.selection()
        if selected:
            filepath = os.path.join(VAULT_FOLDER, file_table.item(selected[0])['text'])
            try:
                if os.name == 'nt':
                    os.startfile(filepath)  # Windows open
                else:
                    subprocess.call(('xdg-open', filepath))  # Linux/macOS
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def download_selected():
        selected = file_table.selection()
        for item in selected:
            file = file_table.item(item)['text']
            dest = filedialog.asksaveasfilename(initialfile=file)
            if dest:
                shutil.copy(os.path.join(VAULT_FOLDER, file), dest)
                messagebox.showinfo("Downloaded", f"Saved to: {dest}")

    def view_files():
        search = search_var.get().lower()
        file_table.delete(*file_table.get_children())
        for file in sorted(os.listdir(VAULT_FOLDER)):
            if search in file.lower():
                path = os.path.join(VAULT_FOLDER, file)
                size = humanize.naturalsize(os.path.getsize(path))
                mtime = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%d-%m-%Y %H:%M")
                ext = os.path.splitext(file)[1][1:].lower()
                ftype = ext.upper() + " File"
                icon = get_file_icon(ext)
                file_table.insert("", "end", text=file, values=(ftype, mtime, size), image=icon)

    dark_mode = False
    def toggle_theme():
        nonlocal dark_mode
        dark_mode = not dark_mode
        bg = "#1e1e1e" if dark_mode else "#f4f4f4"
        fg = "white" if dark_mode else "black"

        dashboard.configure(bg=bg)
        top_toolbar.configure(bg=bg)
        bottom_toolbar.configure(bg=bg)
        search_frame.configure(bg=bg)
        for w in search_frame.winfo_children():
            try: w.configure(bg=bg, fg=fg)
            except: pass

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=bg, fieldbackground=bg, foreground=fg, rowheight=25)
        style.configure("Treeview.Heading", background="#333" if dark_mode else "#ccc", foreground=fg)
        view_files()

    def logout():
        try:
            os.remove(".logged_in_user")  # Delete session file
        except: pass
        dashboard.destroy()
        subprocess.Popen(["python", "login_window.py"])  # Relaunch login window

    def sort_files(criteria):
        data = []
        for row in file_table.get_children():
            name = file_table.item(row)["text"]
            values = file_table.item(row)["values"]
            img = file_table.item(row)["image"]
            data.append((name, values, img))

        reverse = False
        key = lambda x: x[0].lower()

        if criteria == "Name (Z-A)": reverse = True
        elif "Date Modified" in criteria:
            key = lambda x: datetime.strptime(x[1][1], "%d-%m-%Y %H:%M")
            reverse = "Newest" in criteria
        elif "Size" in criteria:
            key = lambda x: float(x[1][2].split()[0])
            reverse = "Largest" in criteria
        elif "Type" in criteria:
            key = lambda x: x[1][0].lower()
            reverse = "Z-A" in criteria

        data.sort(key=key, reverse=reverse)
        file_table.delete(*file_table.get_children())
        for name, val, img in data:
            file_table.insert("", "end", text=name, values=val, image=img)

    # ===== Treeview Styling =====
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", rowheight=25)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#cccccc", foreground="black")

    view_files()
    dashboard.mainloop()
