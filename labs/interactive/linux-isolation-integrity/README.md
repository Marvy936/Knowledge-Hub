# Linux Isolation Integrity

A workload can be called a container and run as UID `0` without being safely isolated. The starter incident shares the host PID/network/IPC/user namespaces, sits in an effectively unbounded cgroup and retains broad capabilities such as `CAP_SYS_ADMIN`, `CAP_NET_ADMIN` and `CAP_SYS_PTRACE`. Local metadata therefore claims isolation while the kernel still permits host-affecting operations.

Repair `isolation_gate.py` so acceptance is based on effective kernel boundaries rather than labels or namespace-root identity.

The repaired gate must prove distinct PID, mount, network, UTS, IPC and user namespace identities; bind inside PID `1` to a non-root host UID mapping; verify exact cgroup v2 placement plus effective CPU, memory and PIDs limits; require zero unexpected cgroup OOM events; validate effective, permitted, bounding and ambient capability sets after execution; enforce `no_new_privs`; allow the one required privileged operation (`bind` to port `443`) while proving adjacent mount, host-ptrace and route-change operations are denied; preserve the shared-kernel model explicitly; and prove an identical second assessment is mutation-free and byte-reproducible.

Direct practical coverage:

- `namespaces.md`
- `cgroups.md`
- `linux-capabilities.md`

Partial practical coverage:

- `kernel-and-user-space.md`

Commands: `lab-help`, `status`, `hint`, `assess`, `check`, `reset`, `self-test`.
