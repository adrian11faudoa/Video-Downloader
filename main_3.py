# Advanced Downloader with Queue, Progress Bar, Multi-threading

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import threading
import queue
import os

# =========================
# Globals
# =========================
download_queue = queue.Queue()
is_paused = False
is_downloading = False

# =========================
# UI Functions
# =========================

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        download_path.set(folder)


def browse_file():
    file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file:
        file_path_var.set(file)


def add_to_queue():
    urls = []

    if url_entry.get().strip():
        urls.append(url_entry.get().strip())

    if file_path_var.get():
        with open(file_path_var.get(), "r", encoding="utf-8") as f:
            urls.extend([line.strip() for line in f if line.strip()])

    for url in urls:
        download_queue.put({
            "url": url,
            "format": format_var.get(),
            "type": type_var.get()
        })
        queue_list.insert(tk.END, url)


def start_download():
    global is_downloading
    if is_downloading:
        return

    is_downloading = True
    threading.Thread(target=process_queue, daemon=True).start()


def pause_download():
    global is_paused
    is_paused = True


def resume_download():
    global is_paused
    is_paused = False


# =========================
# Download Logic
# =========================

def process_queue():
    global is_downloading

    while not download_queue.empty():
        while is_paused:
            continue

        item = download_queue.get()
        url = item["url"]
        fmt = item["format"]
        typ = item["type"]

        status_label.config(text=f"Downloading: {url}")

        try:
            ydl_opts = {
                "outtmpl": os.path.join(download_path.get(), "%(title)s_%(id)s.%(ext)s"),
                "progress_hooks": [progress_hook],
                "concurrent_fragment_downloads": 5,
            }

            if typ == "audio":
                ydl_opts.update({
                    "format": "bestaudio/best",
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": fmt,
                    }],
                })
            else:
                ydl_opts["format"] = fmt

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        except Exception as e:
            print("Error:", e)

        download_queue.task_done()
        queue_list.delete(0)

    is_downloading = False
    status_label.config(text="All downloads completed")


# =========================
# Progress Hook
# =========================

def progress_hook(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded = d.get('downloaded_bytes', 0)

        if total:
            percent = int(downloaded / total * 100)
            progress_bar['value'] = percent
            root.update_idletasks()

    elif d['status'] == 'finished':
        progress_bar['value'] = 100


# =========================
# UI
# =========================

root = tk.Tk()
root.title("Advanced Downloader")
root.geometry("600x500")

# URL
url_entry = tk.Entry(root, width=70)
url_entry.pack(pady=5)

# File loader
file_path_var = tk.StringVar()
file_frame = tk.Frame(root)
file_frame.pack()

tk.Entry(file_frame, textvariable=file_path_var, width=50).pack(side="left")
tk.Button(file_frame, text="Load .txt", command=browse_file).pack(side="left")

# Folder

download_path = tk.StringVar()
path_frame = tk.Frame(root)
path_frame.pack(pady=5)

tk.Entry(path_frame, textvariable=download_path, width=50).pack(side="left")
tk.Button(path_frame, text="Folder", command=browse_folder).pack(side="left")

# Type (video/audio)
type_var = tk.StringVar(value="video")

tk.Radiobutton(root, text="Video", variable=type_var, value="video").pack()
tk.Radiobutton(root, text="Audio", variable=type_var, value="audio").pack()

# Format selection
format_var = tk.StringVar(value="best")

tk.Label(root, text="Format (video: best/mp4, audio: mp3/wav)").pack()
tk.Entry(root, textvariable=format_var).pack()

# Queue list
queue_list = tk.Listbox(root, width=80, height=10)
queue_list.pack(pady=10)

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack()

tk.Button(btn_frame, text="Add to Queue", command=add_to_queue).pack(side="left")
tk.Button(btn_frame, text="Start", command=start_download).pack(side="left")
tk.Button(btn_frame, text="Pause", command=pause_download).pack(side="left")
tk.Button(btn_frame, text="Resume", command=resume_download).pack(side="left")

# Progress bar
progress_bar = ttk.Progressbar(root, length=400, mode='determinate')
progress_bar.pack(pady=10)

# Status
status_label = tk.Label(root, text="Idle")
status_label.pack()

root.mainloop()

