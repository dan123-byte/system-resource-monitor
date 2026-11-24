import platform
import psutil

def get_system_info():
    return {
        "system": platform.system(),
        "release": platform.release(),
        "processor": platform.processor(),
        "hostname": platform.node()
    }

def get_cpu_info():
    frequency = psutil.cpu_freq()

    return {
        "usage": psutil.cpu_percent(interval=None),
        "cores": psutil.cpu_count(logical=False),
        "threads": psutil.cpu_count(logical=True),
        "frequency": frequency.current if frequency else 0
    }

def get_memory_info():
    memory = psutil.virtual_memory()

    return {
        "total": memory.total,
        "used": memory.used,
        "available": memory.available,
        "percent": memory.percent
    }

def get_disk_info():
    disks = []

    for partition in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(partition.mountpoint)

            disks.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent
            })

        except (PermissionError, OSError):
            continue

    return disks

def get_network_info():
    network = psutil.net_io_counters()

    return {
        "bytes_sent": network.bytes_sent,
        "bytes_received": network.bytes_recv
    }

def format_bytes(size):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f} PB"
