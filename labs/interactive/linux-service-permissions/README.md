# Linux Service Permissions

A service account named `khapp` must read `/workspace/secure/app.env`, but the supplied ownership and mode bits block access.

Repair the filesystem permissions using least privilege. The final contract is:

- `/workspace/secure` is owned by `root:khapp` with mode `0750`;
- `/workspace/secure/app.env` is owned by `root:khapp` with mode `0640`;
- `khapp` can read the file and sees exactly `API_MODE=production`;
- `khapp` cannot modify the file;
- the file remains owned by `root` and no world permissions are granted.

Do not solve the exercise with `chmod 777`, by changing the file owner to the service user, or by running the application as root.

Start with:

```bash
id khapp
stat -c '%U:%G %a %n' secure secure/app.env
su-exec khapp:khapp cat secure/app.env
```

Remember that directory execute permission controls pathname traversal, while file read permission controls reading the inode once the path can be resolved.

Lab commands: `status`, `check`, `hint`, `reset`.
