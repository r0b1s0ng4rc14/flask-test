from flask import Flask, render_template
import socket
import psutil
import time
from datetime import datetime

app = Flask(__name__)


def get_ip():
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip
    except Exception:
        return "N/A"


def get_disk():
    partitions = []

    for partition in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(partition.mountpoint)

            partitions.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "total": round(usage.total / (1024 ** 3), 2),
                "used": round(usage.used / (1024 ** 3), 2),
                "free": round(usage.free / (1024 ** 3), 2),
                "percent": usage.percent
            })

        except PermissionError:
            continue

    return partitions


def get_uptime():
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time

    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)

    return f"{days}d {hours}h {minutes}m"


@app.route("/")
def index():

    cpu_percent = psutil.cpu_percent(interval=1)

    memory = psutil.virtual_memory()

    data = {
        "hostname": socket.gethostname(),
        "ip": get_ip(),

        "cpu": {
            "cores": psutil.cpu_count(logical=False),
            "threads": psutil.cpu_count(logical=True),
            "percent": cpu_percent
        },

        "memory": {
            "total": round(memory.total / (1024 ** 3), 2),
            "used": round(memory.used / (1024 ** 3), 2),
            "free": round(memory.available / (1024 ** 3), 2),
            "percent": memory.percent
        },

        "disk": get_disk(),

        "uptime": get_uptime(),

        "last_update": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }

    return render_template("index.html", data=data)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )