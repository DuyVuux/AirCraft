export type NodeType = 'aircraft_stand' | 'bus_stop' | 'rest_area' | 'direction'

export interface MapNode {
  id: string
  name?: string
  type: NodeType
  longitude: number
  latitude: number
}



export interface MapEdge {
  id: string
  nodeA: string
  nodeB: string
  directed: boolean
  distance: number
  travelTime?: number
}

export type TripMode = 'WALK' | 'BUS'

export interface MapTrip {
  id: string
  name: string
  edgeIds: string[]
  color: string
  distance?: number
  path?: string[]
  mode?: TripMode
  tags?: string[]
}

export interface MapSegment {
  manualTime?: number;
  [key: string]: any;
}

export interface MapRoute {
  startNodeId: string;
  endNodeId: string;
  timeMode: 'manual_input' | 'auto_calc' | string;
  segments: MapSegment[];
  fixedVelocity?: number;
  totalDistance?: number;
}

export const NODE_TYPE_LABELS: Record<NodeType, string> = {
  aircraft_stand: 'Vị trí đáp máy bay',
  bus_stop: 'Điểm xe bus',
  rest_area: 'Điểm nghỉ ngơi',
  direction: 'Node định hướng'
}

export const NODE_TYPE_COLORS: Record<NodeType, { fill: string; border: string }> = {
  aircraft_stand: { fill: '#0EA5E9', border: '#0284C7' },
  bus_stop: { fill: '#F59E0B', border: '#D97706' },
  rest_area: { fill: '#10B981', border: '#059669' },
  direction: { fill: '#94A3B8', border: '#64748B' }
}



export function generateTripColor(tripIndex: number): string {
  const hue = (tripIndex * 137.508 + 60) % 360
  return `hsl(${hue}, 65%, 55%)`
}

export function calculateHaversineDistance(
  lat1: number, lon1: number,
  lat2: number, lon2: number
): number {
  const R = 6371000
  const φ1 = lat1 * Math.PI / 180
  const φ2 = lat2 * Math.PI / 180
  const Δφ = (lat2 - lat1) * Math.PI / 180
  const Δλ = (lon2 - lon1) * Math.PI / 180

  const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) *
    Math.sin(Δλ / 2) * Math.sin(Δλ / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))

  return R * c
}

export function generateNodeId(): string {
  return `node-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}



export function generateEdgeId(): string {
  return `edge-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}

export function generateTripId(): string {
  return `trip-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
}
