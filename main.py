import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import threading
import os

# =========================
# Functions
# =========================

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        download_path.set(folder)


def browse_file():
    file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file:
        file_path_var.set(file)


def download():
    urls = []

    # Get single URL
    single_url = url_entry.get().strip()
    if single_url:
        urls.append(single_url)

    # Get URLs from file
    file_path = file_path_var.get()
    if file_path:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                file_urls = [line.strip() for line in f if line.strip()]
                urls.extend(file_urls)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file:\n{e}")
            return

    folder = download_path.get()

    if not urls:
        messagebox.showerror("Error", "Please enter a URL or select a file")
        return

    if not folder:
        messagebox.showerror("Error", "Please select a download folder")
        return

    mode = download_type.get()

    def run():
        try:
            for url in urls:
                status_label.config(text=f"Starting: {url}")

                ydl_opts = {
                    "outtmpl": os.path.join(folder, "%(title)s_%(id)s.%(ext)s"),
                    "noplaylist": False,
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

            status_label.config(text="All downloads completed!")
            messagebox.showinfo("Success", "All downloads completed!")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    threading.Thread(target=run, daemon=True).start()


def progress_hook(d):
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "0%").strip()
        status_label.config(text=f"Downloading: {percent}")
    elif d["status"] == "finished":
        status_label.config(text="Processing file...")


# =========================
# UI Setup
# =========================

root = tk.Tk()
root.title("Video / Audio Downloader")
root.geometry("520x350")
root.resizable(False, False)

# URL input
tk.Label(root, text="Video URL").pack(pady=5)
url_entry = tk.Entry(root, width=65)
url_entry.pack()

# Download type
download_type = tk.StringVar(value="video")

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Radiobutton(frame, text="Video", variable=download_type, value="video").pack(side="left", padx=10)
tk.Radiobutton(frame, text="Audio (MP3)", variable=download_type, value="audio").pack(side="left", padx=10)

# File input (.txt)
file_path_var = tk.StringVar()

file_frame = tk.Frame(root)
file_frame.pack(pady=5)

tk.Entry(file_frame, textvariable=file_path_var, width=45).pack(side="left")
tk.Button(file_frame, text="Load .txt", command=browse_file).pack(side="left", padx=5)

# Folder selection
download_path = tk.StringVar()

path_frame = tk.Frame(root)
path_frame.pack(pady=10)

tk.Entry(path_frame, textvariable=download_path, width=45).pack(side="left")
tk.Button(path_frame, text="Browse Folder", command=browse_folder).pack(side="left", padx=5)

# Download button
tk.Button(root, text="Download", command=download, bg="#4CAF50", fg="white", width=20).pack(pady=15)

# Status label
status_label = tk.Label(root, text="")
status_label.pack()

# Run app
root.mainloop()
