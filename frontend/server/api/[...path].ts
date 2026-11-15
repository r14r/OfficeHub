import { proxyRequest } from 'h3'

export default defineEventHandler((event) => {
  const config = useRuntimeConfig(event)
  // Only routes under /api are proxied; backend is never exposed directly.
  return proxyRequest(event, `${config.apiInternalUrl}${event.path}`)
})
