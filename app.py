from flask import Flask, render_template_string, redirect, url_for
import os
import shutil

app = Flask(__name__)

DOWNLOADS_PATH = os.path.expanduser("~/Downloads")

FILE_TYPES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv"],
    "Audio": [".mp3", ".wav", ".aac"],
    "Archives": [".zip", ".rar", ".tar", ".gz"],
    "Installers": [".exe", ".msi", ".dmg"],
    "Scripts": [".py", ".js", ".html", ".css"],
}

def organize_downloads():
    log = []
    summary = {category: 0 for category in FILE_TYPES.keys()}
    summary["Others"] = 0

    files = [f for f in os.listdir(DOWNLOADS_PATH) if os.path.isfile(os.path.join(DOWNLOADS_PATH, f))]
    total_files = len(files)

    for filename in files:
        file_path = os.path.join(DOWNLOADS_PATH, filename)
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        moved = False
        for folder, extensions in FILE_TYPES.items():
            if ext in extensions:
                dest_folder = os.path.join(DOWNLOADS_PATH, folder)
                os.makedirs(dest_folder, exist_ok=True)
                shutil.move(file_path, os.path.join(dest_folder, filename))
                log.append(f"Moved: {filename} → {folder}")
                summary[folder] += 1
                moved = True
                break

        if not moved:
            dest_folder = os.path.join(DOWNLOADS_PATH, "Others")
            os.makedirs(dest_folder, exist_ok=True)
            shutil.move(file_path, os.path.join(dest_folder, filename))
            log.append(f"Moved: {filename} → Others")
            summary["Others"] += 1

    return log, summary, total_files

TEMPLATE = """
<!doctype html>
<html>
<head>
    <title>Downloads Organizer Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
        .btn { display: inline-block; padding: 10px 20px; background: #0078D7; 
               color: white; text-decoration: none; border-radius: 5px; }
        .btn:hover { background: #005a9e; }
        .log { background: #f4f4f4; padding: 15px; border-radius: 5px; margin-top: 20px; }
        .summary { margin-top: 20px; }
        .bar { height: 20px; background: #0078D7; }
        .bar-container { width: 100%; background: #ddd; border-radius: 5px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <h1>Downloads Organizer Dashboard</h1>
    <a href="{{ url_for('clean') }}" class="btn">Organize Downloads</a>

    {% if summary %}
    <div class="summary">
        <h2>Summary:</h2>
        {% for category, count in summary.items() %}
            <p>{{ category }}: {{ count }} files</p>
            <div class="bar-container">
                <div class="bar" style="width: {{ (count/total_files)*100 if total_files > 0 else 0 }}%"></div>
            </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if log %}
    <h2>Cleanup Log:</h2>
    <div class="log">
        {% for entry in log %}
            <p>{{ entry }}</p>
        {% endfor %}
    </div>
    {% endif %}
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(TEMPLATE, log=None, summary=None, total_files=0)

@app.route("/clean")
def clean():
    log, summary, total_files = organize_downloads()
    return render_template_string(TEMPLATE, log=log, summary=summary, total_files=total_files)

if __name__ == "__main__":
    app.run(debug=True)