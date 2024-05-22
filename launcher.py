"""
Der iThieler - AppLauncher

A script for downloading files from a URL and monitoring a process after the download.

SYNOPSIS:
    python script.py [<URL> <Process Name>]

DESCRIPTION:
    This script allows downloading files from a specified URL and monitoring a process
    after the file has been downloaded. It also provides a user interface for easy operation.

    Options:
        <URL>           The URL of the file to be downloaded.
        <Process Name>  The name or part of the name of the process to be monitored.

EXAMPLES:
    python script.py https://example.com/my_file.zip my_process
    python script.py

LICENSE:
    MIT License

AUTHOR:
    Michael Thiel (der iThieler)

HOMEPAGES:
    Homepage: https://der-ithieler.de
    GitHub: https://github.com/iThieler/AppLauncher

VERSION:
    1.0

COPYRIGHT:
    Copyright © 2024 Michael Thiel (der iThieler)

LAST MODIFIED:
    Last modified: May 20, 2024
"""

import os
import sys
import requests
import threading
import logging
import time
import psutil
import re
import pystray
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox
from queue import Queue, Empty
from PIL import Image
import tempfile

# Set Logging-Configuration
log_file_path = os.path.join(tempfile.gettempdir(), 'der-iThieler_AppLauncher.log')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_file_path, filemode='w')

