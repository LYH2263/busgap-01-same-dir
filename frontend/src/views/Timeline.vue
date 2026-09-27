<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { api } from '../api'
import { useDirectionFilter } from '../composables/useDirectionFilter'
import DirectionFilterBar from '../components/DirectionFilterBar.vue'
import { dirFilterLabel, dirLabel } from '../directions'

const data = ref<{ stop_name: string; marks: any[] }>({ stop_name: '', marks: [] })
const { filter } = useDirectionFilter()

async function load() {
  const qs = filter.value === 'all' ? '' : `&direction=${filter.value}`
  data.value = await api(`/reports/timeline?line_id=1${qs}`)
}
onMounted(load)
watch(filter, load)
</script>
<template>
  <h1>时间轴明细</h1>
  <p class="sub">站点「{{ data.stop_name }}」到站分布（{{ dirFilterLabel(filter) }}，仅同方向相邻参与间隔判定）</p>
  <DirectionFilterBar />
  <div class="card" style="margin-top:0.8rem">
    <div class="tl-track">
      <div v-for="m in data.marks" :key="m.trip_no + '-' + m.direction" class="tl-mark"
        :style="{ left: m.pct + '%', background: m.direction === 'down' ? 'var(--bg-amber)' : (m.pct < 15 ? 'var(--bg-red)' : 'var(--bg-cyan)') }"
        :title="m.trip_no + ' ' + dirLabel(m.direction) + ' ' + m.actual_arrive" />
    </div>
    <table>
      <thead><tr><th>班次</th><th>方向</th><th>到站时间</th><th>相对位置</th></tr></thead>
      <tbody>
        <tr v-for="m in data.marks" :key="m.trip_no + '-' + m.direction">
          <td>{{ m.trip_no }}</td><td>{{ dirLabel(m.direction) }}</td><td>{{ m.actual_arrive }}</td><td>{{ m.pct }}%</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
