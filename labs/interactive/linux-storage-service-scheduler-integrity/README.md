# Linux Storage, Service and Scheduler Integrity

A systemd timer can be `active (waiting)` while the work it schedules is failing. The starter incident treats that timer state as backup success even though `backup.service` exited after `ENOSPC`, the backup pathname resolves to the wrong filesystem, `df` and `du` disagree because a deleted inode is still held open, the current symlink is dangling, and no verified backup artifact exists.

Repair `linux_backup_gate.py` so acceptance follows the full Linux execution and storage path rather than one manager status.

The repaired gate must bind the exact target pathname to the expected mount source, filesystem type and writable options; reconcile visible usage with deleted-open inode evidence; verify target inode plus symlink/hard-link identity; separate `.timer` activation from `.service` execution; verify effective oneshot unit identity, result and process-tree cleanup; use service-scoped journal evidence with boot/run identity and a positive completion event; verify exact backup bytes, manifest count and remote outcome; keep timer-active and exit-zero as evidence only; and prove replay of the same logical run creates no duplicate artifact and remains byte-reproducible.

Direct practical coverage:

- `storage-mounts-and-filesystems.md`
- `systemd-services-daemons.md`
- `journald-and-logging.md`

Partial practical coverage:

- `filesystem-hierarchy-inodes-links.md`
- `cron-and-systemd-timers.md`

Commands: `lab-help`, `status`, `hint`, `diagnose`, `check`, `assess`, `reset`, `self-test`.