# Function for downloading a file from a URL
def download_file(url, dest_folder, progress_queue, on_complete):
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_length = int(r.headers.get('content-length', 0))
            progress = 0
            with open(dest_folder, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        progress += len(chunk)
                        progress_queue.put(progress * 100 // total_length)
        logging.info(f'Download erfolgreich: {dest_folder}')
        on_complete()
    except requests.RequestException as e:
        logging.error(f'Fehler beim Herunterladen der Datei von {url}: {e}')
        raise ValueError(f'Fehler beim Herunterladen der Datei von {url}: {e}')

# Function for monitoring a process and deleting the downloaded file upon process termination
def watch_process(process_name, file_path, stop_event):
    logging.info(f'Suche den zu überwachenden Prozess mit dem Schlagwort: {process_name}')
    process_pid = None

    while not stop_event.is_set() and process_pid is None:
        for process in psutil.process_iter(['pid', 'name']):
            if process_name.lower() in process.name().lower():
                process_pid = process.pid
                process_name_found = process.name()
                break
        time.sleep(1)

    if process_pid is None:
        logging.error(f'Prozess {process_name} wurde nicht gefunden.')
        return

    logging.info(f'Prozess gefunden: {process_name_found} (PID: {process_pid})')
    
    # Minimize the GUI window and display the icon in the system tray
    root.withdraw()
    threading.Thread(target=show_systray_icon).start()

    while not stop_event.is_set():
        if not psutil.pid_exists(process_pid):
            break
        time.sleep(1)

    logging.info(f'{process_name_found} (PID: {process_pid}) wurde beendet.')
    if os.path.exists(file_path):
        os.remove(file_path)
        logging.info(f'Datei gelöscht: {file_path}')
    logging.info('Überwachung des Prozesses beendet.')
    os._exit(0)  # Beendet das Skript sofort

# Function for validating a URL
def validate_url(url):
    if not url.startswith("http://") and not url.startswith("https://"):
        return "Bitte geben Sie eine gültige URL ein (beginnend mit 'http://' oder 'https://')."
    if not re.match(r'^[a-zA-Z0-9\-._~:/?#\[\]@!$&\'()*+,;=%]+$', url) or url.count('.') < 2:
        return "Die eingegebene URL ist ungültig."
    return ""

# Function for validating the process name
def validate_process_name(process_name):
    if ' ' in process_name:
        return "Der Prozessname darf kein Leerzeichen enthalten."
    if not re.match(r'^[a-zA-Z0-9äöüÄÖÜß\-_]+$', process_name):
        return "Erlaubte Zeichen: a-z, A-Z, 0-9, äöü, AÖÜ, ß, Bindestriche und Unterstriche"
    return ""

# Function to determine the path to a resource
def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # Pfad für PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Function for opening the downloaded file and starting the monitored process
def open_file_and_watch(url, process_name, temp_file, progress_queue, stop_event):
    def on_download_complete():
        try:
            os.startfile(temp_file)
            threading.Thread(target=watch_process, args=(process_name, temp_file, stop_event)).start()
        except Exception as e:
            logging.error(f'Fehler beim Öffnen der Datei oder Starten des Prozesses: {e}')

    download_file(url, temp_file, progress_queue, on_download_complete)

# Function for opening the homepage
def open_homepage():
    webbrowser.open("https://der-ithieler.de")

# Function for opening the GitHub page for the repository
def open_Github():
    webbrowser.open("https://github.com/iThieler/AppLauncher")

# Function for displaying the system tray icon
def show_systray_icon():
    icon_path = get_resource_path("logo.ico")
    icon = Image.open(icon_path)
    menu = pystray.Menu(
        pystray.MenuItem("der iThieler - Homepage", open_homepage),  # Menüpunkt für die Webseite
        pystray.MenuItem("der iThieler - Github", open_Github),  # Menüpunkt für die Webseite
        #pystray.MenuItem("Beenden", exit_program)
        )
    systray = pystray.Icon("der iThieler - AppLauncher", icon, "der iThieler - AppLauncher", menu)
    systray.run()

# Main function for starting the download and the GUI
def start_download(url, process_name):
    global root  # Machen Sie die root-Variable global, damit sie in watch_process zugänglich ist
    temp_file = os.path.join(tempfile.gettempdir(), 'downloaded_file.exe')

    root = tk.Tk()
    root.title("der iThieler - AppLauncher")
    root.geometry("400x300")
    root.resizable(False, False)
    root.iconbitmap(get_resource_path("logo.ico"))  # Verwende die get_resource_path Funktion

    progress_var = tk.IntVar()
    progress_queue = Queue()

    ttk.Label(root, text="Download von URL:").pack(pady=5)
    url_entry = ttk.Entry(root, width=50)
    url_entry.pack(pady=5)

    url_error_label = ttk.Label(root, text="", foreground="red")
    url_error_label.pack(pady=5)

    ttk.Label(root, text="Der Prozessname lautet oder beinhaltet:").pack(pady=5)
    process_entry = ttk.Entry(root, width=50)
    process_entry.pack(pady=5)

    process_error_label = ttk.Label(root, text="", foreground="red")
    process_error_label.pack(pady=5)

    ttk.Label(root, text="Download Fortschritt").pack(pady=5)
    progress_bar = ttk.Progressbar(root, orient="horizontal", length=350, mode="determinate", variable=progress_var)
    progress_bar.pack(pady=5)

    def validate_entries(event=None):
        url = url_entry.get()
        process_name = process_entry.get()
        url_error_message = validate_url(url)
        process_error_message = validate_process_name(process_name)
        url_error_label.config(text=url_error_message)
        process_error_label.config(text=process_error_message)
        start_button.config(state="normal" if not url_error_message and not process_error_message else "disabled")


    url_entry.bind("<KeyRelease>", validate_entries)
    process_entry.bind("<KeyRelease>", validate_entries)

    def start_download_from_gui():
        url = url_entry.get()
        process_name = process_entry.get()
        error_message = validate_url(url)
        if error_message:
            url_error_label.config(text=error_message)
        else:
            stop_event = threading.Event()
            threading.Thread(target=open_file_and_watch, args=(url, process_name, temp_file, progress_queue, stop_event)).start()
            start_button.config(state="disabled")
            update_progress_bar()

    start_button = ttk.Button(root, text="Download starten", command=start_download_from_gui, state="disabled")
    start_button.pack(pady=5)

    def update_progress_bar():
        try:
            while True:
                progress = progress_queue.get_nowait()
                progress_var.set(progress)
        except Empty:
            pass
        root.after(100, update_progress_bar)

    if url:
        url_entry.insert(0, url)
        validate_entries()
    if process_name:
        process_entry.insert(0, process_name)
        validate_entries()

    update_progress_bar()
    root.mainloop()

# Main program
if __name__ == '__main__':
    url = ""
    process_name = ""

    if len(sys.argv) == 3:
        url = sys.argv[1]
        process_name = sys.argv[2]

    start_download(url, process_name)
