# Linux Cron Package Execution Integrity

A command can work in an administrator's interactive shell while the scheduled job still fails. The starter incident trusts that cron fired, `report-cli` is installed and an interactive `which report-cli` resolves. In the real scheduler context, however, cron uses a different shell, PATH and working directory; `/usr/bin/report-cli` resolves through stale filesystem state to an old non-package binary, `execve()` fails, and a logging pipeline masks the producer failure with exit status 0.

Repair `execution_gate.py` so acceptance follows the actual runtime chain from scheduler to durable outcome.

The repaired gate must bind the exact cron source/schedule/user and minimal environment; distinguish shell variables from the child process environment; verify fresh signed package metadata, completed dependencies and local package-database state; resolve the launcher to the exact package-owned target inode/owner/mode; prove `execve()` keeps the same process identity across program replacement and returns success; validate the expected APP_ENV/PATH in the actual child; preserve separate producer/logger/job exit statuses, quoting and stdout/stderr redirection semantics; require the exact durable report checkpoint; and prove a second run is mutation-free, duplicate-free and byte-reproducible.

Direct practical coverage:

- `cron-and-systemd-timers.md`
- `environment-variables.md`
- `filesystem-hierarchy-inodes-links.md`
- `kernel-and-user-space.md`
- `package-management.md`
- `processes-threads-pid-signals.md`
- `shell-bash-pipes-redirection-exit-codes.md`

This completes practical coverage for section `01-linux-and-systems`.

Commands: `lab-help`, `status`, `hint`, `assess`, `check`, `reset`, `self-test`.
