<script setup lang="ts">
const route = useRoute()
const section = computed(() => String(route.params.section))
const definitions: Record<string, { title: string; fields: { name: string; label: string; type?: string; required?: boolean }[] }> = {
  clients: { title: 'Clients', fields: [{ name: 'name', label: 'Name', required: true }, { name: 'company', label: 'Company' }, { name: 'email', label: 'Email', type: 'email' }] },
  projects: { title: 'Projects', fields: [{ name: 'name', label: 'Project name', required: true }, { name: 'client_id', label: 'Client ID (optional)', type: 'number' }, { name: 'status', label: 'Status (active / paused / done)' }] },
  tasks: { title: 'Tasks', fields: [{ name: 'title', label: 'Task title', required: true }, { name: 'project_id', label: 'Project ID (optional)', type: 'number' }, { name: 'status', label: 'Status (todo / doing / done)' }, { name: 'due_date', label: 'Due date', type: 'date' }] },
  invoices: { title: 'Invoices', fields: [{ name: 'number', label: 'Invoice number', required: true }, { name: 'client_id', label: 'Client ID', type: 'number', required: true }, { name: 'amount', label: 'Amount (EUR)', type: 'number', required: true }, { name: 'status', label: 'Status (draft / sent / paid)' }] }
}
const definition = computed(() => definitions[section.value])
if (!definition.value) throw createError({ statusCode: 404, statusMessage: 'Section not found' })
const { data, refresh, error } = await useFetch<Record<string, any>[]>(() => `/api/${section.value}`, { default: () => [] })
const form = reactive<Record<string, string>>({})
const busy = ref(false)
const message = ref('')
const failures = ref('')
async function addRecord() {
  busy.value = true
  failures.value = ''
  message.value = ''
  try {
    const body: Record<string, string | number> = {}
    for (const field of definition.value.fields) {
      const value = form[field.name]?.trim()
      if (!value) continue
      body[field.name] = field.type === 'number' ? Number(value) : value
    }
    await $fetch(`/api/${section.value}`, { method: 'POST', body })
    for (const key of Object.keys(form)) delete form[key]
    message.value = 'Record created'
    await refresh()
  } catch (e: any) {
    failures.value = e?.data?.detail ? JSON.stringify(e.data.detail) : 'Could not save record'
  } finally {
    busy.value = false
  }
}
async function removeRecord(id: number) {
  if (!confirm('Delete this record?')) return
  failures.value = ''
  try {
    await $fetch(`/api/${section.value}/${id}`, { method: 'DELETE' })
    await refresh()
  } catch (e: any) {
    failures.value = e?.data?.detail || 'Could not delete record'
  }
}
const columns = computed(() => definition.value.fields.map(f => f.name))
</script>

<template>
  <OfficeShell>
    <template #title>{{ definition.title }}</template>
    <div class="grid gap-6 xl:grid-cols-[1fr_320px]">
      <section class="min-w-0 rounded-2xl border border-slate-200 bg-white p-5">
        <h2 class="mb-5 font-semibold">All {{ definition.title.toLowerCase() }}</h2>
        <UAlert v-if="error" color="error" title="Failed to load records" :description="error.message" class="mb-4" />
        <div class="overflow-x-auto">
          <table class="w-full text-left text-sm">
            <thead class="border-b border-slate-200 text-slate-500"><tr>
              <th class="px-3 py-3">ID</th>
              <th v-for="col in columns" :key="col" class="px-3 py-3">{{ col.replaceAll('_', ' ') }}</th>
              <th class="px-3 py-3">Action</th>
            </tr></thead>
            <tbody>
              <tr v-for="item in data" :key="item.id" class="border-b border-slate-100">
                <td class="px-3 py-3 text-slate-400">{{ item.id }}</td>
                <td v-for="col in columns" :key="col" class="px-3 py-3">{{ item[col] ?? '—' }}</td>
                <td class="px-3 py-3"><UButton size="xs" icon="i-lucide-trash-2" color="error" variant="ghost" aria-label="Delete record" @click="removeRecord(item.id)" /></td>
              </tr>
              <tr v-if="!data?.length"><td :colspan="columns.length + 2" class="px-3 py-10 text-center text-slate-400">No records yet</td></tr>
            </tbody>
          </table>
        </div>
      </section>
      <section class="h-fit rounded-2xl border border-slate-200 bg-white p-5">
        <h2 class="mb-5 font-semibold">Add {{ definition.title.slice(0, -1).toLowerCase() }}</h2>
        <form class="space-y-4" @submit.prevent="addRecord">
          <div v-for="field in definition.fields" :key="field.name">
            <label :for="field.name" class="mb-1 block text-sm font-medium text-slate-700">{{ field.label }}</label>
            <UInput :id="field.name" v-model="form[field.name]" :type="field.type || 'text'" :required="field.required" class="w-full" />
          </div>
          <UAlert v-if="failures" color="error" :description="failures" />
          <UAlert v-if="message" color="success" :description="message" />
          <UButton type="submit" block :loading="busy" icon="i-lucide-plus">Create</UButton>
        </form>
      </section>
    </div>
  </OfficeShell>
</template>
