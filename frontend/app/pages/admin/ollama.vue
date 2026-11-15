<script setup lang="ts">
const { data, status, error, refresh } = await useFetch<{
  ai: { online: boolean; models: string[] }
}>('/api/dashboard')
const ollamaUrl = 'http://ollama:11434'
</script>

<template>
  <OfficeShell>
    <template #title>Admin · Ollama</template>
    <div class="max-w-4xl space-y-6">
      <section class="rounded-2xl border border-slate-200 bg-white p-6">
        <div class="flex items-center justify-between gap-3">
          <div class="flex items-center gap-3">
            <UIcon name="i-lucide-brain-circuit" class="size-8 text-indigo-600" />
            <div>
              <h2 class="text-lg font-semibold">Shared Ollama server</h2>
              <p class="mt-1 text-sm text-slate-500">One model store and one inference server for the entire OfficeHub stack.</p>
            </div>
          </div>
          <UBadge :color="data?.ai.online ? 'success' : 'warning'">{{ data?.ai.online ? 'Online' : 'Offline' }}</UBadge>
        </div>
        <UAlert v-if="error" color="error" class="mt-5" title="Cannot retrieve Ollama status" :description="error.message" />
        <div class="mt-6 flex flex-wrap items-center gap-3">
          <UButton icon="i-lucide-refresh-cw" variant="outline" color="neutral" :loading="status === 'pending'" @click="refresh()">Refresh status</UButton>
          <UButton to="/apps/openwebui" color="primary" variant="subtle">Open WebUI overview</UButton>
        </div>
      </section>
      <section class="rounded-2xl border border-slate-200 bg-white p-6">
        <h2 class="font-semibold">Installed models</h2>
        <p v-if="!data?.ai.models.length" class="mt-4 text-sm text-slate-500">No models reported. Run the model initialization jobs to download their configured models.</p>
        <ul v-else class="mt-4 space-y-2">
          <li v-for="model in data.ai.models" :key="model" class="flex items-center gap-2 rounded-lg bg-slate-50 p-3 font-mono text-sm">
            <UIcon name="i-lucide-box" class="size-4 text-indigo-600" /> {{ model }}
          </li>
        </ul>
      </section>
      <section class="rounded-2xl border border-slate-200 bg-white p-6">
        <h2 class="font-semibold">Connection & model initialization</h2>
        <dl class="mt-4 space-y-3 text-sm">
          <div><dt class="text-slate-500">Docker endpoint</dt><dd class="font-mono">{{ ollamaUrl }}</dd></div>
          <div><dt class="text-slate-500">Model storage</dt><dd class="font-mono">ollama_data</dd></div>
          <div><dt class="text-slate-500">Init jobs</dt><dd class="font-mono">officehub-openwebui-ollama-init<br />officehub-n8n-ollama-init</dd></div>
        </dl>
        <pre class="mt-5 overflow-x-auto rounded-xl bg-slate-900 p-4 text-xs text-slate-50">just docker-model-pull
just docker-models
just docker-app-up automation</pre>
        <p class="mt-4 text-sm text-slate-500">Initialization jobs download models into the shared Ollama instance. Not all OfficeHub applications require an LLM.</p>
      </section>
    </div>
  </OfficeShell>
</template>
