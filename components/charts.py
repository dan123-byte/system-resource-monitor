from matplotlib.figure import Figure

class PerformanceCharts:

    def __init__(self, parent):

        self.figure = Figure(
            figsize=(10, 6),
            dpi=100,
            facecolor="#0f172a"
        )

        self.cpu_ax = self.figure.add_subplot(221)
        self.memory_ax = self.figure.add_subplot(222)
        self.download_ax = self.figure.add_subplot(223)
        self.upload_ax = self.figure.add_subplot(224)

        self.axes = [
            self.cpu_ax,
            self.memory_ax,
            self.download_ax,
            self.upload_ax
        ]

        self.setup_charts()

        self.cpu_line, = self.cpu_ax.plot(
            [], linewidth=2, color="#3b82f6"
        )

        self.memory_line, = self.memory_ax.plot(
            [], linewidth=2, color="#22c55e"
        )

        self.download_line, = self.download_ax.plot(
            [], linewidth=2, color="#06b6d4"
        )

        self.upload_line, = self.upload_ax.plot(
            [], linewidth=2, color="#f59e0b"
        )

    def setup_charts(self):

        chart_settings = [
            (self.cpu_ax, "CPU Usage", "%", 0, 100),
            (self.memory_ax, "Memory Usage", "%", 0, 100),
            (self.download_ax, "Download Speed", "KB/s", None, None),
            (self.upload_ax, "Upload Speed", "KB/s", None, None)
        ]

        for ax, title, ylabel, ymin, ymax in chart_settings:

            ax.set_facecolor("#172554")
            ax.set_title(title, color="white", fontsize=11)
            ax.set_ylabel(ylabel, color="white")

            ax.tick_params(colors="white")
            ax.grid(True, alpha=0.2)

            if ymin is not None:
                ax.set_ylim(ymin, ymax)

            for spine in ax.spines.values():
                spine.set_color("#334155")

        self.figure.tight_layout(pad=3)

    def update(self, history):

        self.cpu_line.set_data(
            range(len(history["cpu"])),
            history["cpu"]
        )

        self.memory_line.set_data(
            range(len(history["memory"])),
            history["memory"]
        )

        download_values = [
            value / 1024 for value in history["download"]
        ]

        upload_values = [
            value / 1024 for value in history["upload"]
        ]

        self.download_line.set_data(
            range(len(download_values)),
            download_values
        )

        self.upload_line.set_data(
            range(len(upload_values)),
            upload_values
        )

        for ax, values in [
            (self.cpu_ax, history["cpu"]),
            (self.memory_ax, history["memory"]),
            (self.download_ax, download_values),
            (self.upload_ax, upload_values)
        ]:

            ax.set_xlim(0, max(30, len(values) - 1))

            if ax not in [self.cpu_ax, self.memory_ax]:

                maximum = max(values, default=0)

                ax.set_ylim(
                    0,
                    max(10, maximum * 1.2)
                )

    def get_figure(self):

        return self.figure
