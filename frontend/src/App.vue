<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { RouterLink, RouterView } from 'vue-router'
import { api } from './api'
import { useDirectionFilter } from './composables/useDirectionFilter'
import DirectionFilterBar from './components/DirectionFilterBar.vue'
import { dirLabel } from './directions'

const marks = ref<any[]>([])
const stopName = ref('')
const { filter } = useDirectionFilter()

async function load() {
  try {
    const qs = filter.value === 'all' ? '' : `&direction=${filter.value}`
    const data = await api(`/reports/timeline?line_id=1${qs}`)
    marks.value = data.marks || []
    stopName.value = data.stop_name || ''
  } catch {
    marks.value = []
  }
}

onMounted(load)
watch(filter, load)
</script>
<template>
  <div class="bg-shell">
    <header class="bg-headway">
      <div class="bg-headway-meta">
        <span class="bg-brand">BusGap · 串车检测</span>
        <span class="bg-stop">发车间隔轴 · {{ stopName || '主站' }}</span>
      </div>
      <div class="bg-rail">
        <div class="bg-rail-ticks">
          <span v-for="t in 11" :key="t">{{ (t - 1) * 10 }}%</span>
        </div>
        <div class="bg-rail-track">
          <div
            v-for="m in marks"
            :key="m.trip_no + '-' + m.direction"
            class="bg-bus-dot"
            :class="{ 'bg-bus-tight': m.pct < 15, 'bg-bus-down': m.direction === 'down' }"
            :style="{ left: m.pct + '%' }"
            :title="`${m.trip_no} ${dirLabel(m.direction)} ${m.actual_arrive}`"
          >
            <span class="bg-bus-label">{{ m.trip_no }}</span>
          </div>
        </div>
        <div class="bg-rail-tools">
          <DirectionFilterBar />
          <span class="bg-rail-hint">间隔轴只比较同方向相邻到站</span>
        </div>
      </div>
      <nav class="bg-segments">
        <RouterLink to="/timeline">时间轴</RouterLink>
        <RouterLink to="/trips">班次</RouterLink>
        <RouterLink to="/arrivals">到站</RouterLink>
        <RouterLink to="/reports">串车报告</RouterLink>
        <RouterLink to="/lines">线路</RouterLink>
        <RouterLink to="/suggestions">建议</RouterLink>
      </nav>
    </header>
    <div class="bg-deck">
      <RouterView />
    </div>
  </div>
</template>
<style scoped>
.bg-rail-tools { display: flex; align-items: center; gap: 0.7rem; margin-top: 0.45rem; }
.bg-rail-hint { font-size: 0.7rem; color: var(--bg-dim); }
.bg-bus-dot.bg-bus-down { background: var(--bg-amber); box-shadow: 0 0 10px rgba(255,176,32,0.55); }
.bg-bus-dot.bg-bus-down.bg-bus-tight { background: var(--bg-red); }
</style>
