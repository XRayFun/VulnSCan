import subprocess
import sys
import threading
import uuid

from _log import vsc_log, logger

_monitor_threads = {}
_stop_events = {}

_module_name = "utils.check_connection"


@logger(_module_name)
def check_internet_connection():
    try:
        subprocess.check_call(
            ["ping", "-c", "1", "google.com"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False


@logger(_module_name)
def _monitor_internet_connection(stop_event:threading.Event, monitor_id:uuid.UUID, max_retries:int=10, delay:int=5):
    retry_count = 0
    internet = False

    while retry_count < max_retries and not stop_event.is_set():
        if check_internet_connection():
            internet = True
            retry_count = 0
            stop_event.wait(delay)
        else:
            if retry_count % 2 == 0:
                vsc_log.warn_result(_module_name, f"Monitor {str(monitor_id)}: Internet is still down.")
            internet = False
            retry_count += 1
            stop_event.wait(delay)

    if not internet:
        vsc_log.error_result(_module_name, f"Monitor {str(monitor_id)}: No internet connection after {max_retries} attempts or script complete.")
        sys.exit()


@logger(_module_name)
def start_monitor(max_retries:int=10, delay:int=5) -> uuid.UUID:
    monitor_id = uuid.uuid4()
    stop_event = threading.Event()
    monitor_thread = threading.Thread(
        target=_monitor_internet_connection, args=(stop_event, monitor_id, max_retries, delay)
    )

    # Store the thread and stop event in dictionaries
    _stop_events[monitor_id] = stop_event
    _monitor_threads[monitor_id] = monitor_thread

    # Start the monitor thread
    monitor_thread.start()
    vsc_log.info_status_result(_module_name, "START", f"Monitor of connection with ID: {monitor_id}")

    return monitor_id


@logger(_module_name)
def stop_monitor(monitor_id:uuid.UUID):
    if monitor_id in _stop_events:
        _stop_events[monitor_id].set()  # Signal the monitor to stop
        _monitor_threads[monitor_id].join()  # Wait for the monitor to finish

        del _stop_events[monitor_id]
        del _monitor_threads[monitor_id]

        vsc_log.info_status_result(_module_name, "STOP", f"Monitor of connection with ID: {monitor_id}")
    else:
        vsc_log.warn_status_result(_module_name, "FAILED", f"No monitor of connection found with ID: {monitor_id}")
