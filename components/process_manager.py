import time
import psutil


def get_processes():

    start_time = time.perf_counter()

    processes = []
    skipped = 0

    total_memory = psutil.virtual_memory().total

    loop_start = time.perf_counter()

    for process in psutil.process_iter(
        ["pid", "name", "status", "memory_info"]
    ):

        try:

            info = process.info

            memory_info = info["memory_info"]

            if memory_info and total_memory > 0:
                memory_percent = (
                    memory_info.rss / total_memory
                ) * 100
            else:
                memory_percent = 0.0

            cpu_percent = process.cpu_percent(interval=None)

            processes.append({
                "pid": info["pid"],
                "name": info["name"] or "Unknown",
                "status": info["status"] or "Unknown",
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent
            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            skipped += 1

    loop_time = time.perf_counter() - loop_start
    elapsed = time.perf_counter() - start_time

    print(
        f"[PROCESS DEBUG] "
        f"Loop time: {loop_time * 1000:.2f} ms | "
        f"Processes: {len(processes)}"
    )

    print(
        f"[PROCESS MANAGER] "
        f"Collected: {len(processes)} | "
        f"Skipped: {skipped} | "
        f"Time: {elapsed * 1000:.2f} ms"
    )

    return processes


def search_processes(processes, search_term):

    search_term = search_term.lower().strip()

    if not search_term:
        return processes

    return [
        process
        for process in processes
        if search_term in process["name"].lower()
    ]


def sort_processes(processes, sort_by="memory_percent"):

    return sorted(
        processes,
        key=lambda process: process.get(sort_by, 0),
        reverse=True
    )


def terminate_process(pid):

    process = psutil.Process(pid)

    process.terminate()

    process.wait(timeout=3)

    return True
