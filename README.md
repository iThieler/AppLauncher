<h1 align="center" id="heading">AppLauncher</h1>

<p align="center"><sub> Always remember to use due diligence when sourcing scripts and automation tasks from third-party sites. Primarily, I created this script to facilitate downloading files from a URL and monitoring a process after the download. If you want to use the script, do it. </sub></p>

<p align="center">
  <a href="https://github.com/iThieler/AppLauncher/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" ></a>
  <a href="https://github.com/iThieler/iThieler/discussions"><img src="https://img.shields.io/badge/%F0%9F%92%AC-Discussions-orange" /></a>
  <a href="https://github.com/iThieler/AppLauncher/blob/master/CHANGELOG.md"><img src="https://img.shields.io/badge/🔶-Changelog-blue" /></a>
  <a href="https://ko-fi.com/U7U3FUTLF"><img src="https://img.shields.io/badge/%E2%98%95-Buy%20me%20a%20coffee-red" /></a>
</p><br><br>

<p align="center"><img src="https://github.com/home-assistant/brands/blob/master/core_integrations/proxmoxve/icon.png?raw=true" height="100"/></p>

This script performs the following tasks:
- Downloads a file from a specified URL.
- Monitors a process after the file has been downloaded.
- Deletes the downloaded file when the monitored process ends.

## Usage
Run the following in the command line:
```bash
python launcher.py [<URL> <Process Name>]
```
Example:
```bash
python launcher.py https://example.com/my_file.zip my_process
```

## Features
* Download files from a URL.
* Monitor a specific process.
* Delete downloaded files when the monitored process ends.
* Provides a user interface for easy operation.
* System tray integration for process monitoring.

## Installation
1. Clone the repository:
```bash
git clone https://github.com/iThieler/AppLauncher.git
```
2. Navigate to the repository directory:
```bash
cd AppLauncher
```
3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## How It Works
1. The script takes a URL and a process name as inputs.
2. It downloads the file from the provided URL.
3. After the download is complete, it opens the file and starts monitoring the specified process.
4. The script deletes the downloaded file once the monitored process ends.

## License
This project is licensed under the MIT License - see the [LICENSE](https://github.com/iThieler/AppLauncher/blob/master/LICENSE) file for details.

<h1 align="center" id="heading"> Good to know & more </h1>

<details>
<summary markdown="span"> Process Monitoring </summary>

<h1 align="center" id="heading"> Process Monitoring </h1>
The script uses psutil to monitor the specified process. It checks if the process is running and deletes the downloaded file once the process ends.

Example:
```python
def watch_process(process_name, file_path, stop_event):
    logging.info(f'Searching for process: {process_name}')
    process_pid = None

    while not stop_event.is_set() and process_pid is None:
        for process in psutil.process_iter(['pid', 'name']):
            if process_name.lower() in process.name().lower():
                process_pid = process.pid
                process_name_found = process.name()
                break
        time.sleep(1)

    if process_pid is None:
        logging.error(f'Process {process_name} not found.')
        return

    logging.info(f'Process found: {process_name_found} (PID: {process_pid})')

    while not stop_event.is_set():
        if not psutil.pid_exists(process_pid):
            break
        time.sleep(1)

    logging.info(f'{process_name_found} (PID: {process_pid}) has ended.')
    if os.path.exists(file_path):
        os.remove(file_path)
        logging.info(f'File deleted: {file_path}')
    logging.info('Process monitoring ended.')
    os._exit(0)  # Exit the script immediately
```
</details>

<details>
<summary markdown="span"> Download Progress </summary>
<h1 align="center" id="heading"> Download Progress </h1>
The script uses a progress bar to show the download progress. It updates the progress bar as the file is being downloaded.

Example:
```python
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
        logging.info(f'Successfully downloaded: {dest_folder}')
        on_complete()
    except requests.RequestException as e:
        logging.error(f'Error downloading file from {url}: {e}')
        raise ValueError(f'Error downloading file from {url}: {e}')
```
</details>

<details>
<summary markdown="span"> GUI Interface </summary>
<h1 align="center" id="heading"> GUI Interface </h1>
The script includes a graphical user interface (GUI) using Tkinter. The GUI allows users to input the URL and process name, and to start the download and monitoring process.

Example:
```python
def start_download(url, process_name):
    global root
    temp_file = os.path.join(tempfile.gettempdir(), 'downloaded_file.exe')

    root = tk.Tk()
    root.title("der iThieler - Applauncher")
    root.geometry("400x300")
    root.resizable(False, False)
    root.iconbitmap(get_resource_path("logo.ico"))

    progress_var = tk.IntVar()
    progress_queue = Queue()

    ttk.Label(root, text="Download URL:").pack(pady=5)
    url_entry = ttk.Entry(root, width=50)
    url_entry.pack(pady=5)

    url_error_label = ttk.Label(root, text="", foreground="red")
    url_error_label.pack(pady=5)

    ttk.Label(root, text="Process Name:").pack(pady=5)
    process_entry = ttk.Entry(root, width=50)
    process_entry.pack(pady=5)

    process_error_label = ttk.Label(root, text="", foreground="red")
    process_error_label.pack(pady=5)

    ttk.Label(root, text="Download Progress").pack(pady=5)
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

    start_button = ttk.Button(root, text="Start Download", command=start_download_from_gui, state="disabled")
    start_button.pack(pady=5)

    def update_progress_bar():
        try:
            while True:
                progress = progress_queue.get_nowait()
                progress_var.set(progress)
        except Empty:
            pass
        root.after(100, update_progress_bar)

    update_progress_bar()
    root.mainloop()
```
</details>

## Contact
For any questions or suggestions, feel free to open an issue or start a discussion in the [GitHub Discussions](https://github.com/iThieler/iThieler/discussions) section.
