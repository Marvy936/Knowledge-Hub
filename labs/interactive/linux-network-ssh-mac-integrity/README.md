# Linux Network, SSH and MAC Integrity

Reachability is not trust, and a successful SSH login is not proof of a safe administrative path. The starter incident accepts ping/TCP/login while host-key verification is disabled, forwarding is broad, sudo is effectively unrestricted and SELinux is permissive with the wrong object label.

Repair `access_gate.py` so one exact deployment path is verified end to end.

The repaired gate must bind the exact destination name/IP/port, source address, route, interface and listener; verify the expected SSH host-key fingerprint with strict checking; require the exact deploy user and public-key authentication; disable agent/TCP forwarding and PTY; constrain sudo to the approved commands while preserving PAM account acceptance and required group membership; keep SELinux enforcing; verify process domain, persistent config type and policy generation; prove the intended deploy/restart/read-config flow; reject adjacent shadow-read, arbitrary-root-shell and forwarding flows; and prove the second identical assessment is mutation-free and byte-reproducible.

Direct practical coverage:

- `linux-networking.md`
- `ssh.md`
- `selinux-and-apparmor.md`

This lab is also intended to complete the missing sudo/PAM boundary of `users-groups-permissions-sudo-pam.md` together with the existing file-permissions lab.

Commands: `lab-help`, `status`, `hint`, `verify`, `check`, `assess`, `reset`, `self-test`.
