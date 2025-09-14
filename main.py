import os
import threading
import tkinter as tk
from tkinter import messagebox, font
import yt_dlp

# --------------------------
# Constants
# --------------------------
DOWNLOAD_DIR = "downloads"
VIDEO_FORMAT = "18"  # 360p MP4

# Ensure downloads folder exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# --------------------------
# Functions
# --------------------------
def search_videos():
    """Search YouTube and display results in the listbox."""
    query = search_entry.get().strip()
    results_listbox.delete(0, tk.END)

    if not query:
        return

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch100:{query}", download=False)
            for video in search_results.get('entries', []):
                title = video.get('title', 'No title')
                url = video.get('url')
                results_listbox.insert(tk.END, f"{title:<60} | {url}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while searching: {e}")

def download_worker(urls):
    """Worker thread to download videos."""
    ydl_opts = {
        'format': VIDEO_FORMAT,
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'quiet': True,
    }
    ydl = yt_dlp.YoutubeDL(ydl_opts)
    for url in urls:
        try:
            ydl.download([url])
        except Exception as e:
            # Show error in main thread
            root.after(0, lambda e=e: messagebox.showerror("Error", f"Error downloading {url}: {e}"))
    # When finished, show success message
    root.after(0, lambda: messagebox.showinfo("Success", "All downloads completed!"))

def download_selected():
    """Start download in a background thread with simple notifications."""
    selected_indices = results_listbox.curselection()
    if not selected_indices:
        messagebox.showinfo("Info", "Please select at least one video to download!")
        return

    # Collect URLs
    urls = [results_listbox.get(i).split("|")[-1].strip() for i in selected_indices]

    # Show "download started" message
    messagebox.showinfo("Download Started", "Download started... please wait a few moments.")

    # Start download in a separate thread
    threading.Thread(target=download_worker, args=(urls,), daemon=True).start()

# --------------------------
# GUI Setup
# --------------------------
root = tk.Tk()
root.title("YouTube Video Downloader")
root.geometry("800x500")

app_font = font.Font(family="Helvetica", size=10)

# Search input
search_entry = tk.Entry(root, width=50, font=app_font)
search_entry.pack(padx=10, pady=10)

search_button = tk.Button(root, text="Search", command=search_videos, font=app_font)
search_button.pack(pady=5)

# Frame for listbox + scrollbar
frame = tk.Frame(root)
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

results_listbox = tk.Listbox(frame, width=100, height=15, selectmode=tk.MULTIPLE, font=app_font)
results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

results_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=results_listbox.yview)

# Download button
download_button = tk.Button(root, text="Download Selected", command=download_selected, font=app_font)
download_button.pack(pady=10)

root.mainloop()
