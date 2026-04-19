from bcc import BPF
import pickle
import numpy as np

with open("/home/f/Downloads/archive (1)/ids_model.pkl", "rb") as f:
    model = pickle.load(f)

bpf_program = """
#include <uapi/linux/ptrace.h>
struct data_t {
    u32 pid;
    u64 syscall_id;
    char comm[16];
};
BPF_PERF_OUTPUT(events);
TRACEPOINT_PROBE(raw_syscalls, sys_enter) {
    struct data_t data = {};
    data.pid = bpf_get_current_pid_tgid() >> 32;
    data.syscall_id = args->id;
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    events.perf_submit(args, &data, sizeof(data));
    return 0;
}
"""

b = BPF(text=bpf_program)
print("✅ BPF Compiled!")

process_buffers = {}

IGNORE_LIST = [
    b"firefox", b"code", b"VS Code", b"Xorg",
    b"python3", b"gnome", b"systemd", b"snapd"
]

def predict(pid, comm, buffer):
    freq = np.zeros(400)
    for s in buffer:
        if s < 400:
            freq[s] += 1
    prediction = model.predict([freq])[0]
    confidence = model.predict_proba([freq])[0]
    if prediction == 1:
        print(f"🚨 ANOMALY DETECTED! Process: {comm} | PID: {pid} | Confidence: {confidence[1]:.2%}")
    else:
        print(f"✅ Normal | Process: {comm} | PID: {pid} | Confidence: {confidence[0]:.2%}")

def handle_event(cpu, data, size):
    event = b["events"].event(data)
    comm = event.comm
    for ignore in IGNORE_LIST:
        if ignore in comm:
            return
    pid = event.pid
    if pid not in process_buffers:
        process_buffers[pid] = []
    process_buffers[pid].append(int(event.syscall_id))
    if len(process_buffers[pid]) >= 50:
        predict(pid, comm.decode('utf-8', errors='replace'), process_buffers[pid])
        process_buffers[pid] = []
