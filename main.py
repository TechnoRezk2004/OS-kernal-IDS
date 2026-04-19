from monitor1 import b, handle_event

b["events"].open_perf_buffer(handle_event)
print("🔍 Monitoring started...")
while True:
    b.perf_buffer_poll()