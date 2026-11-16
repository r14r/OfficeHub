# Optional application data migration

PR #9 moves persistent application storage from bind mounts under the old Compose
relative `../data` folder to named Docker volumes. The old files remain untouched;
**Docker does not migrate them**. Starting on empty volumes can make existing
documents, workflow definitions, vector collections, and other records disappear
from an application's UI even though the host files still exist.

## Safe upgrade sequence

1. **Stop the optional application containers** and take verified backups. Do
   not copy files from a live database or in-flight service.
2. Check the affected folders and destination volume names with
   `just volume-migration-check`. The mapping is in
   `scripts/legacy-volume-map.json`.
3. Migrate valuable application files **and related database contents**
   using a service-appropriate backup/restore procedure. Docker named volume
   names are prefixed with the project name, normally `officehub_`.
   For example, `officehub_paperless_frontend_media` becomes the Docker
   volume `officehub_officehub_paperless_frontend_media`.
4. Verify that files, owners, permissions, and application records are complete
   before restarting. Retain backups and previous host directories.
5. Once migration has been verified, explicitly acknowledge it for the new
   Compose start:

   ```bash
   OFFICEHUB_LEGACY_DATA_ACK=1 just start-all
   ```

   Or set `OFFICEHUB_LEGACY_DATA_ACK=1` in your local `.env` only
   after the old data has been backed up/migrated.

If this is a new installation with no nonempty legacy directories, no
acknowledgement is necessary. The guard runs for `just start-all` and
`just docker-app-up <profile>`. It does **not** intercept raw
`docker compose up` commands. Acknowledgement skips the protection,
not the migration: it is **not** a copy/import command.

## Paperless input/output

Paperless uses Docker volumes for internal data and media, but its
`consume` and `export` directories remain accessible from the host:

- `PAPERLESS_CONSUME_DIR` defaults to
  `$HOME/.local/share/officehub/paperless/consume`.
- `PAPERLESS_EXPORT_DIR` defaults to
  `$HOME/.local/share/officehub/paperless/export`.

Create both directories with normal user permissions:

```bash
mkdir -p "$HOME/.local/share/officehub/paperless/"{consume,export}
```

Place files in `consume` for Paperless to import. The default location is
outside a cloud-synced repository; override both variables in `.env`
with **absolute, writable, non-cloud paths** if needed. If old
`../data/officehub-paperless-frontend/consume` or `export` contained
files, copy those to the new folders before acknowledgement.

On macOS, avoid using synchronized iCloud/Dropbox/OneDrive paths for
Docker database directories or mounts that require ownership changes.

## Recovery and destructive operations

The preflight does not move, overwrite, or delete data. A populated old
directory is intentionally sufficient to block startup, even if new data
has already been migrated, until explicitly acknowledged. This avoids
mistaking stale data for a clean install.

Never use `docker compose down -v` as part of migration. It destroys
Docker-managed volumes. Review `docs/database-volumes.md` for SQL
database-specific backup/restore guidance. Bind-mounted database data
may have been migrated in an earlier PR and is not covered by this
PR's application-file guard.
