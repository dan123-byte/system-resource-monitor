from matplotlib.figure import Figure


class PerformanceCharts:

    def __init__(self, parent):

        self.sample_interval = 2
        self.history_limit = 60

        self.figure = Figure(
            figsize=(10, 8),
            dpi=100,
            facecolor="#0f172a"
        )

        self.cpu_ax = self.figure.add_subplot(321)
        self.memory_ax = self.figure.add_subplot(322)
        self.download_ax = self.figure.add_subplot(323)
        self.upload_ax = self.figure.add_subplot(324)
        self.disk_read_ax = self.figure.add_subplot(325)
        self.disk_write_ax = self.figure.add_subplot(326)

        self.axes = [
            self.cpu_ax,
            self.memory_ax,
            self.download_ax,
            self.upload_ax,
            self.disk_read_ax,
            self.disk_write_ax
        ]

        self.setup_charts()

        self.cpu_line, = self.cpu_ax.plot(
            [], linewidth=2, color="#3b82f6", label="CPU"
        )

        self.memory_line, = self.memory_ax.plot(
            [], linewidth=2, color="#22c55e", label="Memory"
        )

        self.download_line, = self.download_ax.plot(
            [], linewidth=2, color="#06b6d4", label="Download"
        )

        self.upload_line, = self.upload_ax.plot(
            [], linewidth=2, color="#f59e0b", label="Upload"
        )

        self.disk_read_line, = self.disk_read_ax.plot(
            [], linewidth=2, color="#a78bfa", label="Disk Read"
        )

        self.disk_write_line, = self.disk_write_ax.plot(
            [], linewidth=2, color="#f472b6", label="Disk Write"
        )

    def setup_charts(self):

        chart_settings = [
            (self.cpu_ax, "CPU Usage", "%", 0, 100),
            (self.memory_ax, "Memory Usage", "%", 0, 100),
            (self.download_ax, "Network Download", "KB/s", None, None),
            (self.upload_ax, "Network Upload", "KB/s", None, None),
            (self.disk_read_ax, "Disk Read", "KB/s", None, None),
            (self.disk_write_ax, "Disk Write", "KB/s", None, None)
        ]

        for ax, title, ylabel, ymin, ymax in chart_settings:

            ax.set_facecolor("#172554")

            ax.set_title(
                title,
                color="white",
                fontsize=10,
                fontweight="bold"
            )

            ax.set_ylabel(
                ylabel,
                color="#cbd5e1",
                fontsize=8
            )

            ax.tick_params(
                colors="#94a3b8",
                labelsize=8
            )

            ax.grid(
                True,
                alpha=0.2,
                linestyle="--"
            )

            if ymin is not None:
                ax.set_ylim(ymin, ymax)

            for spine in ax.spines.values():
                spine.set_color("#334155")

            ax.set_xlim(0, self.history_limit - 1)

        self.figure.tight_layout(pad=2.5)

    def update(self, history):

        chart_data = [
            (self.cpu_line, self.cpu_ax, history.get("cpu", []), True),
            (self.memory_line, self.memory_ax, history.get("memory", []), True),
            (self.download_line, self.download_ax, history.get("download", []), False),
            (self.upload_line, self.upload_ax, history.get("upload", []), False),
            (self.disk_read_line, self.disk_read_ax, history.get("disk_read", []), False),
            (self.disk_write_line, self.disk_write_ax, history.get("disk_write", []), False)
        ]

        for line, ax, values, percentage in chart_data:

            if not percentage:
                values = [
                    value / 1024 for value in values
                ]

            count = len(values)
            x_values = list(range(count))

            line.set_data(x_values, values)

            ax.set_xlim(
                0,
                max(self.history_limit - 1, count - 1)
            )

            if not percentage:

                maximum = max(values, default=0)

                ax.set_ylim(
                    0,
                    max(10, maximum * 1.2)
                )

            tick_positions = list(range(0, max(count, 1), 10))

            if count > 0 and (count - 1) not in tick_positions:
                tick_positions.append(count - 1)

            tick_labels = [
                f"-{(count - 1 - position) * self.sample_interval}s"
                for position in tick_positions
            ]

            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels)

    def get_figure(self):

        return self.figure