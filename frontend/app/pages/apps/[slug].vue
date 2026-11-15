<script setup lang="ts">
const route = useRoute()
const apps = useOfficeApps()
const app = computed(() => apps.find(item => item.slug === route.params.slug))
if (!app.value) throw createError({ statusCode: 404, statusMessage: 'Application not found' })
useHead({ title: `${app.value.name} | OfficeHub` })
</script>

<template>
  <OfficeShell v-if="app">
    <template #title>{{ app.name }} · Overview</template>
    <NuxtLink to="/" class="mb-6 inline-flex items-center gap-2 text-sm font-medium text-indigo-600 hover:underline">
      <UIcon name="i-lucide-arrow-left" /> Back to dashboard
    </NuxtLink>
    <div class="max-w-4xl space-y-6">
      <section class="rounded-2xl border border-slate-200 bg-white p-7 shadow-sm">
        <div class="flex items-start gap-4">
          <span class="flex size-14 shrink-0 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600">
            <UIcon :name="app.icon" class="size-8" />
          </span>
          <div>
            <div class="text-xs font-semibold uppercase tracking-wider text-indigo-600">{{ app.category }}</div>
            <h2 class="mt-1 text-2xl font-semibold">{{ app.name }}</h2>
            <p class="mt-3 text-sm leading-7 text-slate-600">{{ app.description }}</p>
          </div>
        </div>
        <div class="mt-7 flex flex-wrap gap-3">
          <a v-if="app.url" :href="app.url" target="_blank" rel="noopener noreferrer"
            class="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700">
            <UIcon name="i-lucide-external-link"/> Open {{ app.name }}
          </a>
          <a :href="app.repository" target="_blank" rel="noopener noreferrer"
            class="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50">
            <UIcon name="i-lucide-github" /> GitHub repository
          </a>
        </div>
        <p v-if="!app.url" class="mt-4 text-sm text-amber-700">This service is only accessible within the Docker network. No browser launch URL is exposed.</p>
      </section>
      <div class="grid gap-5 md:grid-cols-2">
        <section class="rounded-2xl border border-slate-200 bg-white p-6">
          <h3 class="font-semibold">What it provides</h3>
          <ul class="mt-4 space-y-3">
            <li v-for="feature in app.capabilities" :key="feature" class="flex items-center gap-2 text-sm text-slate-600">
              <UIcon name="i-lucide-check-circle-2" class="size-4 text-indigo-600" /> {{ feature }}
            </li>
          </ul>
        </section>
        <section class="rounded-2xl border border-slate-200 bg-white p-6">
          <h3 class="font-semibold">Deployment information</h3>
          <dl class="mt-4 space-y-4 text-sm">
            <div><dt class="text-xs text-slate-400">Compose profile</dt><dd class="mt-1 font-mono">{{ app.profile }}</dd></div>
            <div><dt class="text-xs text-slate-400">Required components</dt><dd class="mt-1 text-slate-700">{{ app.dependencies }}</dd></div>
            <div><dt class="text-xs text-slate-400">{{ app.url ? 'Browser URL' : 'Docker network endpoint' }}</dt>
              <dd class="mt-1 break-all font-mono text-xs">{{ app.url || app.internalUrl || 'Not available' }}</dd></div>
          </dl>
        </section>
      </div>
      <p class="text-xs text-slate-400">Links reflect configured addresses, not live health checks. Optional application profiles must be started separately.</p>
    </div>
  </OfficeShell>
</template>
