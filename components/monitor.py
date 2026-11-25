import time
import psutil

from components.system_info import (
    get_cpu_info,
    get_memory_info,
    get_disk_info,
    get_network_info
)


class SystemMonitor:

    def __init__(self, history_limit=60):

        psutil.cpu_percent(interval=None)

        self.previous_network = get_network_info()

        self.previous_disk_io = psutil.disk_io_counters()

        self.previous_time = time.monotonic()

        self.history_limit = history_limit

        self.history = {
            "cpu": [],
            "memory": [],
            "download": [],
            "upload": [],
            "disk_read": [],
            "disk_write": []
        }

    def update_history(self, key, value):

        self.history[key].append(value)

        if len(self.history[key]) > self.history_limit:
            self.history[key].pop(0)

    def get_metrics(self):

        cpu = get_cpu_info()
        memory = get_memory_info()
        disks = get_disk_info()

        current_network = get_network_info()

        current_disk_io = psutil.disk_io_counters()

        current_time = time.monotonic()
        elapsed = current_time - self.previous_time

        download_speed = 0
        upload_speed = 0
        disk_read_speed = 0
        disk_write_speed = 0

        if elapsed > 0:

            download_speed = max(
                0,
                (
                    current_network["bytes_received"]
                    - self.previous_network["bytes_received"]
                ) / elapsed
            )

            upload_speed = max(
                0,
                (
                    current_network["bytes_sent"]
                    - self.previous_network["bytes_sent"]
                ) / elapsed
            )

            if (
                current_disk_io is not None
                and self.previous_disk_io is not None
            ):

                disk_read_speed = max(
                    0,
                    (
                        current_disk_io.read_bytes
                        - self.previous_disk_io.read_bytes
                    ) / elapsed
                )

                disk_write_speed = max(
                    0,
                    (
                        current_disk_io.write_bytes
                        - self.previous_disk_io.write_bytes
                    ) / elapsed
                )

        self.previous_network = current_network
        self.previous_disk_io = current_disk_io
        self.previous_time = current_time

        self.update_history("cpu", cpu["usage"])
        self.update_history("memory", memory["percent"])
        self.update_history("download", download_speed)
        self.update_history("upload", upload_speed)
        self.update_history("disk_read", disk_read_speed)
        self.update_history("disk_write", disk_write_speed)

        return {
            "cpu": cpu,
            "memory": memory,
            "disks": disks,

            "network": {
                "download_speed": download_speed,
                "upload_speed": upload_speed,
                "bytes_received": current_network["bytes_received"],
                "bytes_sent": current_network["bytes_sent"]
            },

            "disk_io": {
                "read_speed": disk_read_speed,
                "write_speed": disk_write_speed
            },

            "history": self.history
        }
