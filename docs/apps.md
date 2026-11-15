## Optional self-hosted applications

`compose.apps.yaml` includes separately profiled services and dedicated dependencies. **None are started by default.** Source repositories: [Paperless-ngx](https://github.com/paperless-ngx/paperless-ngx), [Gotenberg](https://github.com/gotenberg/gotenberg), [n8n](https://github.com/n8n-io/n8n), [DocuSeal](https://github.com/docusealco/docuseal), [Kimai](https://github.com/kimai/kimai), [Authentik](https://github.com/goauthentik/authentik), [Stirling PDF](https://github.com/Stirling-Tools/Stirling-PDF), [Vikunja](https://github.com/go-vikunja/vikunja), [Twenty](https://github.com/twentyhq/twenty), [Actual Budget](https://github.com/actualbudget/actual), [Qdrant](https://github.com/qdrant/qdrant), [Akaunting](https://github.com/akaunting/akaunting), [Invoice Ninja](https://github.com/invoiceninja/invoiceninja), and [Automatisch](https://github.com/automatisch/automatisch).

```bash
just init
just apps-init
just docker-app-up documents    # Paperless, Gotenberg, Tika, PostgreSQL, Valkey
just docker-app-up automation   # n8n, PostgreSQL
just docker-app-up signing      # DocuSeal, PostgreSQL
just docker-app-up time         # Kimai, MySQL
just docker-app-up security     # Authentik, PostgreSQL, worker
just docker-app-up pdf          # Stirling PDF
just docker-app-up tasks        # Vikunja, PostgreSQL
just docker-app-up crm          # Twenty, PostgreSQL, Redis, worker
just docker-app-up budget       # Actual Budget
just docker-app-up vector       # Qdrant (internal only)
just docker-app-up accounting   # Akaunting, MariaDB (setup required)
just docker-app-up invoicing    # Invoice Ninja, MariaDB (upstream proxy may be required)
just docker-app-up automation-alt # Automatisch, PostgreSQL, Redis, worker
just docker-app-logs documents
just docker-app-down documents
```

| Profile | Browser URL (localhost only) |
| --- | --- |
| documents | http://localhost:8010 |
| automation | http://localhost:5678 |
| signing | http://localhost:3002 |
| time | http://localhost:8001 |
| security | http://localhost:9000 |
| pdf | http://localhost:8088 |
| tasks | http://localhost:3456 |
| crm | http://localhost:3020 |
| budget | http://localhost:5006 |
| accounting | http://localhost:8040 |
| invoicing | http://localhost:8050 |
| automation-alt | http://localhost:3060 |

**Data:** Each optional app service has its own bind mount(s) under `../data/officehub-<repo>-<component>/`, relative to the repository checkout. The Gotenberg and Tika converters are stateless and do not need a writable host directory. Ensure the host filesystem is backed up and writable by each image's internal UID. In particular, n8n and Vikunja may require ownership by UID 1000. **Do not share database directories among services.**

**Operational cautions:** These are upstream-image integration templates, not a tested or production-certified deployment. Complete each app's first-run setup and admin password setup before using it. Akaunting and Invoice Ninja have image-specific installation steps, and Invoice Ninja's recommended architecture includes a web server/proxy that may need further configuration. Authentik is included but is **not yet wired into OfficeHub login**. The frontend currently has no authentication. Keep every published port bound to loopback; do not expose services to the Internet without TLS, SSO, reverse proxy, and backups. Image tags marked `latest` should be pinned before production. The included apps are separate UIs, not yet synchronized with the OfficeHub business data.

**Excluded pending upstream-vendor packaging:** Dify has a large generated Compose topology with many security-critical dependencies; deploying a simplified subset would be unsafe. Deploy using [Dify's supported Compose stack](https://github.com/langgenius/dify/tree/main/docker) in its own checkout and configure its data volumes there. Restic is a backup CLI rather than an always-on web service; use it for encrypted off-host backups after implementing backup retention and restore tests. Do not treat a local bind mount as a backup.
