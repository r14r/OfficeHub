<script setup lang="ts">
const route = useRoute()
const apps = useOfficeApps()
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
        <nav aria-label="Workspace navigation" class="mt-8 space-y-2">
          <NuxtLink to="/" class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold text-slate-600 hover:bg-indigo-50 hover:text-indigo-700"
            active-class="bg-indigo-50 !text-indigo-700">
            <UIcon name="i-lucide-layout-dashboard" class="size-5" /> Dashboard
          </NuxtLink>
          <details class="group rounded-lg" :open="route.path.startsWith('/admin') ? true : undefined">
            <summary class="flex cursor-pointer list-none items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 [&::-webkit-details-marker]:hidden">
              <UIcon name="i-lucide-settings-2" class="size-5" />
              <span class="flex-1">Admin</span>
              <UIcon name="i-lucide-chevron-down" class="size-4 transition-transform group-open:rotate-180" />
            </summary>
            <div class="ml-6 border-l border-slate-200 pl-3">
              <NuxtLink to="/admin/ollama" class="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-slate-600 hover:bg-indigo-50 hover:text-indigo-700"
                active-class="bg-indigo-50 !text-indigo-700"><UIcon name="i-lucide-brain-circuit" class="size-4" /> Ollama</NuxtLink>
            </div>
          </details>
          <details class="group rounded-lg" :open="route.path.startsWith('/apps') ? true : undefined">
            <summary class="flex cursor-pointer list-none items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 [&::-webkit-details-marker]:hidden">
              <UIcon name="i-lucide-layout-grid" class="size-5" />
              <span class="flex-1">Apps</span>
              <span class="text-xs text-slate-400">{{ apps.length }}</span>
              <UIcon name="i-lucide-chevron-down" class="size-4 transition-transform group-open:rotate-180" />
            </summary>
            <nav aria-label="Application navigation" class="ml-6 space-y-1 border-l border-slate-200 pl-3">
              <NuxtLink v-for="app in apps" :key="app.slug" :to="`/apps/${app.slug}`"
                class="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-slate-600 hover:bg-indigo-50 hover:text-indigo-700"
                active-class="bg-indigo-50 !text-indigo-700">
                <UIcon :name="app.icon" class="size-4 shrink-0" />
                <span class="truncate">{{ app.name }}</span>
              </NuxtLink>
            </nav>
          </details>
        </nav>
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
        <nav aria-label="Mobile workspace navigation" class="mb-6 flex flex-wrap items-center gap-2 md:hidden">
          <UButton to="/" color="neutral" variant="outline" size="sm">Dashboard</UButton>
          <UButton to="/admin/ollama" color="neutral" variant="outline" size="sm">Admin · Ollama</UButton>
          <details class="w-full rounded-lg border border-slate-200 bg-white p-3">
            <summary class="cursor-pointer text-sm font-semibold">Apps ({{ apps.length }})</summary>
            <div class="mt-3 grid grid-cols-2 gap-2">
              <NuxtLink v-for="app in apps" :key="app.slug" :to="`/apps/${app.slug}`"
                class="rounded-lg bg-slate-50 px-3 py-2 text-xs text-slate-700 hover:text-indigo-700">{{ app.name }}</NuxtLink>
            </div>
          </details>
        </nav>
        <slot />
      </main>
    </div>
  </div>
</template>
