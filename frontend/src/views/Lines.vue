<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../api'
import { dirLabel } from '../directions'
const rows = ref<any[]>([])
const savingId = ref<number | null>(null)

onMounted(async () => { rows.value = await api('/lines') })

async function saveDirection(r: any, v: string) {
  savingId.value = r.id
  try {
    const updated = await api(`/lines/${r.id}`, {
      method: 'PATCH',
      body: JSON.stringify({ direction: v || null }),
    })
    Object.assign(r, updated)
  } finally {
    savingId.value = null
  }
}
</script>
<template>
  <h1>线路</h1>
  <p class="sub">运营线路与串车 / 大间隔判定阈值；线路方向作为未标方向班次的默认值，留空按上行兼容</p>
  <div class="card">
    <table>
      <thead><tr><th>编码</th><th>名称</th><th>计划间隔(分)</th><th>串车阈值</th><th>大间隔阈值</th><th>登记方向</th><th>生效方向</th></tr></thead>
      <tbody>
        <tr v-for="r in rows" :key="r.id ?? JSON.stringify(r)">
          <td>{{ r.code }}</td><td>{{ r.name }}</td>
          <td>{{ r.planned_headway_min }}</td><td>{{ r.bunch_threshold }}</td><td>{{ r.large_threshold }}</td>
          <td>
            <select :value="r.direction ?? ''" :disabled="savingId === r.id"
                    @change="saveDirection(r, ($event.target as HTMLSelectElement).value)">
              <option value="">未登记</option>
              <option value="up">上行</option>
              <option value="down">下行</option>
            </select>
          </td>
          <td><span class="badge" :class="r.direction === 'down' ? 'badge-warn' : 'badge-ok'">{{ dirLabel(r.direction) }}</span></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
