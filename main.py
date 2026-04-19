from monitor1 import b, handle_event
import signal
import sys

def signal_handler(sig, frame):
    print("\n⛔ Monitoring stopped.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

b["events"].open_perf_buffer(handle_event, page_cnt=64)
print("🔍 Monitoring started... Press Ctrl+Z to stop")

while True:
    b.perf_buffer_poll(timeout=100)
