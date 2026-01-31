# Imports
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import threading
import os


def download():
    url = url_entry.get().strip()
    mode = download_type.get()
    folder = download_path.get()

    if not url:
        messagebox.showerror("Error", "Please enter a URL")
        return

    if not folder:
        messagebox.showerror("Error", "Please select a download folder")
        return

    def run():
        try:
            ydl_opts = {
                "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
                "noplaylist": False,
                "progress_hooks": [progress_hook],
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

            messagebox.showinfo("Success", "Download completed!")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    threading.Thread(target=run).start()



def progress_hook(d):
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "0%").strip()
        status_label.config(text=f"Downloading: {percent}")
    elif d["status"] == "finished":
        status_label.config(text="Processing file...")



def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        download_path.set(folder)


# UI 
root = tk.Tk()
root.title("Video / Audio Downloader")
root.geometry("500x300")
root.resizable(False, False)

tk.Label(root, text="Video URL").pack(pady=5)
url_entry = tk.Entry(root, width=60)
url_entry.pack()

download_type = tk.StringVar(value="video")

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Radiobutton(frame, text="Video", variable=download_type, value="video").pack(side="left", padx=10)
tk.Radiobutton(frame, text="Audio (MP3)", variable=download_type, value="audio").pack(side="left", padx=10)

download_path = tk.StringVar()

path_frame = tk.Frame(root)
path_frame.pack(pady=10)

tk.Entry(path_frame, textvariable=download_path, width=40).pack(side="left")
tk.Button(path_frame, text="Browse", command=browse_folder).pack(side="left", padx=5)

tk.Button(root, text="Download", command=download, bg="#4CAF50", fg="white").pack(pady=15)

status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()
