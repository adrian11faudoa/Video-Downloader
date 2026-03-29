import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import threading
import os
from queue import Queue
import time

# =========================
# Globals
# =========================
download_queue = Queue()
is_downloading = False
paused = False

# =========================
# Functions
# =========================

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        download_path.set(folder)


def add_links():
    text = input_box.get("1.0", tk.END).strip()
    if not text:
        return

    links = [line.strip() for line in text.split("\n") if line.strip()]

    for link in links:
        queue_list.insert("", "end", iid=link, values=(link, "Queued", "0%"))
        download_queue.put(link)

    input_box.delete("1.0", tk.END)


def start_download():
    global is_downloading, paused

    if is_downloading:
        paused = False
        return

    if download_queue.empty():
        messagebox.showerror("Error", "Queue is empty")
        return

    if not download_path.get():
        messagebox.showerror("Error", "Select a download folder first")
        return

    is_downloading = True
    paused = False
    threading.Thread(target=process_queue, daemon=True).start()


def pause_download():
    global paused
    paused = True


def process_queue():
    global is_downloading

    while not download_queue.empty():
        while paused:
            time.sleep(0.5)

        url = download_queue.get()
        root.after(0, lambda u=url: move_to_processing(u))

        try:
            download_single(url)
            root.after(0, lambda u=url: move_to_done(u))
        except Exception as e:
            root.after(0, lambda err=e: messagebox.showerror("Error", str(err)))

    is_downloading = False


def move_to_processing(url):
    if queue_list.exists(url):
        queue_list.delete(url)
    processing_list.insert("", "end", iid=url, values=(url, "Processing", "0%"))
    notebook.select(1)  # Switch to Processing tab


def move_to_done(url):
    if processing_list.exists(url):
        processing_list.delete(url)
    done_list.insert("", "end", iid=url, values=(url, "Done", "100%"))


def update_progress(url, percent):
    if processing_list.exists(url):
        processing_list.item(url, values=(url, "Processing", percent))


def download_single(url):
    folder = download_path.get()
    fmt = format_var.get()

    ydl_opts = {
        "outtmpl": os.path.join(folder, "%(title)s_%(id)s.%(ext)s"),
        "progress_hooks": [lambda d: progress_hook(d, url)],
        "concurrent_fragment_downloads": 3,
    }

    if fmt == "mp3":
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
    elif fmt == "wav":
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }],
        })
    else:
        ydl_opts["format"] = f"bestvideo+bestaudio/{fmt}"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def progress_hook(d, url):
    if d["status"] == "downloading":
        # Use _percent_str or calculate from downloaded/total bytes
        percent_str = d.get("_percent_str", "")
        
        # Strip ANSI escape codes and extract just the number+%
        import re
        clean = re.sub(r'\x1b\[[0-9;]*m', '', percent_str).strip()
        
        # Fallback: calculate manually from bytes
        if not clean or "%" not in clean:
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            if total:
                clean = f"{downloaded / total * 100:.1f}%"
            else:
                clean = "..."
        
        root.after(0, lambda p=clean: update_progress(url, p))


# =========================
# UI
# =========================

root = tk.Tk()
root.title("Downloader Pro")
root.geometry("900x650")
root.minsize(700, 550)

# --- Top: URL Input ---
input_frame = tk.LabelFrame(root, text="Add URLs (one per line)", padx=5, pady=5)
input_frame.pack(fill="x", padx=10, pady=(10, 0))

input_box = tk.Text(input_frame, height=4)
input_box.pack(fill="x", side="left", expand=True)

tk.Button(input_frame, text="Add Links", command=add_links, width=12).pack(side="left", padx=(8, 0))

# --- Middle: Tabbed Tables ---
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=10, pady=8)

columns = ("URL", "Status", "Progress")

def make_tree(parent):
    frame = tk.Frame(parent)
    tree = ttk.Treeview(frame, columns=columns, show="headings")
    tree.heading("URL", text="URL")
    tree.heading("Status", text="Status")
    tree.heading("Progress", text="Progress")
    tree.column("URL", width=580, stretch=True)
    tree.column("Status", width=120, anchor="center")
    tree.column("Progress", width=100, anchor="center")
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    return frame, tree

queue_frame, queue_list = make_tree(notebook)
processing_frame, processing_list = make_tree(notebook)
done_frame, done_list = make_tree(notebook)

notebook.add(queue_frame, text="  Queue  ")
notebook.add(processing_frame, text="  Processing  ")
notebook.add(done_frame, text="  Done  ")

# --- Bottom bar ---
bottom = tk.Frame(root)
bottom.pack(fill="x", padx=10, pady=(0, 10))

# Format selector
format_var = tk.StringVar(value="mp4")
fmt_frame = tk.LabelFrame(bottom, text="Format", padx=6, pady=4)
fmt_frame.pack(side="left")

for fmt in ["mp4", "mkv", "mp3", "wav"]:
    tk.Radiobutton(fmt_frame, text=fmt.upper(), variable=format_var, value=fmt).pack(side="left", padx=4)

# Folder picker
folder_frame = tk.LabelFrame(bottom, text="Save to", padx=6, pady=4)
folder_frame.pack(side="left", fill="x", expand=True, padx=10)

download_path = tk.StringVar()
tk.Entry(folder_frame, textvariable=download_path).pack(side="left", fill="x", expand=True)
tk.Button(folder_frame, text="Browse", command=browse_folder).pack(side="left", padx=(6, 0))

# Control buttons
ctrl_frame = tk.Frame(bottom)
ctrl_frame.pack(side="right")

tk.Button(ctrl_frame, text="▶  Start / Resume", command=start_download,
          bg="#27ae60", fg="white", font=("", 10, "bold"), padx=10, pady=6).pack(side="left", padx=4)
tk.Button(ctrl_frame, text="⏸  Pause", command=pause_download,
          bg="#e67e22", fg="white", font=("", 10, "bold"), padx=10, pady=6).pack(side="left", padx=4)

root.mainloop()
