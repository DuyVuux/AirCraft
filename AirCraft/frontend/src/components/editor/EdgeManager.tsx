import { useState } from 'react'
import type { MapNode, MapEdge } from '@/types/mapEditor'

interface EdgeManagerProps {
    edges: MapEdge[]
    nodes: MapNode[]
    selectedEdgeId: string | null
    onSelectEdge: (edgeId: string | null) => void
    onDeleteEdge: (edgeId: string) => void
}

export default function EdgeManager({
    edges,
    nodes,
    selectedEdgeId,
    onSelectEdge,
    onDeleteEdge
}: EdgeManagerProps) {
    const [isCollapsed, setIsCollapsed] = useState(false)

    const getNodeName = (nodeId: string): string => {
        const node = nodes.find(n => n.id === nodeId)
        return node?.name || nodeId.slice(-6)
    }

    const formatDistance = (meters: number): string => {
        if (meters >= 1000) return `${(meters / 1000).toFixed(2)} km`
        return `${meters.toFixed(0)} m`
    }

    return (
        <div className="edge-manager">
            <div className="panel-header"
                onClick={() => setIsCollapsed(!isCollapsed)}
                style={{ cursor: 'pointer', userSelect: 'none' }}
            >
                <h3>Cạnh ({edges.length})</h3>
                <span className="material-symbols-outlined" style={{ fontSize: '1.25rem', color: 'var(--color-text-secondary)' }}>
                    {isCollapsed ? 'expand_more' : 'expand_less'}
                </span>
            </div>

            {!isCollapsed && (
                edges.length === 0 ? (
                    <div className="empty-state">
                        <span className="material-symbols-outlined">timeline</span>
                        <p>Chưa có cạnh nào</p>
                        <p className="hint">Click 2 node liên tiếp để tạo cạnh</p>
                    </div>
                ) : (
                    <div className="edges-list">
                        {edges.map(edge => (
                            <div
                                key={edge.id}
                                className={`edge-item ${selectedEdgeId === edge.id ? 'selected' : ''}`}
                                onClick={() => onSelectEdge(edge.id)}
                            >
                                <div className="edge-header">
                                    <span className="edge-direction">
                                        {edge.directed ? '→' : '↔'}
                                    </span>
                                    <span className="edge-path">
                                        {getNodeName(edge.nodeA)} {edge.directed ? '→' : '↔'} {getNodeName(edge.nodeB)}
                                    </span>
                                    <button
                                        className="delete-btn"
                                        onClick={(e) => { e.stopPropagation(); onDeleteEdge(edge.id) }}
                                    >
                                        <span className="material-symbols-outlined">close</span>
                                    </button>
                                </div>
                                <div className="edge-info">
                                    <span>📏 {formatDistance(edge.distance)}</span>
                                    {edge.travelTime && <span>⏱️ {edge.travelTime}s</span>}
                                </div>
                            </div>
                        ))}
                    </div>
                )
            )}
        </div>
    )
}
