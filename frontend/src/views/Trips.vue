<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../api'
import { dirLabel } from '../directions'
const trips = ref<any[]>([])
const events = ref<any[]>([])
const savingId = ref<number | null>(null)

async function loadEvents() {
  try {
    events.value = (await api('/reports/run?line_id=1', { method: 'POST' })).events || []
  } catch { events.value = [] }
}

onMounted(async () => {
  trips.value = await api('/trips')
  await loadEvents()
})

async function saveDirection(r: any, v: string) {
  savingId.value = r.id
  try {
    const updated = await api(`/trips/${r.id}`, {
      method: 'PATCH',
      body: JSON.stringify({ direction: v || null }),
    })
    Object.assign(r, updated)
    await loadEvents()
  } finally {
    savingId.value = null
  }
}

function stripClass(s: string) {
  return s === 'bunching' ? 'bg-bunch' : s === 'large_gap' ? 'bg-large' : ''
}
function label(s: string) {
  return s === 'bunching' ? '串车' : s === 'large_gap' ? '大间隔' : '正常'
}
</script>
<template>
  <h1>班次 · 间隔条带</h1>
  <p class="sub">左侧班次清单（可改班次方向，留空继承线路方向），右侧同方向相邻到站的串车/间隔条带</p>
  <div class="bg-split">
    <aside class="bg-trip-col">
      <h2>班次列表</h2>
      <div v-for="r in trips" :key="r.id ?? r.trip_no" class="bg-trip-row bg-trip-row-dir">
        <div>
          <div>{{ r.trip_no }} <span class="badge" :class="r.resolved_direction === 'down' ? 'badge-warn' : 'badge-ok'">{{ dirLabel(r.resolved_direction) }}</span></div>
          <div class="bg-trip-meta">线路 {{ r.line_id }} · 车 {{ r.vehicle_no }}</div>
          <div class="bg-trip-meta" v-if="!r.direction">未标方向，按{{ r.line_direction === 'down' ? '下行' : '上行' }}兼容</div>
        </div>
        <div class="bg-trip-side">
          <div class="bg-trip-meta">{{ r.planned_depart }}</div>
          <select :value="r.direction ?? ''" :disabled="savingId === r.id"
                  @change="saveDirection(r, ($event.target as HTMLSelectElement).value)">
            <option value="">继承线路</option>
            <option value="up">上行</option>
            <option value="down">下行</option>
          </select>
        </div>
      </div>
    </aside>
    <div class="bg-strip-col">
      <article
        v-for="(e, i) in events"
        :key="i"
        class="bg-gap-strip"
        :class="stripClass(e.status)"
      >
        <header>{{ e.stop_name }} · {{ dirLabel(e.direction) }}</header>
        <div class="bg-gap-body">
          <div class="bg-gap-val">{{ e.gap_min }}′</div>
          <div>计划 {{ e.planned_headway_min }}′</div>
          <div>{{ e.earlier_trip }} → {{ e.later_trip }}</div>
          <span class="badge" :class="e.status === 'bunching' ? 'badge-bad' : e.status === 'large_gap' ? 'badge-warn' : 'badge-ok'">
            {{ label(e.status) }}
          </span>
        </div>
      </article>
      <p v-if="!events.length" class="muted">暂无间隔事件</p>
    </div>
  </div>
</template>
<style scoped>
.bg-trip-row-dir { grid-template-columns: 1fr auto; align-items: center; }
.bg-trip-side { display: flex; flex-direction: column; align-items: flex-end; gap: 0.3rem; }
select {
  background: #0a1c28; color: var(--bg-text);
  border: 1px solid var(--bg-edge); padding: 0.2rem 0.3rem; font-size: 0.74rem;
}
</style>
