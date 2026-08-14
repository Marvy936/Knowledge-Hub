# Linux Process Signals and Graceful Shutdown

This challenge simulates a small service supervisor such as a container entrypoint or shell wrapper around a long-running application.

Work on `/workspace/service.sh`. It starts `/workspace/worker-sim` as a child process, but the starter wrapper has two production-grade bugs:

- it masks the child process exit status, so a worker failure can look successful;
- it does not forward `SIGTERM`, so stopping the wrapper can leave the worker alive and skip graceful cleanup.

Repair `service.sh` so it satisfies this behavior contract:

- `service.sh` starts `worker-sim`, records its own PID in `service.pid`, and the child PID in `worker.pid`;
- if the worker exits naturally with status `42`, the wrapper also exits with status `42`;
- when `SIGTERM` is sent to the wrapper, the wrapper forwards `SIGTERM` to the child, waits for it, and exits with the child's status;
- the worker's `SIGTERM` handler must be allowed to create `shutdown.marker` containing `shutdown=graceful` before both processes exit;
- do not use `SIGKILL` as the shutdown mechanism. `SIGKILL` cannot be trapped or forwarded gracefully and therefore bypasses cleanup.

Do not edit `worker-sim`; it is the deterministic application process used by the validator.

Start with:

```bash
cat service.sh
./service.sh &
cat service.pid worker.pid
ps -o pid,ppid,stat,comm,args | grep -E "PID|$(cat service.pid)|$(cat worker.pid)"
kill -TERM "$(cat service.pid)"
```

To inspect the failure-propagation path:

```bash
WORKER_MODE=fail ./service.sh
echo $?
```

Useful concepts are parent/child PIDs, `trap`, `kill -TERM`, `wait`, signal forwarding, exit-status propagation, and why `SIGKILL` differs from a graceful termination signal.

Lab commands: `status`, `check`, `hint`, `reset`.
