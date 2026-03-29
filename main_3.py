import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import threading
import os
from queue import Queue

# =========================
# Globals
# =========================
download_queue = Queue()
is_downloading = False

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
        queue_listbox.insert(tk.END, link)
        download_queue.put(link)

    input_box.delete("1.0", tk.END)


def start_download():
    global is_downloading

    if is_downloading:
        return

    if download_queue.empty():
        messagebox.showerror("Error", "No links in queue")
        return

    folder = download_path.get()
    if not folder:
        messagebox.showerror("Error", "Select a download folder")
        return

    is_downloading = True
    threading.Thread(target=process_queue, daemon=True).start()


def process_queue():
    global is_downloading

    while not download_queue.empty():
        url = download_queue.get()

        # Move from queue → processing
        root.after(0, move_to_processing, url)

        try:
            download_single(url)
            root.after(0, move_to_done, url)
        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Error", str(e)))

    is_downloading = False
    root.after(0, lambda: status_label.config(text="All downloads completed!"))


def move_to_processing(url):
    remove_from_list(queue_listbox, url)
    processing_listbox.insert(tk.END, url)
    status_label.config(text=f"Processing: {url}")


def move_to_done(url):
    remove_from_list(processing_listbox, url)
    done_listbox.insert(tk.END, url)
    status_label.config(text=f"Finished: {url}")


def remove_from_list(listbox, value):
    items = listbox.get(0, tk.END)
    for i, item in enumerate(items):
        if item == value:
            listbox.delete(i)
            break


def download_single(url):
    folder = download_path.get()
    mode = download_type.get()

    ydl_opts = {
        "outtmpl": os.path.join(folder, "%(title)s_%(id)s.%(ext)s"),
        "progress_hooks": [progress_hook],
        "concurrent_fragment_downloads": 5,
    }

    if mode == "audio":
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
    else:
        ydl_opts["format"] = "bestvideo+bestaudio/best"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def progress_hook(d):
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "0%").strip()
        root.after(0, lambda: status_label.config(text=f"Downloading: {percent}"))
    elif d["status"] == "finished":
        root.after(0, lambda: status_label.config(text="Processing file..."))


# =========================
# UI Setup
# =========================

root = tk.Tk()
root.title("Advanced Downloader")
root.geometry("750x500")

# Input box (multi-links)
tk.Label(root, text="Paste Links (one per line)").pack()
input_box = tk.Text(root, height=5)
input_box.pack(fill="x", padx=10, pady=5)

tk.Button(root, text="Add to Queue", command=add_links).pack(pady=5)

# Frames for lists
lists_frame = tk.Frame(root)
lists_frame.pack(fill="both", expand=True)

# Queue list
queue_frame = tk.Frame(lists_frame)
queue_frame.pack(side="left", fill="both", expand=True)

tk.Label(queue_frame, text="Queued").pack()
queue_listbox = tk.Listbox(queue_frame)
queue_listbox.pack(fill="both", expand=True, padx=5, pady=5)

# Processing list
processing_frame = tk.Frame(lists_frame)
processing_frame.pack(side="left", fill="both", expand=True)

tk.Label(processing_frame, text="Processing").pack()
processing_listbox = tk.Listbox(processing_frame)
processing_listbox.pack(fill="both", expand=True, padx=5, pady=5)

# Done list
done_frame = tk.Frame(lists_frame)
done_frame.pack(side="left", fill="both", expand=True)

tk.Label(done_frame, text="Done").pack()
done_listbox = tk.Listbox(done_frame)
done_listbox.pack(fill="both", expand=True, padx=5, pady=5)

# Download type
download_type = tk.StringVar(value="video")

type_frame = tk.Frame(root)
type_frame.pack(pady=5)

tk.Radiobutton(type_frame, text="Video", variable=download_type, value="video").pack(side="left", padx=10)
tk.Radiobutton(type_frame, text="Audio (MP3)", variable=download_type, value="audio").pack(side="left", padx=10)

# Folder selection
download_path = tk.StringVar()

path_frame = tk.Frame(root)
path_frame.pack(pady=5)

tk.Entry(path_frame, textvariable=download_path, width=50).pack(side="left")
tk.Button(path_frame, text="Browse", command=browse_folder).pack(side="left", padx=5)

# Start button
tk.Button(root, text="Start Download", command=start_download, bg="#4CAF50", fg="white").pack(pady=10)

# Status
status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()
