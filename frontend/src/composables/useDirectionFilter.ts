import { ref, watch } from 'vue'
import type { DirectionFilter } from '../directions'

const STORAGE_KEY = 'busgap.direction-filter'

function readInitial(): DirectionFilter {
  const v = localStorage.getItem(STORAGE_KEY)
  return v === 'up' || v === 'down' || v === 'all' ? v : 'all'
}

// 全局单例：顶部间隔轴与时间轴页共用同一个过滤选择，离开再进来仍保留
const filter = ref<DirectionFilter>(readInitial())

watch(filter, (v) => localStorage.setItem(STORAGE_KEY, v))

export function useDirectionFilter() {
  return { filter }
}
