import os
import subprocess
from datetime import datetime
import json
import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def app_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(".")


def load_config():
    config_path = os.path.join(app_base_path(), "config.json")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    return config


def create_backup():
    config = load_config()
    db = config["db"]

    host = db["host"]
    user = db["user"]
    password = db["password"]
    database = db["database"]

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


    base_dir = app_base_path()
    backup_folder = os.path.join(base_dir, "backup")
    os.makedirs(backup_folder, exist_ok=True)

    filename = os.path.join(backup_folder, f"backup_{database}_{timestamp}.sql")

    command = f"mysqldump -h {host} -u {user} -p{password} {database} > {filename}"

    subprocess.call(command, shell=True)

    return filename