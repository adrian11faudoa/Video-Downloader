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
current_tasks = {}

# =========================
# Functions
# =========================

def check_ffmpeg():
    try:
        import subprocess
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

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

    # Check FFmpeg if needed
    if format_var.get() in ["mp3", "wav"] and not check_ffmpeg():
        messagebox.showerror("FFmpeg Missing", "FFmpeg is required for audio conversion (MP3/WAV). Please install it and add it to PATH.")
        return
    global is_downloading, paused

    if is_downloading:
        paused = False
        return

    if download_queue.empty():
        messagebox.showerror("Error", "Queue is empty")
        return

    if not download_path.get():
        messagebox.showerror("Error", "Select folder")
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
            root.after(0, lambda: messagebox.showerror("Error", str(e)))

    is_downloading = False


def move_to_processing(url):
    if queue_list.exists(url):
        queue_list.delete(url)
    processing_list.insert("", "end", iid=url, values=(url, "Processing", "0%"))


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
        percent = d.get("_percent_str", "0%").strip()
        root.after(0, lambda: update_progress(url, percent))

# =========================
# UI
# =========================

root = tk.Tk()
root.title("Downloader Pro")

# Make window auto-fit screen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set to ~80% of screen size
window_width = int(screen_width * 0.8)
window_height = int(screen_height * 0.8)

root.geometry(f"{window_width}x{window_height}")
root.minsize(800, 500)

# Allow resizing
root.rowconfigure(2, weight=1)
root.columnconfigure(0, weight=1)

# Input
input_box = tk.Text(root, height=4)
input_box.pack(fill="x", padx=10, pady=5)

tk.Button(root, text="Add Links", command=add_links).pack()

# Tables
frame = tk.Frame(root)
frame.pack(fill="both", expand=True)

columns = ("URL", "Status", "Progress")

queue_list = ttk.Treeview(frame, columns=columns, show="headings")
processing_list = ttk.Treeview(frame, columns=columns, show="headings")
done_list = ttk.Treeview(frame, columns=columns, show="headings")

for tree, title in [(queue_list, "Queue"), (processing_list, "Processing"), (done_list, "Done")]:
    tree.heading("URL", text=title)
    tree.heading("Status", text="Status")
    tree.heading("Progress", text="Progress")
    tree.pack(side="left", fill="both", expand=True)

# Format selector
format_var = tk.StringVar(value="mp4")
format_frame = tk.Frame(root)
format_frame.pack()

for fmt in ["mp4", "mkv", "mp3", "wav"]:
    tk.Radiobutton(format_frame, text=fmt.upper(), variable=format_var, value=fmt).pack(side="left")

# Folder
path_frame = tk.Frame(root)
path_frame.pack(fill="x", padx=10)

download_path = tk.StringVar()

tk.Entry(path_frame, textvariable=download_path).pack(side="left", fill="x", expand=True)
tk.Button(path_frame, text="Browse", command=browse_folder).pack(side="left", padx=5)

# Controls
control_frame = tk.Frame(root)
control_frame.pack(pady=10)

tk.Button(control_frame, text="Start / Resume", command=start_download, bg="green", fg="white").pack(side="left", padx=5)
tk.Button(control_frame, text="Pause", command=pause_download, bg="orange").pack(side="left", padx=5)

root.mainloop()
