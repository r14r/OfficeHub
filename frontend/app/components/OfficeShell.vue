<script setup lang="ts">
const route = useRoute()
const apps = useOfficeApps()
const nav = [
  { label: 'Dashboard', to: '/', icon: 'i-lucide-layout-dashboard' },
  { label: 'Clients', to: '/clients', icon: 'i-lucide-users' },
  { label: 'Projects', to: '/projects', icon: 'i-lucide-folder-kanban' },
  { label: 'Tasks', to: '/tasks', icon: 'i-lucide-list-checks' },
  { label: 'Invoices', to: '/invoices', icon: 'i-lucide-receipt' }
]
const activeSlug = computed(() => String(route.params.slug ?? ''))
const aiChat = computed(() => apps.find(app => app.slug === 'openwebui')?.url ?? '')
</script>

<template>
  <div class="min-h-screen text-slate-900">
    <div class="mx-auto flex min-h-screen max-w-[1600px]">
      <aside class="sticky top-0 hidden h-screen w-72 shrink-0 overflow-y-auto border-r border-slate-200 bg-white p-5 md:block">
        <NuxtLink to="/" class="flex items-center gap-3 text-xl font-bold tracking-tight">
          <span class="flex size-10 items-center justify-center rounded-xl bg-indigo-600 text-white">OH</span>
          OfficeHub
        </NuxtLink>
        <p class="mt-2 text-xs text-slate-500">Your freelance command center</p>
        <nav aria-label="Workspace navigation" class="mt-8 space-y-1">
          <NuxtLink v-for="item in nav" :key="item.to" :to="item.to"
            class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-600 hover:bg-indigo-50 hover:text-indigo-700"
            active-class="bg-indigo-50 !text-indigo-700">
            <UIcon :name="item.icon" class="size-5" />
            {{ item.label }}
          </NuxtLink>
        </nav>
        <div class="mt-7 border-t border-slate-200 pt-5">
          <div class="mb-3 flex items-center justify-between px-3">
            <h2 class="text-xs font-semibold uppercase tracking-wider text-slate-400">Applications</h2>
            <span class="text-xs text-slate-400">{{ apps.length }}</span>
          </div>
          <nav aria-label="Application navigation" class="space-y-1">
            <details v-for="app in apps" :key="app.slug" :open="activeSlug === app.slug ? true : undefined"
              class="group rounded-lg text-sm">
              <summary class="flex cursor-pointer list-none items-center gap-2 rounded-lg px-3 py-2 text-slate-600 hover:bg-slate-50 [&::-webkit-details-marker]:hidden">
                <UIcon :name="app.icon" class="size-4 shrink-0 text-indigo-500" />
                <span class="min-w-0 flex-1 truncate font-medium">{{ app.name }}</span>
                <UIcon name="i-lucide-chevron-down" class="size-4 transition-transform group-open:rotate-180" />
              </summary>
              <div class="ml-5 border-l border-slate-200 pb-2 pl-4">
                <NuxtLink :to="`/apps/${app.slug}`" class="mt-1 block rounded-md px-2 py-1.5 text-xs text-slate-500 hover:bg-indigo-50 hover:text-indigo-700"
                  active-class="bg-indigo-50 !text-indigo-700">Overview</NuxtLink>
                <a v-if="app.url" :href="app.url" target="_blank" rel="noopener noreferrer"
                  class="block rounded-md px-2 py-1.5 text-xs text-slate-500 hover:text-indigo-700">Open app ↗</a>
                <span v-else class="block px-2 py-1 text-xs text-slate-400">Internal API only</span>
              </div>
            </details>
          </nav>
        </div>
      </aside>
      <main class="min-w-0 flex-1 px-5 py-6 md:px-9 md:py-9">
        <header class="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p class="text-xs font-semibold uppercase tracking-widest text-indigo-600">Workspace / OfficeHub</p>
            <h1 class="mt-1 text-2xl font-semibold"><slot name="title">Dashboard</slot></h1>
          </div>
          <a v-if="aiChat" :href="aiChat" target="_blank" rel="noopener noreferrer"
            class="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700">
            <UIcon name="i-lucide-sparkles" class="size-4" /> Open AI chat
          </a>
        </header>
        <div class="mb-6 md:hidden">
          <nav aria-label="Mobile workspace navigation" class="flex gap-2 overflow-x-auto pb-2">
            <UButton v-for="item in nav" :key="item.to" :to="item.to" color="neutral" variant="outline" size="sm">{{ item.label }}</UButton>
          </nav>
          <details class="mt-2 rounded-xl border border-slate-200 bg-white p-3">
            <summary class="cursor-pointer text-sm font-medium">Applications ({{ apps.length }})</summary>
            <div class="mt-3 grid grid-cols-2 gap-2">
              <NuxtLink v-for="app in apps" :key="app.slug" :to="`/apps/${app.slug}`"
                class="rounded-lg bg-slate-50 px-3 py-2 text-xs text-slate-700 hover:text-indigo-700">
                {{ app.name }} · Overview
              </NuxtLink>
            </div>
          </details>
        </div>
        <slot />
      </main>
    </div>
  </div>
</template>
