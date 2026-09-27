export const DIRECTION_OPTIONS = [
  { value: 'up', label: '上行' },
  { value: 'down', label: '下行' },
] as const

export function directionLabel(d: string | null | undefined): string {
  return d === 'down' ? '下行' : '上行'
}
