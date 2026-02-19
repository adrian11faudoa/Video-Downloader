# Video Downloader

### Characteristics: <br>
GUI <br>
Video download <br>
Audio (MP3) extraction <br>
YouTube + many other sites <br>
Playlist support <br>

### Features <br>
Playlist checkbox <br>
Subtitle download <br>
Format chooser (MP4, MKV, M4A, WAV) <br>
Queue system (multiple URLs) <br>


### Tech Stack <br>
Python 3.10+ <br>
yt-dlp → download engine (YouTube, Vimeo, Twitter, etc.) <br>
FFmpeg → audio/video conversion <br>
Tkinter → GUI (built into Python) <br>

### Install Requirements <br>
Install yt-dlp <br>
    
    pip install yt-dlp 

### Install FFmpeg (REQUIRED)  <br>
Download from: https://ffmpeg.org/download.html <br>
Add ffmpeg/bin to PATH <br>
Run ffmpeg -version <br>

### Supported Sites (via yt-dlp) <br>
YouTube <br>
Vimeo <br>
Twitter / X <br>
TikTok <br>
Facebook <br>
Instagram <br>
Hundreds more <br>

### Run the App: <br>

    python downloader_app.py 

## Version 1 <br>
### Code Structure:  <br>
🟢Imports : Added <br>
🟢Download Function : Added <br>
🟢Progress Hook : Added <br>
🟢UI Setup : Added <br>



### Upgrade Ideas (V2) <br>
If you want to evolve this into a real product: 

### UI <br>
Progress bar <br>
Dark mode <br>
Video quality selector (720p / 1080p / 4K) <br>
Thumbnail preview <br>


### Packaging <br>
Turn into .exe with PyInstaller <br>
Build modern UI with CustomTkinter or PySide6 <br>
Add auto-update <br>


