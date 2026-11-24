import psutil

def get_processes():

    processes = []

    for process in psutil.process_iter(
        ["pid", "name", "status", "memory_percent"]
    ):

        try:
            with process.oneshot():

                process_info = {
                    "pid": process.info["pid"],
                    "name": process.info["name"] or "Unknown",
                    "status": process.info["status"],
                    "cpu_percent": process.cpu_percent(interval=None),
                    "memory_percent": process.info["memory_percent"] or 0
                }

                processes.append(process_info)

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            continue

    return processes

def search_processes(processes, search_term):

    search_term = search_term.lower().strip()

    if not search_term:
        return processes

    return [
        process for process in processes
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