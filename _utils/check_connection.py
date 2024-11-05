import subprocess
import sys
import threading
import uuid

from _log import log_error, log_info, log_warn


_monitor_threads = {}
_stop_events = {}


def check_internet_connection():
    try:
        subprocess.check_call(
            ["ping", "-c", "1", "www.google.ru"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except subprocess.CalledProcessError:
        return False


def monitor_internet_connection(stop_event, monitor_id, max_retries=10, delay=5):
    retry_count = 0
    internet = False

    while retry_count < max_retries and not stop_event.is_set():
        if check_internet_connection():
            internet = True
            retry_count = 0
            stop_event.wait(delay)
        else:
            if retry_count % 2 == 0:
                log_warn(f"Monitor {monitor_id}: Internet is still down.")
            internet = False
            retry_count += 1
            stop_event.wait(delay)

    if not internet:
        log_error(f"Monitor {monitor_id}: No internet connection after {max_retries} attempts or script complete.")
        sys.exit()


def start_monitor(max_retries=10, delay=5):
    monitor_id = str(uuid.uuid4())
    stop_event = threading.Event()
    monitor_thread = threading.Thread(
        target=monitor_internet_connection, args=(stop_event, monitor_id, max_retries, delay)
    )

    # Store the thread and stop event in dictionaries
    _stop_events[monitor_id] = stop_event
    _monitor_threads[monitor_id] = monitor_thread

    # Start the monitor thread
    monitor_thread.start()

    log_info(f"Started monitor with ID: {monitor_id}")
    return monitor_id


def stop_monitor(monitor_id):
    if monitor_id in _stop_events:
        _stop_events[monitor_id].set()  # Signal the monitor to stop
        _monitor_threads[monitor_id].join()  # Wait for the monitor to finish

        del _stop_events[monitor_id]
        del _monitor_threads[monitor_id]

        log_info(f"Stopped monitor with ID: {monitor_id}")
    else:
        log_warn(f"No monitor found with ID: {monitor_id}")
