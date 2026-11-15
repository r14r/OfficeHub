// A single catalog powers the dashboard, sidebar and per-app overview routes.
// Browser URLs are injected by the Nuxt public runtime configuration.
export type OfficeApp = {
  slug: string
  name: string
  category: string
  profile: string
  icon: string
  summary: string
  description: string
  dependencies: string
  repository: string
  capabilities: string[]
  url: string | null
  internalUrl?: string
}
type AppDefinition = Omit<OfficeApp, 'url'> & { urlKey: string | null }
const definitions: AppDefinition[] = [
  {
    "slug": "openwebui",
    "name": "Open WebUI",
    "category": "AI & knowledge",
    "profile": "core",
    "icon": "i-lucide-bot",
    "summary": "Chat with locally hosted Ollama models.",
    "description": "A self-hosted chat interface for local LLM conversations and model management.",
    "dependencies": "Ollama",
    "repository": "https://github.com/open-webui/open-webui",
    "urlKey": "openWebuiUrl",
    "capabilities": [
      "Local AI chat",
      "Model selection",
      "Conversation history"
    ]
  },
  {
    "slug": "paperless",
    "name": "Paperless-ngx",
    "category": "Documents",
    "profile": "documents",
    "icon": "i-lucide-files",
    "summary": "Scan, organize and search documents.",
    "description": "OCR-powered document storage for contracts, receipts and client files.",
    "dependencies": "PostgreSQL, Valkey, Tika, Gotenberg",
    "repository": "https://github.com/paperless-ngx/paperless-ngx",
    "urlKey": "paperlessUrl",
    "capabilities": [
      "OCR",
      "Document archive",
      "Search and tagging"
    ]
  },
  {
    "slug": "gotenberg",
    "name": "Gotenberg",
    "category": "Documents",
    "profile": "documents",
    "icon": "i-lucide-file-output",
    "summary": "Convert HTML and office files to PDF.",
    "description": "A headless PDF conversion API used by Paperless; no browser user interface.",
    "dependencies": "Standalone API",
    "repository": "https://github.com/gotenberg/gotenberg",
    "urlKey": null,
    "capabilities": [
      "HTML to PDF",
      "Office conversion",
      "API access"
    ],
    "internalUrl": "http://officehub-gotenberg-api:3000"
  },
  {
    "slug": "n8n",
    "name": "n8n",
    "category": "Automation",
    "profile": "automation",
    "icon": "i-lucide-workflow",
    "summary": "Automate repeated business processes.",
    "description": "Design workflows connecting events, webhooks, office services and external APIs.",
    "dependencies": "PostgreSQL",
    "repository": "https://github.com/n8n-io/n8n",
    "urlKey": "n8nUrl",
    "capabilities": [
      "Visual workflows",
      "Webhooks",
      "Integrations"
    ]
  },
  {
    "slug": "docuseal",
    "name": "DocuSeal",
    "category": "Documents",
    "profile": "signing",
    "icon": "i-lucide-pen-line",
    "summary": "Prepare and request electronic signatures.",
    "description": "Sign contracts and approvals using templates and track document completion.",
    "dependencies": "PostgreSQL",
    "repository": "https://github.com/docusealco/docuseal",
    "urlKey": "docusealUrl",
    "capabilities": [
      "Signing templates",
      "Signature requests",
      "Document approvals"
    ]
  },
  {
    "slug": "kimai",
    "name": "Kimai",
    "category": "Business",
    "profile": "time",
    "icon": "i-lucide-clock-3",
    "summary": "Track client time and billable work.",
    "description": "Create time entries, billable activities and project-based reports.",
    "dependencies": "MySQL",
    "repository": "https://github.com/kimai/kimai",
    "urlKey": "kimaiUrl",
    "capabilities": [
      "Timesheets",
      "Rates",
      "Time reporting"
    ]
  },
  {
    "slug": "authentik",
    "name": "Authentik",
    "category": "Security",
    "profile": "security",
    "icon": "i-lucide-shield-check",
    "summary": "Identity management and single sign-on.",
    "description": "Independent identity provider for SSO and access management. OfficeHub login is not connected yet.",
    "dependencies": "PostgreSQL, worker",
    "repository": "https://github.com/goauthentik/authentik",
    "urlKey": "authentikUrl",
    "capabilities": [
      "OIDC / SSO",
      "User directory",
      "Access policies"
    ]
  },
  {
    "slug": "stirlingpdf",
    "name": "Stirling PDF",
    "category": "Documents",
    "profile": "pdf",
    "icon": "i-lucide-file-text",
    "summary": "Merge, split and convert PDF documents.",
    "description": "Web toolbox for everyday PDF transformation tasks.",
    "dependencies": "Standalone",
    "repository": "https://github.com/Stirling-Tools/Stirling-PDF",
    "urlKey": "stirlingUrl",
    "capabilities": [
      "PDF merge",
      "Split",
      "Convert"
    ]
  },
  {
    "slug": "vikunja",
    "name": "Vikunja",
    "category": "Productivity",
    "profile": "tasks",
    "icon": "i-lucide-list-todo",
    "summary": "Plan tasks and projects.",
    "description": "Dedicated task manager with planning views, independent of OfficeHub tasks.",
    "dependencies": "PostgreSQL",
    "repository": "https://github.com/go-vikunja/vikunja",
    "urlKey": "vikunjaUrl",
    "capabilities": [
      "Task lists",
      "Planning",
      "Project organization"
    ]
  },
  {
    "slug": "twenty",
    "name": "Twenty CRM",
    "category": "Business",
    "profile": "crm",
    "icon": "i-lucide-contact-round",
    "summary": "Manage customer relationships and leads.",
    "description": "CRM for contacts, companies and opportunities; separate from OfficeHub clients.",
    "dependencies": "PostgreSQL, Redis, worker",
    "repository": "https://github.com/twentyhq/twenty",
    "urlKey": "twentyUrl",
    "capabilities": [
      "Contacts",
      "Sales opportunities",
      "CRM workflows"
    ]
  },
  {
    "slug": "actualbudget",
    "name": "Actual Budget",
    "category": "Finance",
    "profile": "budget",
    "icon": "i-lucide-wallet",
    "summary": "Manage budgets and spending.",
    "description": "Local-first budgeting to monitor income, expenses and financial plans.",
    "dependencies": "Standalone",
    "repository": "https://github.com/actualbudget/actual",
    "urlKey": "actualUrl",
    "capabilities": [
      "Budget planning",
      "Expenses",
      "Reports"
    ]
  },
  {
    "slug": "qdrant",
    "name": "Qdrant",
    "category": "AI & knowledge",
    "profile": "vector",
    "icon": "i-lucide-database-zap",
    "summary": "Store embeddings for semantic search.",
    "description": "Private vector-search database; no browser port is published in OfficeHub.",
    "dependencies": "Standalone API",
    "repository": "https://github.com/qdrant/qdrant",
    "urlKey": null,
    "capabilities": [
      "Vector storage",
      "Semantic search",
      "RAG infrastructure"
    ],
    "internalUrl": "http://officehub-qdrant-database:6333"
  },
  {
    "slug": "akaunting",
    "name": "Akaunting",
    "category": "Finance",
    "profile": "accounting",
    "icon": "i-lucide-calculator",
    "summary": "Track accounting and expenses.",
    "description": "Bookkeeping app for managing income and expenses. Requires first-run configuration.",
    "dependencies": "MariaDB",
    "repository": "https://github.com/akaunting/akaunting",
    "urlKey": "akauntingUrl",
    "capabilities": [
      "Bookkeeping",
      "Expense tracking",
      "Income reports"
    ]
  },
  {
    "slug": "invoiceninja",
    "name": "Invoice Ninja",
    "category": "Finance",
    "profile": "invoicing",
    "icon": "i-lucide-receipt-text",
    "summary": "Create quotes and invoices.",
    "description": "Dedicated invoicing and billing app. Its upstream installation may require a proxy and extra setup.",
    "dependencies": "MariaDB, optional web proxy",
    "repository": "https://github.com/invoiceninja/invoiceninja",
    "urlKey": "invoiceNinjaUrl",
    "capabilities": [
      "Estimates",
      "Invoices",
      "Payments"
    ]
  },
  {
    "slug": "automatisch",
    "name": "Automatisch",
    "category": "Automation",
    "profile": "automation-alt",
    "icon": "i-lucide-git-branch",
    "summary": "Alternative workflow automation.",
    "description": "Self-hosted integrations and event-triggered workflows as an alternative to n8n.",
    "dependencies": "PostgreSQL, Redis, worker",
    "repository": "https://github.com/automatisch/automatisch",
    "urlKey": "automatischUrl",
    "capabilities": [
      "Workflow triggers",
      "Connected actions",
      "Automation"
    ]
  }
]

export function useOfficeApps(): OfficeApp[] {
  const config = useRuntimeConfig()
  const publicConfig = config.public as Record<string, unknown>
  return definitions.map(({ urlKey, ...app }) => ({
    ...app,
    url: urlKey && typeof publicConfig[urlKey] === 'string'
      ? publicConfig[urlKey] as string
      : null
  }))
}
