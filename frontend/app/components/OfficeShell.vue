<script setup lang="ts">
const nav = [
  { label: 'Overview', to: '/', icon: 'i-lucide-layout-dashboard' },
  { label: 'Clients', to: '/clients', icon: 'i-lucide-users' },
  { label: 'Projects', to: '/projects', icon: 'i-lucide-folder-kanban' },
  { label: 'Tasks', to: '/tasks', icon: 'i-lucide-list-checks' },
  { label: 'Invoices', to: '/invoices', icon: 'i-lucide-receipt' }
]
</script>

<template>
  <div class="min-h-screen text-slate-900">
    <div class="mx-auto flex min-h-screen max-w-7xl">
      <aside class="hidden w-64 shrink-0 border-r border-slate-200 bg-white p-6 md:block">
        <NuxtLink to="/" class="flex items-center gap-3 text-xl font-bold tracking-tight">
          <span class="flex size-10 items-center justify-center rounded-xl bg-indigo-600 text-white">OH</span>
          OfficeHub
        </NuxtLink>
        <p class="mt-2 text-xs text-slate-500">Your freelance command center</p>
        <nav class="mt-10 space-y-1">
          <NuxtLink v-for="item in nav" :key="item.to" :to="item.to"
            class="flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium text-slate-600 hover:bg-indigo-50 hover:text-indigo-700"
            active-class="bg-indigo-50 !text-indigo-700">
            <UIcon :name="item.icon" class="size-5" />
            {{ item.label }}
          </NuxtLink>
        </nav>
        <div class="mt-12 rounded-xl bg-slate-50 p-4 text-xs text-slate-500">
          <div class="font-semibold text-slate-800">Local-first</div>
          Your records stay in your PostgreSQL volume.
        </div>
      </aside>
      <main class="min-w-0 flex-1 px-5 py-6 md:px-10 md:py-9">
        <header class="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p class="text-xs font-semibold uppercase tracking-widest text-indigo-600">Workspace / OfficeHub</p>
            <h1 class="mt-1 text-2xl font-semibold"><slot name="title">Dashboard</slot></h1>
          </div>
          <a href="http://localhost:3001" target="_blank" rel="noopener noreferrer">
            <UButton icon="i-lucide-sparkles" color="primary">Open AI chat</UButton>
          </a>
        </header>
        <div class="mb-6 flex gap-2 overflow-x-auto md:hidden">
          <UButton v-for="item in nav" :key="item.to" :to="item.to" color="neutral" variant="outline" size="sm">{{ item.label }}</UButton>
        </div>
        <slot />
      </main>
    </div>
  </div>
</template>
