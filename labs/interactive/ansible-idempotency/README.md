# Ansible Idempotency

This lab teaches a common Ansible convergence failure. The supplied playbook uses `ansible.builtin.file` with `state: touch`, so every identical run updates file metadata and reports a change. Replacing it with a no-op file-state check is not sufficient either: configuration management must also restore the desired content when drift occurs.

Repair `/workspace/site.yml` so Ansible owns the complete file contract:

- content is exactly `MODE=production` followed by a newline;
- mode is `0644`;
- a run against drift reports a real change and restores the desired state;
- the next identical run converges with `changed=0`.

`check` injects a controlled content drift before validation, so the solution must actually reconcile the file rather than rely on the initial fixture already being correct.

Start with:

```bash
cat site.yml
apply
apply
check
```

Lab commands: `status`, `apply`, `check`, `hint`, `reset`.

This is a shell-profile lab. The learner host needs Docker, but this lab itself does not require `--privileged` or nested Docker.
