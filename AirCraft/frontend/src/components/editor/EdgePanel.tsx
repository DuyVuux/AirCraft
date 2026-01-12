import type { MapNode, MapEdge, MapTrip } from '@/types/mapEditor'

interface EdgePanelProps {
    edge: MapEdge
    nodes: MapNode[]
    trips: MapTrip[]
    onUpdateEdge: (edge: MapEdge) => void
    onDeleteEdge: (edgeId: string) => void
    onClose: () => void
}

export default function EdgePanel({
    edge,
    nodes,
    trips,
    onUpdateEdge,
    onDeleteEdge,
    onClose
}: EdgePanelProps) {
    const getNodeName = (nodeId: string): string => {
        const node = nodes.find(n => n.id === nodeId)
        return node?.name || nodeId.slice(-6)
    }

    const formatDistance = (meters: number): string => {
        if (meters >= 1000) return `${(meters / 1000).toFixed(2)} km`
        return `${meters.toFixed(0)} m`
    }

    const edgeTrips = trips.filter(t => t.edgeIds.includes(edge.id))

    return (
        <div className="edge-panel">
            <div className="panel-header">
                <h3>Thuộc tính cạnh</h3>
                <button className="close-btn" onClick={onClose}>
                    <span className="material-symbols-outlined">close</span>
                </button>
            </div>

            <div className="panel-content">
                <div className="edge-nodes">
                    <span className="node-label">{getNodeName(edge.nodeA)}</span>
                    <span className="edge-arrow">
                        {edge.directed ? '→' : '↔'}
                    </span>
                    <span className="node-label">{getNodeName(edge.nodeB)}</span>
                </div>

                <div className="form-group">
                    <label>Hướng di chuyển</label>
                    <select
                        value={edge.directed ? 'directed' : 'undirected'}
                        onChange={(e) => onUpdateEdge({
                            ...edge,
                            directed: e.target.value === 'directed'
                        })}
                    >
                        <option value="directed">Có hướng (A → B)</option>
                        <option value="undirected">Vô hướng (A ↔ B)</option>
                    </select>
                </div>

                <div className="info-row">
                    <span className="info-label">Khoảng cách:</span>
                    <span className="info-value">{formatDistance(edge.distance)}</span>
                </div>

                <div className="form-group">
                    <label>Thời gian di chuyển (giây)</label>
                    <input
                        type="number"
                        value={edge.travelTime || 0}
                        onChange={(e) => onUpdateEdge({
                            ...edge,
                            travelTime: parseFloat(e.target.value) || 0
                        })}
                        min="0"
                    />
                </div>

                <div className="trips-section">
                    <h4>Trips sử dụng cạnh này ({edgeTrips.length})</h4>
                    {edgeTrips.length === 0 ? (
                        <p className="empty-text">Chưa có trip nào</p>
                    ) : (
                        <div className="trips-list">
                            {edgeTrips.map(trip => (
                                <div key={trip.id} className="trip-item">
                                    <span
                                        className="trip-color"
                                        style={{ backgroundColor: trip.color }}
                                    />
                                    <span>{trip.name}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                <button
                    className="dataset-btn danger"
                    onClick={() => {
                        if (window.confirm('Bạn có chắc muốn xóa cạnh này?')) {
                            onDeleteEdge(edge.id)
                            onClose()
                        }
                    }}
                    style={{
                        width: '100%',
                        padding: '0.75rem',
                        marginTop: '1rem',
                    }}
                >
                    <span className="material-symbols-outlined">delete</span>
                    Xóa cạnh
                </button>
            </div>
        </div>
    )
}
