# PostgreSQL Backup Restore

A PostgreSQL table has suffered partial data loss. The lab creates a real plain-text logical backup with `pg_dump`, then removes one customer from the live table. Recover the table from `/workspace/customers-backup.sql` and use `check` to prove all expected rows are present again.

The intended workflow uses PostgreSQL tooling against the disposable database container; no PostgreSQL client is required on the host.
