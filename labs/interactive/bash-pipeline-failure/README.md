# Bash Pipeline Failure Propagation

This challenge demonstrates a common CI/CD shell bug: an upstream build command fails, but its output is piped through `tee`, so the script observes the successful status of the last pipeline command and continues as if the build succeeded.

Work on `/workspace/deploy.sh`.

The script must satisfy both paths:

- when `BUILD_OUTCOME=fail`, it must exit non-zero, preserve the build log, and must not create `release.marker`;
- when `BUILD_OUTCOME=success`, it must exit zero, preserve the build log, and create `release.marker` containing `release=ready`.

The supplied `build-sim` command is deterministic. Do not edit it; repair the shell error propagation in `deploy.sh`.

Start with:

```bash
cat deploy.sh
BUILD_OUTCOME=fail ./deploy.sh
echo $?
ls -l build.log release.marker
```

Useful concepts are pipeline exit status, `pipefail`, `${PIPESTATUS[@]}`, and the interaction between pipeline status and `set -e`.

Lab commands: `status`, `check`, `hint`, `reset`.
