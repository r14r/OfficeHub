<script setup lang="ts">
type Dashboard = {
  counts: Record<string, number>
  outstanding: string
  recent_tasks: Array<{ id: number; title: string; status: string; due_date?: string }>
  ai: { online: boolean; models: string[] }
}
const { data, status, error, refresh } = await useFetch<Dashboard>('/api/dashboard')
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
  </OfficeShell>
</template>
