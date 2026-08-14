# Linux File Permissions

This challenge practices the effective Unix owner/group/other permission model with three local service accounts.

Work on `/workspace/config/app.conf`.

Required access contract:

- `kh-deploy` owns the file and can read and write it;
- group `kh-app` owns the group slot and `kh-app` can read but not write;
- `kh-guest` has no read or write access;
- the file content remains exactly `MODE=production`.

The starter state is intentionally over-permissive. Repair ownership and mode without changing the required content.

Start with:

```bash
status
ls -l /workspace/config/app.conf
stat /workspace/config/app.conf
id kh-deploy
id kh-app
id kh-guest
```

Useful commands include `chown`, `chgrp`, `chmod`, `stat`, and `id`. Think in terms of which permission class applies to each process: owner, group, or other.

When finished, run `check`.

Lab commands: `status`, `check`, `hint`, `reset`.
