<script setup lang="ts">
import { useDirectionFilter } from '../composables/useDirectionFilter'
const { filter } = useDirectionFilter()
const options = [
  { value: 'all', label: '全部' },
  { value: 'up', label: '上行' },
  { value: 'down', label: '下行' },
] as const
</script>
<template>
  <div class="dir-filter" role="group" aria-label="按方向过滤">
    <button
      v-for="o in options"
      :key="o.value"
      type="button"
      class="dir-filter-btn"
      :class="{ active: filter === o.value }"
      @click="filter = o.value"
    >{{ o.label }}</button>
  </div>
</template>
<style scoped>
.dir-filter { display: inline-flex; border: 1px solid var(--bg-edge); }
.dir-filter-btn {
  background: #0a1c28; color: var(--bg-dim);
  border: none; border-right: 1px solid var(--bg-edge);
  padding: 0.28rem 0.7rem; font-size: 0.76rem; cursor: pointer;
}
.dir-filter-btn:last-child { border-right: none; }
.dir-filter-btn.active { background: rgba(46,196,255,0.18); color: var(--bg-cyan); font-weight: 700; }
.dir-filter-btn:hover { color: var(--bg-text); }
</style>
