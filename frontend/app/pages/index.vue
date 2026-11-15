<script setup lang="ts">
type Dashboard = {
  counts: Record<string, number>
  outstanding: string
  recent_tasks: Array<{ id: number; title: string; status: string; due_date?: string }>
  ai: { online: boolean; models: string[] }
}
const { data, status, error, refresh } = await useFetch<Dashboard>('/api/dashboard')
const apps = useOfficeApps()
const cards = [
  { key: 'clients', label: 'Clients', icon: 'i-lucide-users', to: '/clients' },
  { key: 'projects', label: 'Projects', icon: 'i-lucide-folder-kanban', to: '/projects' },
  { key: 'tasks', label: 'Tasks', icon: 'i-lucide-list-checks', to: '/tasks' },
  { key: 'invoices', label: 'Invoices', icon: 'i-lucide-receipt', to: '/invoices' }
]
</script>

<template>
  <OfficeShell>
    <template #title>Good to see you. Here's your workspace.</template>
    <div class="mb-7 flex items-center justify-between">
      <p class="text-sm text-slate-500">Clients, projects and billing in one place.</p>
      <UButton icon="i-lucide-refresh-cw" color="neutral" variant="ghost" :loading="status === 'pending'" @click="refresh()">Refresh</UButton>
    </div>
    <UAlert v-if="error" color="error" title="Could not load dashboard" :description="error.message" class="mb-5" />
    <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <NuxtLink v-for="card in cards" :key="card.key" :to="card.to" class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-indigo-300">
        <div class="flex items-center justify-between">
          <span class="text-sm font-medium text-slate-500">{{ card.label }}</span>
          <UIcon :name="card.icon" class="size-5 text-indigo-600" />
        </div>
        <div class="mt-5 text-3xl font-semibold">{{ data?.counts?.[card.key] ?? '—' }}</div>
        <p class="mt-2 text-xs text-slate-400">View {{ card.label.toLowerCase() }} →</p>
      </NuxtLink>
    </div>
    <div class="mt-6 grid gap-5 lg:grid-cols-3">
      <section class="rounded-2xl border border-slate-200 bg-white p-6 lg:col-span-2">
        <div class="mb-5 flex items-center justify-between">
          <h2 class="text-lg font-semibold">Recent tasks</h2>
          <UButton to="/tasks" variant="link" color="primary">Manage tasks</UButton>
        </div>
        <div v-if="!data?.recent_tasks?.length" class="py-9 text-center text-sm text-slate-400">No tasks yet. Add one to get started.</div>
        <div v-for="task in data?.recent_tasks" :key="task.id" class="flex items-center justify-between border-t border-slate-100 py-4">
          <span class="text-sm font-medium">{{ task.title }}</span>
          <UBadge :color="task.status === 'done' ? 'success' : 'neutral'" variant="subtle">{{ task.status }}</UBadge>
        </div>
      </section>
      <div class="space-y-5">
        <section class="rounded-2xl bg-indigo-600 p-6 text-white">
          <div class="flex items-center gap-2 text-sm text-indigo-100"><UIcon name="i-lucide-wallet" /> Outstanding invoices</div>
          <div class="mt-4 text-3xl font-semibold">{{ Number(data?.outstanding || 0).toLocaleString('de-DE', { style: 'currency', currency: 'EUR' }) }}</div>
          <p class="mt-2 text-xs text-indigo-100">Total of all unpaid invoice records</p>
        </section>
        <section class="rounded-2xl border border-slate-200 bg-white p-6">
          <div class="flex items-center justify-between">
            <h2 class="font-semibold">Local AI</h2>
            <UBadge :color="data?.ai.online ? 'success' : 'warning'">{{ data?.ai.online ? 'Online' : 'Offline' }}</UBadge>
          </div>
          <p class="mt-3 text-sm text-slate-500">{{ data?.ai.models.length ? data.ai.models.join(', ') : 'No downloaded models found yet.' }}</p>
          <p class="mt-2 text-xs text-slate-400">Ollama model initialization can take time on first run.</p>
        </section>
      </div>
    </div>
    <section class="mt-9">
      <div class="mb-5 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p class="text-xs font-semibold uppercase tracking-wider text-indigo-600">Integrated tools</p>
          <h2 class="mt-1 text-xl font-semibold">Applications</h2>
          <p class="mt-1 text-sm text-slate-500">Launch self-hosted apps or explore what each service does.</p>
        </div>
        <span class="text-xs text-slate-400">{{ apps.length }} configured apps · Availability not checked</span>
      </div>
      <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        <article v-for="app in apps" :key="app.slug" class="flex flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div class="flex items-start justify-between gap-2">
            <div class="flex size-11 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
              <UIcon :name="app.icon" class="size-6" />
            </div>
            <span class="rounded-full bg-slate-100 px-2 py-1 text-[11px] font-medium text-slate-500">{{ app.category }}</span>
          </div>
          <h3 class="mt-4 text-base font-semibold">{{ app.name }}</h3>
          <p class="mt-1 flex-1 text-sm leading-relaxed text-slate-500">{{ app.summary }}</p>
          <p class="mt-3 text-xs text-slate-400">Profile: {{ app.profile }}</p>
          <p v-if="app.url" class="mt-1 truncate text-xs text-slate-400" :title="app.url">{{ app.url }}</p>
          <p v-else class="mt-1 text-xs text-amber-600">Internal API · No browser UI</p>
          <div class="mt-5 flex flex-wrap items-center gap-3 border-t border-slate-100 pt-4">
            <NuxtLink :to="`/apps/${app.slug}`" class="text-sm font-semibold text-indigo-600 hover:underline">Overview</NuxtLink>
            <a v-if="app.url" :href="app.url" target="_blank" rel="noopener noreferrer"
              class="ml-auto inline-flex items-center gap-1 text-sm font-medium text-slate-700 hover:text-indigo-600">
              Open app <UIcon name="i-lucide-external-link" class="size-4" />
            </a>
          </div>
        </article>
      </div>
    </section>
  </OfficeShell>
</template>
