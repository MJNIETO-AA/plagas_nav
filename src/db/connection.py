import json
import mysql.connector
from mysql.connector import Error
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
    return os.path.dirname(os.path.abspath(__file__))

def load_config(path=None):
    if path is None:
        path = os.path.join(app_base_path(), "config.json")

    with open(path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config

def get_connection():
    cfg = load_config() ['db']
    try:
        conn = mysql.connector.connect(
            host=cfg['host'],
            port=cfg['port'],
            user=cfg['user'],
            password=cfg['password'],
            database=cfg['database']
        )
        return conn
    except Error as e:
        raise RuntimeError(f"Error conectando a MySQL: {e}")