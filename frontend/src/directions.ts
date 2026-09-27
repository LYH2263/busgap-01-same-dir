export type DirectionCode = 'up' | 'down'
export type DirectionFilter = 'all' | DirectionCode

export const DIRECTION_LABELS: Record<DirectionCode, string> = {
  up: '上行',
  down: '下行',
}

export function dirLabel(d?: string | null): string {
  return d === 'down' ? DIRECTION_LABELS.down : DIRECTION_LABELS.up
}

export function dirFilterLabel(f: DirectionFilter): string {
  return f === 'all' ? '全部方向' : DIRECTION_LABELS[f]
}
