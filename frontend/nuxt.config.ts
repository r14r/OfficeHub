export default defineNuxtConfig({
  compatibilityDate: '2026-07-01',
  modules: ['@nuxt/ui'],
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    apiInternalUrl: process.env.NUXT_API_INTERNAL_URL || 'http://localhost:8000',
    public: {
      openWebuiUrl: 'http://localhost:3001',
      paperlessUrl: 'http://localhost:8010',
      n8nUrl: 'http://localhost:5678',
      docusealUrl: 'http://localhost:3002',
      kimaiUrl: 'http://localhost:8001',
      authentikUrl: 'http://localhost:9000',
      stirlingUrl: 'http://localhost:8088',
      vikunjaUrl: 'http://localhost:3456',
      twentyUrl: 'http://localhost:3020',
      actualUrl: 'http://localhost:5006',
      akauntingUrl: 'http://localhost:8040',
      invoiceNinjaUrl: 'http://localhost:8050',
      automatischUrl: 'http://localhost:3060'
    }
  },
  app: {
    head: {
      title: 'OfficeHub | Freelancer workspace',
      meta: [{ name: 'description', content: 'Local-first freelance office dashboard' }]
    }
  }
})
