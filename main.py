import customtkinter as ctk
import tkinter as tk
import threading
import time

from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from components.system_info import (
    get_system_info,
    format_bytes
)

from components.monitor import SystemMonitor
from components.charts import PerformanceCharts

from components.process_manager import (
    get_processes,
    search_processes,
    sort_processes,
    terminate_process
)

from components.performance_profiler import profile_function


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SystemResourceMonitor(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("System Resource Monitor")
        self.geometry("1450x950")
        self.minsize(1100, 750)

        self.colors = {
            "background": "#0f172a",
            "sidebar": "#111c35",
            "card": "#172554",
            "border": "#263858",
            "text": "#f8fafc",
            "muted": "#94a3b8",
            "accent": "#3b82f6",
            "danger": "#dc2626",
            "success": "#16a34a"
        }

        self.configure(
            fg_color=self.colors["background"]
        )

        self.monitor = SystemMonitor(history_limit=30)

        self.running = True

        self.process_loading = False
        self.cached_processes = []
        self.process_refresh_job = None
        self.process_lock = threading.Lock()

        self.metrics_refresh_job = None
        self.previous_label_values = {}
        self.previous_chart_history = None

        self.create_interface()

        self.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )

        self.update_metrics()
        self.refresh_process_table()

    def update_label(self, label, key, value):

        if self.previous_label_values.get(key) != value:

            label.configure(text=value)

            self.previous_label_values[key] = value

    def create_interface(self):

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()
        self.create_main_content()

    def create_sidebar(self):

        self.sidebar = ctk.CTkFrame(
            self,
            width=230,
            corner_radius=0,
            fg_color=self.colors["sidebar"]
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text="SYSTEM MONITOR",
            font=("Segoe UI", 20, "bold"),
            text_color=self.colors["text"]
        ).pack(
            pady=(35, 5),
            padx=20
        )

        ctk.CTkLabel(
            self.sidebar,
            text="Performance Dashboard",
            font=("Segoe UI", 11),
            text_color=self.colors["muted"]
        ).pack(pady=(0, 35))

        navigation_items = [
            ("Overview", "overview"),
            ("Processes", "processes"),
            ("Performance", "performance"),
            ("System Information", "information")
        ]

        self.nav_buttons = {}

        for label, section in navigation_items:

            button = ctk.CTkButton(
                self.sidebar,
                text=label,
                height=45,
                corner_radius=8,
                anchor="w",
                fg_color="transparent",
                hover_color=self.colors["card"],
                text_color=self.colors["text"],
                font=("Segoe UI", 13),
                command=lambda s=section: self.navigate_to(s)
            )

            button.pack(
                fill="x",
                padx=15,
                pady=5
            )

            self.nav_buttons[section] = button

        ctk.CTkButton(
            self.sidebar,
            text="Refresh Dashboard",
            height=40,
            corner_radius=8,
            fg_color=self.colors["accent"],
            hover_color="#2563eb",
            command=self.refresh_dashboard
        ).pack(
            side="bottom",
            fill="x",
            padx=15,
            pady=(5, 15)
        )

        ctk.CTkLabel(
            self.sidebar,
            text="LOCAL SYSTEM MONITOR",
            font=("Segoe UI", 10),
            text_color=self.colors["muted"]
        ).pack(
            side="bottom",
            pady=15
        )

    def create_main_content(self):

        self.main_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.main_frame.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=25,
            pady=20
        )

        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 15)
        )

        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="System Overview",
            font=("Segoe UI", 28, "bold"),
            text_color=self.colors["text"]
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.status_label = ctk.CTkLabel(
            header,
            text="● Monitoring Active",
            font=("Segoe UI", 12),
            text_color="#22c55e"
        )

        self.status_label.grid(
            row=0,
            column=1,
            sticky="e"
        )

        self.content_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="transparent",
            scrollbar_button_color=self.colors["border"],
            scrollbar_button_hover_color=self.colors["accent"]
        )

        self.content_frame.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

        self.content_frame.grid_columnconfigure(0, weight=1)

        self.create_metrics_section()
        self.create_charts_section()
        self.create_processes_section()
        self.create_system_information()

    def navigate_to(self, section):

        sections = {
            "overview": self.metrics_section,
            "processes": self.processes_section,
            "performance": self.charts_section,
            "information": self.information_section
        }

        target = sections.get(section)

        if target is None:
            return

        canvas = self.content_frame._parent_canvas

        def scroll_to_section():

            if not self.running:
                return

            canvas.update_idletasks()

            bounds = canvas.bbox("all")

            if bounds:

                total_height = bounds[3]

                if total_height > 0:

                    position = target.winfo_y() / total_height

                    canvas.yview_moveto(position)

        self.after(50, scroll_to_section)

        for key, button in self.nav_buttons.items():

            button.configure(
                fg_color=(
                    self.colors["accent"]
                    if key == section
                    else "transparent"
                )
            )

    def create_metric_card(
        self,
        parent,
        title,
        value,
        subtitle,
        column
    ):

        card = ctk.CTkFrame(
            parent,
            fg_color=self.colors["card"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["border"]
        )

        card.grid(
            row=0,
            column=column,
            sticky="nsew",
            padx=6,
            pady=6
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 11, "bold"),
            text_color=self.colors["muted"]
        ).pack(
            anchor="w",
            padx=15,
            pady=(18, 5)
        )

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Segoe UI", 25, "bold"),
            text_color=self.colors["text"]
        )

        value_label.pack(
            anchor="w",
            padx=15,
            pady=5
        )

        subtitle_label = ctk.CTkLabel(
            card,
            text=subtitle,
            font=("Segoe UI", 10),
            text_color=self.colors["muted"]
        )

        subtitle_label.pack(
            anchor="w",
            padx=15,
            pady=(0, 18)
        )

        return value_label, subtitle_label

    def create_metrics_section(self):

        self.metrics_section = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )

        self.metrics_section.pack(
            fill="x",
            pady=(5, 15)
        )

        ctk.CTkLabel(
            self.metrics_section,
            text="Resource Overview",
            font=("Segoe UI", 19, "bold"),
            text_color=self.colors["text"]
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        cards_frame = ctk.CTkFrame(
            self.metrics_section,
            fg_color="transparent"
        )

        cards_frame.pack(fill="x")

        for column in range(5):
            cards_frame.grid_columnconfigure(column, weight=1)

        self.cpu_value, self.cpu_subtitle = self.create_metric_card(
            cards_frame,
            "CPU USAGE",
            "0%",
            "Processor utilization",
            0
        )

        self.memory_value, self.memory_subtitle = self.create_metric_card(
            cards_frame,
            "MEMORY USAGE",
            "0%",
            "RAM utilization",
            1
        )

        self.disk_value, self.disk_subtitle = self.create_metric_card(
            cards_frame,
            "DISK USAGE",
            "0%",
            "Storage utilization",
            2
        )

        self.download_value, self.download_subtitle = self.create_metric_card(
            cards_frame,
            "DOWNLOAD",
            "0 B/s",
            "Network download",
            3
        )

        self.upload_value, self.upload_subtitle = self.create_metric_card(
            cards_frame,
            "UPLOAD",
            "0 B/s",
            "Network upload",
            4
        )

    @profile_function
    def update_metrics(self):

        if not self.running:
            return

        try:

            total_start = time.perf_counter()

            metrics_start = time.perf_counter()

            metrics = self.monitor.get_metrics()

            metrics_time = time.perf_counter() - metrics_start

            cpu = metrics["cpu"]
            memory = metrics["memory"]
            disks = metrics["disks"]
            network = metrics["network"]

            labels_start = time.perf_counter()

            self.update_label(
                self.cpu_value,
                "cpu_value",
                f"{cpu['usage']:.1f}%"
            )

            self.update_label(
                self.cpu_subtitle,
                "cpu_subtitle",
                f"{cpu['cores']} cores / {cpu['threads']} threads"
            )

            self.update_label(
                self.memory_value,
                "memory_value",
                f"{memory['percent']:.1f}%"
            )

            self.update_label(
                self.memory_subtitle,
                "memory_subtitle",
                f"{format_bytes(memory['used'])} / {format_bytes(memory['total'])}"
            )

            if disks:

                disk = disks[0]

                self.update_label(
                    self.disk_value,
                    "disk_value",
                    f"{disk['percent']:.1f}%"
                )

                self.update_label(
                    self.disk_subtitle,
                    "disk_subtitle",
                    f"{disk['mountpoint']} - {format_bytes(disk['free'])} free"
                )

            else:

                self.update_label(
                    self.disk_value,
                    "disk_value",
                    "N/A"
                )

                self.update_label(
                    self.disk_subtitle,
                    "disk_subtitle",
                    "No available drives"
                )

            self.update_label(
                self.download_value,
                "download_value",
                f"{format_bytes(network['download_speed'])}/s"
            )

            self.update_label(
                self.upload_value,
                "upload_value",
                f"{format_bytes(network['upload_speed'])}/s"
            )

            labels_time = time.perf_counter() - labels_start

            chart_start = time.perf_counter()

            history = metrics["history"]

            current_history = {
                key: tuple(values)
                for key, values in history.items()
            }

            if current_history != self.previous_chart_history:

                self.charts.update(history)

                self.previous_chart_history = current_history

                self.chart_canvas.draw_idle()

            chart_time = time.perf_counter() - chart_start

            total_time = time.perf_counter() - total_start

            print(
                f"[METRICS BREAKDOWN] "
                f"Collection: {metrics_time * 1000:.2f} ms | "
                f"Labels: {labels_time * 1000:.2f} ms | "
                f"Charts: {chart_time * 1000:.2f} ms | "
                f"Total: {total_time * 1000:.2f} ms"
            )

        except Exception as error:

            print("Monitoring error:", error)

        if self.running:

            self.metrics_refresh_job = self.after(
                2000,
                self.update_metrics
            )

    def create_charts_section(self):

        self.charts_section = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )

        self.charts_section.pack(
            fill="x",
            pady=15
        )

        ctk.CTkLabel(
            self.charts_section,
            text="Performance Monitoring",
            font=("Segoe UI", 19, "bold"),
            text_color=self.colors["text"]
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        chart_container = ctk.CTkFrame(
            self.charts_section,
            fg_color=self.colors["card"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["border"]
        )

        chart_container.pack(
            fill="x",
            expand=True
        )

        self.charts = PerformanceCharts(chart_container)

        self.chart_canvas = FigureCanvasTkAgg(
            self.charts.get_figure(),
            master=chart_container
        )

        self.chart_canvas.get_tk_widget().pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    def create_processes_section(self):

        self.processes_section = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )

        self.processes_section.pack(
            fill="x",
            pady=15
        )

        ctk.CTkLabel(
            self.processes_section,
            text="Running Processes",
            font=("Segoe UI", 19, "bold"),
            text_color=self.colors["text"]
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        process_container = ctk.CTkFrame(
            self.processes_section,
            fg_color=self.colors["card"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["border"]
        )

        process_container.pack(
            fill="both",
            expand=True
        )

        controls = ctk.CTkFrame(
            process_container,
            fg_color="transparent"
        )

        controls.pack(
            fill="x",
            padx=15,
            pady=15
        )

        self.process_search = ctk.CTkEntry(
            controls,
            placeholder_text="Search process name...",
            width=250,
            height=38
        )

        self.process_search.pack(
            side="left",
            padx=(0, 10)
        )

        self.process_search.bind(
            "<KeyRelease>",
            self.search_process_table
        )

        self.sort_option = ctk.CTkOptionMenu(
            controls,
            values=[
                "Memory Usage",
                "CPU Usage",
                "Process Name"
            ],
            width=150,
            height=38,
            command=lambda value: self.update_process_table()
        )

        self.sort_option.set("Memory Usage")

        self.sort_option.pack(
            side="left",
            padx=5
        )

        ctk.CTkButton(
            controls,
            text="Refresh",
            width=90,
            height=38,
            command=self.refresh_process_table
        ).pack(
            side="left",
            padx=5
        )

        ctk.CTkButton(
            controls,
            text="Terminate Process",
            width=150,
            height=38,
            fg_color=self.colors["danger"],
            hover_color="#b91c1c",
            command=self.terminate_selected_process
        ).pack(
            side="right",
            padx=5
        )

        table_frame = ctk.CTkFrame(
            process_container,
            fg_color="transparent"
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            background="#111c35",
            foreground="#f8fafc",
            fieldbackground="#111c35",
            rowheight=30,
            borderwidth=0,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Treeview.Heading",
            background="#263858",
            foreground="#f8fafc",
            font=("Segoe UI", 10, "bold"),
            relief="flat"
        )

        style.map(
            "Treeview",
            background=[("selected", "#2563eb")],
            foreground=[("selected", "#ffffff")]
        )

        columns = (
            "pid",
            "name",
            "cpu",
            "memory",
            "status"
        )

        self.process_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12
        )

        headings = {
            "pid": ("PID", 80),
            "name": ("Process Name", 280),
            "cpu": ("CPU Usage", 120),
            "memory": ("Memory Usage", 140),
            "status": ("Status", 120)
        }

        for column, (heading, width) in headings.items():

            self.process_table.heading(
                column,
                text=heading
            )

            self.process_table.column(
                column,
                width=width,
                anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.process_table.yview
        )

        self.process_table.configure(
            yscrollcommand=scrollbar.set
        )

        self.process_table.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.process_table.bind(
            "<Double-1>",
            lambda event: self.terminate_selected_process()
        )

    def search_process_table(self, event=None):
        self.update_process_table()

    @profile_function
    def update_process_table(self):

        if not self.running:
            return

        try:

            processes = self.cached_processes

            search_term = self.process_search.get()

            processes = search_processes(
                processes,
                search_term
            )

            selected_sort = self.sort_option.get()

            sort_mapping = {
                "Memory Usage": "memory_percent",
                "CPU Usage": "cpu_percent",
                "Process Name": "name"
            }

            sort_key = sort_mapping[selected_sort]

            if sort_key == "name":

                processes = sorted(
                    processes,
                    key=lambda process: process["name"].lower()
                )

            else:

                processes = sort_processes(
                    processes,
                    sort_key
                )

            existing_items = {
                self.process_table.item(item, "values")[0]: item
                for item in self.process_table.get_children()
            }

            current_pids = set()

            for process in processes:

                pid = str(process["pid"])
                current_pids.add(pid)

                values = (
                    pid,
                    process["name"],
                    f"{process['cpu_percent']:.1f}%",
                    f"{process['memory_percent']:.2f}%",
                    process["status"]
                )

                if pid in existing_items:

                    item = existing_items[pid]

                    if self.process_table.item(item, "values") != values:
                        self.process_table.item(
                            item,
                            values=values
                        )

                    self.process_table.move(
                        item,
                        "",
                        len(current_pids) - 1
                    )

                else:

                    self.process_table.insert(
                        "",
                        "end",
                        values=values
                    )

            for pid, item in existing_items.items():

                if pid not in current_pids:
                    self.process_table.delete(item)

        except Exception as error:

            print("Process table error:", error)

    def refresh_process_table(self):

        if not self.running:
            return

        if self.process_refresh_job is not None:

            try:
                self.after_cancel(self.process_refresh_job)
            except tk.TclError:
                pass

        self.process_refresh_job = self.after(
            15000,
            self.refresh_process_table
        )

        with self.process_lock:

            if self.process_loading:
                return

            self.process_loading = True

        def load_processes():

            try:

                processes = get_processes()

                try:

                    self.after(
                        0,
                        lambda result=processes:
                            self.finish_process_refresh(result)
                    )

                except (RuntimeError, tk.TclError):
                    pass

            except Exception as error:

                error_message = str(error)

                try:

                    self.after(
                        0,
                        lambda msg=error_message:
                            self.finish_process_refresh(
                                None,
                                msg
                            )
                    )

                except (RuntimeError, tk.TclError):
                    pass

        threading.Thread(
            target=load_processes,
            daemon=True,
            name="ProcessCollector"
        ).start()

    @profile_function
    def finish_process_refresh(self, processes, error=None):

        if not self.running:
            return

        with self.process_lock:
            self.process_loading = False

        if error:

            print(
                f"[PROCESS MANAGER] Refresh error: {error}"
            )

            return

        if processes is None:
            return

        self.cached_processes = processes

        self.update_process_table()

    @profile_function
    def terminate_selected_process(self):

        selected = self.process_table.selection()

        if not selected:

            messagebox.showwarning(
                "No Process Selected",
                "Please select a process first."
            )

            return

        values = self.process_table.item(
            selected[0],
            "values"
        )

        pid = int(values[0])
        process_name = values[1]

        confirm = messagebox.askyesno(
            "Confirm Termination",
            (
                f"Are you sure you want to terminate "
                f"{process_name} (PID: {pid})?\n\n"
                "This may cause the selected application "
                "to close unexpectedly."
            )
        )

        if not confirm:
            return

        try:

            terminate_process(pid)

            messagebox.showinfo(
                "Process Terminated",
                f"{process_name} was terminated successfully."
            )

            self.refresh_process_table()

        except Exception as error:

            messagebox.showerror(
                "Termination Failed",
                (
                    "Unable to terminate this process.\n\n"
                    f"{error}"
                )
            )

    def create_system_information(self):

        self.information_section = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )

        self.information_section.pack(
            fill="x",
            pady=(15, 30)
        )

        ctk.CTkLabel(
            self.information_section,
            text="System Information",
            font=("Segoe UI", 19, "bold"),
            text_color=self.colors["text"]
        ).pack(
            anchor="w",
            pady=(0, 10)
        )

        system = get_system_info()

        info_frame = ctk.CTkFrame(
            self.information_section,
            fg_color=self.colors["card"],
            corner_radius=12,
            border_width=1,
            border_color=self.colors["border"]
        )

        info_frame.pack(fill="x")

        info_frame.grid_columnconfigure(
            (0, 1),
            weight=1
        )

        information = [
            ("Computer Name", system["hostname"]),
            ("Operating System", system["system"]),
            ("OS Version", system["release"]),
            ("Processor", system["processor"] or "Not available")
        ]

        for index, (label, value) in enumerate(information):

            row = index // 2
            column = index % 2

            item_frame = ctk.CTkFrame(
                info_frame,
                fg_color="transparent"
            )

            item_frame.grid(
                row=row,
                column=column,
                sticky="ew",
                padx=20,
                pady=18
            )

            ctk.CTkLabel(
                item_frame,
                text=label,
                font=("Segoe UI", 11),
                text_color=self.colors["muted"]
            ).pack(anchor="w")

            ctk.CTkLabel(
                item_frame,
                text=value,
                font=("Segoe UI", 14, "bold"),
                text_color=self.colors["text"],
                wraplength=450
            ).pack(
                anchor="w",
                pady=(5, 0)
            )

    @profile_function
    def refresh_dashboard(self):

        if not self.running:
            return

        if self.metrics_refresh_job is not None:

            try:
                self.after_cancel(self.metrics_refresh_job)
            except tk.TclError:
                pass

            self.metrics_refresh_job = None

        self.update_metrics()
        self.refresh_process_table()

    def on_close(self):

        if not self.running:
            return

        self.running = False

        for job in (
            self.process_refresh_job,
            self.metrics_refresh_job
        ):

            if job is not None:

                try:
                    self.after_cancel(job)
                except tk.TclError:
                    pass

        self.destroy()


if __name__ == "__main__":

    app = SystemResourceMonitor()
    app.mainloop()
