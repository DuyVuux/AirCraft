import { useState } from 'react'
import type { MapNode, MapEdge, MapTrip } from '@/types/mapEditor'
import { generateTripId, generateTripColor } from '@/types/mapEditor'

interface TripManagerProps {
    trips: MapTrip[]
    edges: MapEdge[]
    nodes: MapNode[]
    selectedTripId: string | null
    onSelectTrip: (tripId: string | null) => void
    onAddTrip: (trip: MapTrip) => void
    onUpdateTrip: (trip: MapTrip) => void
    onDeleteTrip: (tripId: string) => void
}

export default function TripManager({
    trips,
    edges,
    nodes,
    selectedTripId,
    onSelectTrip,
    onAddTrip,
    onUpdateTrip,
    onDeleteTrip
}: TripManagerProps) {
    const [isCreating, setIsCreating] = useState(false)
    const [isCollapsed, setIsCollapsed] = useState(false)
    const [newTripName, setNewTripName] = useState('')

    const getNodeName = (nodeId: string): string => {
        const node = nodes.find(n => n.id === nodeId)
        return node?.name || nodeId.slice(-6)
    }

    const getTripPath = (trip: MapTrip): string => {
        if (trip.edgeIds.length === 0) return '(Chưa có cạnh)'

        const tripEdges = trip.edgeIds
            .map(id => edges.find(e => e.id === id))
            .filter(Boolean) as MapEdge[]

        if (tripEdges.length === 0) return '(Chưa có cạnh)'

        const nodeNames = [getNodeName(tripEdges[0].nodeA)]
        tripEdges.forEach(edge => {
            nodeNames.push(getNodeName(edge.nodeB))
        })

        return nodeNames.join(' → ')
    }

    const handleCreateTrip = () => {
        if (!newTripName.trim()) return
        const newTrip: MapTrip = {
            id: generateTripId(),
            name: newTripName.trim(),
            edgeIds: [],
            color: generateTripColor(trips.length)
        }
        onAddTrip(newTrip)
        setNewTripName('')
        setIsCreating(false)
        setIsCollapsed(false)
    }

    return (
        <div className="trip-manager">
            <div className="panel-header">
                <div
                    style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', flex: 1, userSelect: 'none' }}
                    onClick={() => setIsCollapsed(!isCollapsed)}
                >
                    <h3>Trips ({trips.length})</h3>
                    <span className="material-symbols-outlined" style={{ fontSize: '1.25rem', color: 'var(--color-text-secondary)' }}>
                        {isCollapsed ? 'expand_more' : 'expand_less'}
                    </span>
                </div>
                <button
                    className="add-btn"
                    onClick={() => {
                        setIsCreating(true)
                        setIsCollapsed(false)
                    }}
                >
                    <span className="material-symbols-outlined">add</span>
                </button>
            </div>

            {!isCollapsed && (
                <>
                    {isCreating && (
                        <div className="create-trip-form" style={{ marginBottom: '1rem', padding: '0.75rem', background: 'var(--color-surface-hover)', borderRadius: '8px' }}>
                            <input
                                type="text"
                                className="editor-form-input"
                                placeholder="Nhập tên trip..."
                                value={newTripName}
                                onChange={(e) => setNewTripName(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleCreateTrip()}
                                autoFocus
                                style={{ marginBottom: '0.5rem' }}
                            />
                            <div className="form-actions" style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                                <button className="editor-form-button-secondary" onClick={() => setIsCreating(false)} style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>Hủy</button>
                                <button className="editor-form-button-primary" onClick={handleCreateTrip} style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}>Tạo</button>
                            </div>
                        </div>
                    )}

                    {trips.length === 0 ? (
                        <div className="empty-state">
                            <span className="material-symbols-outlined">route</span>
                            <p>Chưa có trip nào</p>
                            <button className="editor-form-button-primary" onClick={() => { setIsCreating(true); setIsCollapsed(false); }} style={{ marginTop: '0.5rem' }}>
                                <span className="material-symbols-outlined">add</span>
                                Tạo Trip Mới
                            </button>
                        </div>
                    ) : (
                        <div className="trips-list">
                            {selectedTripId && (
                                <div className="trip-instruction-banner">
                                    <span className="material-symbols-outlined">info</span>
                                    <small>Click vào cạnh trên bản đồ để thêm/bớt khỏi trip</small>
                                </div>
                            )}
                            {trips.map(trip => (
                                <div
                                    key={trip.id}
                                    className={`trip-item ${selectedTripId === trip.id ? 'selected' : ''}`}
                                    onClick={() => onSelectTrip(selectedTripId === trip.id ? null : trip.id)}
                                >
                                    <div className="trip-header">
                                        <span
                                            className="trip-color"
                                            style={{ backgroundColor: trip.color }}
                                        />
                                        <input
                                            type="text"
                                            className="trip-name"
                                            value={trip.name}
                                            onChange={(e) => onUpdateTrip({ ...trip, name: e.target.value })}
                                            onClick={(e) => e.stopPropagation()}
                                        />
                                        <button
                                            className="delete-btn"
                                            onClick={(e) => { e.stopPropagation(); onDeleteTrip(trip.id) }}
                                        >
                                            <span className="material-symbols-outlined">close</span>
                                        </button>
                                    </div>
                                    <div className="trip-path">
                                        {getTripPath(trip)}
                                    </div>
                                    <div className="trip-info">
                                        <span>{trip.edgeIds.length} cạnh</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </>
            )}
        </div>
    )
}
