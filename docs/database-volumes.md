# Docker-managed database volumes

All PostgreSQL, MySQL, and MariaDB services in `compose.apps.yaml` use named volumes, not cloud-folder bind mounts. This prevents database entrypoints from failing with `chown: /var/lib/postgresql/data: Permission denied` and `chown: /var/lib/mysql: Permission denied` when the checkout lives on a macOS-synchronized filesystem.

The **core** PostgreSQL instance already uses the named `postgres_data` volume in `compose.yaml`. The other databases now use:

- `officehub_paperless_database` for `officehub-paperless-database`
- `officehub_n8n_database` for `officehub-n8n-database`
- `officehub_docuseal_database` for `officehub-docuseal-database`
- `officehub_kimai_database` for `officehub-kimai-database`
- `officehub_authentik_database` for `officehub-authentik-database`
- `officehub_vikunja_database` for `officehub-vikunja-database`
- `officehub_twenty_database` for `officehub-twenty-database`
- `officehub_akaunting_database` for `officehub-akaunting-database`
- `officehub_invoiceninja_database` for `officehub-invoiceninja-database`
- `officehub_automatisch_database` for `officehub-automatisch-database`

Because Compose uses `name: officehub`, Docker volume names are prefixed with `officehub_`. For example, the complete Docker volume name for the Akaunting database is `officehub_officehub_akaunting_database`.

## Existing database data — read before restarting

**Switching from bind mounts to named volumes does not migrate existing database files.** Existing data in `../data/officehub-*-database` is left on the host, untouched. An empty new volume causes the respective database to initialize an empty database, which may make existing app records appear missing.

Before applying the new Compose file, **stop applications and take backups of important data**. For databases that have already initialized successfully, prefer engine-native logical backups (`pg_dump`, `mysqldump`, or `mariadb-dump`) and restore them into the new instances. If a database has only partially initialized, **do not copy its files blindly**; determine whether to recover or recreate the instance first. Copying live database directories risks corruption. Never delete existing bind-mount directories or use `docker compose down -v` until recovery is complete.

If this is the first bootstrap and the failed databases contain no valuable data, new named volumes may initialize normally:

```bash
git pull --ff-only
just docker-app-check
just start-all
```

Check the previously failing services:

```bash
docker compose -f compose.yaml -f compose.apps.yaml --profile '*' ps -a
docker compose -f compose.yaml -f compose.apps.yaml --profile '*' logs --tail=100 \
  officehub-akaunting-database officehub-authentik-database \
  officehub-docuseal-database officehub-invoiceninja-database \
  officehub-kimai-database officehub-paperless-database \
  officehub-twenty-database officehub-vikunja-database
```

Other non-database application bind mounts are unchanged. If those encounter similar permission errors, move their data to a local, non-cloud filesystem or migrate them individually to named volumes.
