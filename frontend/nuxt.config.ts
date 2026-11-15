export default defineNuxtConfig({
  compatibilityDate: '2026-07-01',
  modules: ['@nuxt/ui'],
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    apiInternalUrl: process.env.NUXT_API_INTERNAL_URL || 'http://localhost:8000'
  },
  app: {
    head: {
      title: 'OfficeHub | Freelancer workspace',
      meta: [{ name: 'description', content: 'Local-first freelance office dashboard' }]
    }
  }
})
