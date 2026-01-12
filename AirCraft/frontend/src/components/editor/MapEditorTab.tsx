import { useState, useCallback, useMemo, useRef, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Polyline, useMapEvents, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type { MapNode, MapEdge, MapTrip, NodeType } from '@/types/mapEditor'
import {
    NODE_TYPE_COLORS,
    NODE_TYPE_LABELS,
    generateNodeId,
    generateEdgeId,
    calculateHaversineDistance
} from '@/types/mapEditor'

import { useNotification } from '@/contexts/NotificationContext'
import { useGlobalData } from '@/contexts/GlobalDataContext'
import NodePropertiesPanel from './NodePropertiesPanel'
import EdgeManager from './EdgeManager'
import EdgePanel from './EdgePanel'
import TripManager from './TripManager'
import './MapEditorTab.css'

interface MapEditorTabProps {
    nodes: MapNode[]
    edges: MapEdge[]
    trips: MapTrip[]
    onNodesChange: (nodes: MapNode[]) => void
    onEdgesChange: (edges: MapEdge[]) => void
    onTripsChange: (trips: MapTrip[]) => void
    center?: { lat: number; lng: number }
    defaultZoom?: number
}

type EditorMode = 'view' | 'add_node' | 'edit' | 'edge'

interface MapClickHandlerProps {
    mode: EditorMode
    selectedNodeType: NodeType
    onMapClick: (lat: number, lng: number) => void
}

function MapClickHandler({ mode, onMapClick }: MapClickHandlerProps) {
    useMapEvents({
        click(e) {
            if (mode === 'add_node') {
                onMapClick(e.latlng.lat, e.latlng.lng)
            }
        }
    })
    return null
}

function createNodeIcon(type: NodeType, isSelected: boolean): L.DivIcon {
    const colors = NODE_TYPE_COLORS[type]
    const size = type === 'direction' ? 12 : 20
    const shape = type === 'aircraft_stand' ? 'square' :
        type === 'rest_area' ? 'diamond' : 'circle'

    const borderWidth = isSelected ? 3 : 2
    const borderColor = isSelected ? '#FFFFFF' : colors.border

    let shapeStyle = ''
    if (shape === 'square') {
        shapeStyle = `width: ${size}px; height: ${size}px; border-radius: 2px;`
    } else if (shape === 'diamond') {
        shapeStyle = `width: ${size}px; height: ${size}px; transform: rotate(45deg);`
    } else {
        shapeStyle = `width: ${size}px; height: ${size}px; border-radius: 50%;`
    }

    return L.divIcon({
        className: 'custom-node-icon',
        html: `<div style="
      ${shapeStyle}
      background-color: ${colors.fill};
      border: ${borderWidth}px solid ${borderColor};
      cursor: pointer;
      box-shadow: ${isSelected ? '0 0 8px rgba(255,255,255,0.8)' : '0 2px 4px rgba(0,0,0,0.3)'};
    "></div>`,
        iconSize: [size, size],
        iconAnchor: [size / 2, size / 2]
    })
}

function MapResetControl({ center, zoom }: { center: { lat: number; lng: number }, zoom: number }) {
    const map = useMap()

    const handleReset = (e: React.MouseEvent) => {
        e.preventDefault()
        e.stopPropagation()
        map.setView([center.lat, center.lng], zoom)
    }

    return (
        <div className="leaflet-bottom leaflet-left">
            <div className="leaflet-control leaflet-bar">
                <a
                    href="#"
                    role="button"
                    title="Reset View"
                    onClick={handleReset}
                    className="leaflet-control-zoom-in"
                    style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', width: '30px', height: '30px', textDecoration: 'none', color: '#333' }}
                >
                    <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>center_focus_strong</span>
                </a>
            </div>
        </div>
    )
}

export default function MapEditorTab({
    nodes,
    edges,
    trips,
    onNodesChange,
    onEdgesChange,
    onTripsChange,
    center = { lat: 21.2187, lng: 105.8076 },
    defaultZoom = 15
}: MapEditorTabProps) {
    const [mode, setMode] = useState<EditorMode>('view')
    const [selectedNodeType, setSelectedNodeType] = useState<NodeType>('aircraft_stand')
    const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null)
    const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null)
    const [selectedTripId, setSelectedTripId] = useState<string | null>(null)
    const [edgeCreation, setEdgeCreation] = useState<string | null>(null)
    const { addNotification } = useNotification()
    const { epsilonWalk, setEpsilonWalk } = useGlobalData()

    const selectedNode = useMemo(() =>
        nodes.find(n => n.id === selectedNodeId) || null, [nodes, selectedNodeId])

    const selectedEdge = useMemo(() =>
        edges.find(e => e.id === selectedEdgeId) || null, [edges, selectedEdgeId])



    // Refs to hold latest state for event handlers
    const nodesRef = useRef(nodes)
    const edgesRef = useRef(edges)

    useEffect(() => {
        nodesRef.current = nodes
        edgesRef.current = edges
    }, [nodes, edges])

    const handleMapClick = useCallback((lat: number, lng: number) => {
        if (mode === 'add_node') {
            const newNode: MapNode = {
                id: generateNodeId(),
                type: selectedNodeType,
                latitude: lat,
                longitude: lng
            }
            onNodesChange([...nodesRef.current, newNode])
        }
    }, [mode, selectedNodeType, onNodesChange])

    const handleNodeClick = useCallback((nodeId: string) => {
        if (mode === 'edge') {
            if (!edgeCreation) {
                // Chọn node đầu tiên
                setEdgeCreation(nodeId)
            } else if (nodeId === edgeCreation) {
                // Click lại vào node đang chọn → Hủy chọn
                setEdgeCreation(null)
            } else {
                // Chọn node thứ hai → Tạo cạnh
                const currentNodes = nodesRef.current
                const currentEdges = edgesRef.current

                const nodeA = currentNodes.find(n => n.id === edgeCreation)
                const nodeB = currentNodes.find(n => n.id === nodeId)

                if (nodeA && nodeB) {
                    const existingEdge = currentEdges.find(e =>
                        (e.nodeA === edgeCreation && e.nodeB === nodeId) ||
                        (e.nodeA === nodeId && e.nodeB === edgeCreation)
                    )
                    if (!existingEdge) {
                        const distance = calculateHaversineDistance(
                            nodeA.latitude, nodeA.longitude,
                            nodeB.latitude, nodeB.longitude
                        )
                        const newEdge: MapEdge = {
                            id: generateEdgeId(),
                            nodeA: edgeCreation,
                            nodeB: nodeId,
                            directed: true,
                            distance
                        }
                        onEdgesChange([...currentEdges, newEdge])
                        addNotification('success', `Đã tạo cạnh nối ${nodeA.id} và ${nodeB.id}`)
                    }
                    setEdgeCreation(null)
                }
            }
        } else {
            setSelectedNodeId(nodeId)
            setSelectedEdgeId(null)
            setSelectedTripId(null)
            setMode('edit')
        }
    }, [mode, edgeCreation, onEdgesChange])

    const handleNodeUpdate = useCallback((updatedNode: MapNode) => {
        onNodesChange(nodes.map(n => n.id === updatedNode.id ? updatedNode : n))
    }, [nodes, onNodesChange])

    const handleNodeDelete = useCallback((nodeId: string) => {
        onNodesChange(nodes.filter(n => n.id !== nodeId))
        // Edges connected to this node should be removed (handled by EdgeManager logic or parent? Usually better here)
        // Clean up edges connected to deleted node
        onEdgesChange(edges.filter(e => e.nodeA !== nodeId && e.nodeB !== nodeId))

        // Clean up trips using those edges
        const invalidEdgeIds = edges.filter(e => e.nodeA === nodeId || e.nodeB === nodeId).map(e => e.id)
        onTripsChange(trips.map(t => ({
            ...t,
            edgeIds: t.edgeIds.filter(id => !invalidEdgeIds.includes(id))
        })))

        setSelectedNodeId(null)
        setMode('view')
    }, [nodes, edges, trips, onNodesChange, onEdgesChange, onTripsChange])



    return (
        <div className="map-editor-container">
            <div className="map-editor-main">
                <div className="map-editor-left-panel">
                    <div className="left-panel-section">
                        <div className="left-panel-title">Chế độ</div>
                        <button
                            className={`mode-btn ${mode === 'view' ? 'active' : ''}`}
                            onClick={() => { setMode('view'); setEdgeCreation(null); setSelectedNodeId(null) }}
                        >
                            <span className="material-symbols-outlined">pan_tool</span>
                            <span>Di chuyển</span>
                        </button>
                        <button
                            className={`mode-btn ${mode === 'edge' ? 'active' : ''}`}
                            onClick={() => { setMode('edge'); setEdgeCreation(null) }}
                        >
                            <span className="material-symbols-outlined">timeline</span>
                            <span>Tạo Cạnh</span>
                        </button>
                    </div>

                    <div className="left-panel-section">
                        <div className="left-panel-title">Thêm Node</div>
                        {(Object.keys(NODE_TYPE_LABELS) as NodeType[]).map(type => (
                            <button
                                key={type}
                                className={`mode-btn node-type-btn ${mode === 'add_node' && selectedNodeType === type ? 'active' : ''}`}
                                onClick={() => { setMode('add_node'); setSelectedNodeType(type) }}
                            >
                                <span
                                    className="node-type-icon"
                                    style={{
                                        backgroundColor: NODE_TYPE_COLORS[type].fill,
                                        borderColor: NODE_TYPE_COLORS[type].border
                                    }}
                                />
                                <span>{NODE_TYPE_LABELS[type]}</span>
                            </button>
                        ))}
                    </div>

                    <div className="left-panel-section">
                        <div className="left-panel-title">Hành động</div>
                        <button
                            className="mode-btn danger"
                            onClick={() => selectedNodeId && handleNodeDelete(selectedNodeId)}
                            disabled={!selectedNodeId}
                            style={{ opacity: !selectedNodeId ? 0.5 : 1 }}
                        >
                            <span className="material-symbols-outlined">delete</span>
                            <span>Xóa Node</span>
                        </button>
                        <button
                            className="mode-btn danger"
                            onClick={() => {
                                if (selectedEdgeId) {
                                    if (window.confirm('Bạn có chắc muốn xóa cạnh này?')) {
                                        onEdgesChange(edges.filter(e => e.id !== selectedEdgeId))
                                        onTripsChange(trips.map(t => ({
                                            ...t,
                                            edgeIds: t.edgeIds.filter(id => id !== selectedEdgeId)
                                        })))
                                        setSelectedEdgeId(null)
                                    }
                                }
                            }}
                            disabled={!selectedEdgeId}
                            style={{ opacity: !selectedEdgeId ? 0.5 : 1 }}
                        >
                            <span className="material-symbols-outlined">delete</span>
                            <span>Xóa Cạnh</span>
                        </button>
                    </div>

                    <div className="left-panel-section">
                        <div className="left-panel-title">Cấu hình Trip</div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', padding: '8px 0' }}>
                            <label style={{ fontSize: '12px', color: '#94A3B8' }}>Ngưỡng đi bộ (m)</label>
                            <input
                                type="number"
                                value={epsilonWalk}
                                onChange={(e) => setEpsilonWalk(Number(e.target.value))}
                                min="0"
                                step="10"
                                style={{
                                    padding: '8px 12px',
                                    borderRadius: '6px',
                                    border: '1px solid #334155',
                                    backgroundColor: '#1E293B',
                                    color: '#F1F5F9',
                                    fontSize: '14px',
                                    width: '100%'
                                }}
                            />
                            <span style={{ fontSize: '11px', color: '#64748B' }}>
                                WALK nếu ≤ {epsilonWalk}m, BUS nếu &gt; {epsilonWalk}m
                            </span>
                        </div>
                    </div>

                    <div className="left-panel-spacer" />


                </div>

                <div className="map-section">

                    <MapContainer
                        center={[center.lat, center.lng]}
                        zoom={defaultZoom}
                        className="map-container"
                        scrollWheelZoom={true}
                    >
                        <MapResetControl center={center} zoom={defaultZoom} />
                        <TileLayer
                            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />

                        <MapClickHandler
                            mode={mode}
                            selectedNodeType={selectedNodeType}
                            onMapClick={handleMapClick}
                        />



                        {edges.map(edge => {
                            const nodeA = nodes.find(n => n.id === edge.nodeA)
                            const nodeB = nodes.find(n => n.id === edge.nodeB)
                            if (!nodeA || !nodeB) return null

                            const isSelected = selectedEdgeId === edge.id
                            const selectedTrip = trips.find(t => t.id === selectedTripId)
                            const isTripHighlight = selectedTrip?.edgeIds.includes(edge.id)

                            // Find if this edge is part of any WALK trip
                            const tripWithEdge = trips.find(t => t.edgeIds.includes(edge.id))
                            const isWalkTrip = tripWithEdge?.mode === 'WALK'

                            return (
                                <Polyline
                                    key={edge.id}
                                    positions={[[nodeA.latitude, nodeA.longitude], [nodeB.latitude, nodeB.longitude]]}
                                    pathOptions={{
                                        color: isTripHighlight ? selectedTrip!.color : (isSelected ? '#0EA5E9' : '#64748B'),
                                        weight: isSelected || isTripHighlight ? 5 : 3,
                                        opacity: isSelected || isTripHighlight ? 1 : 0.6,
                                        dashArray: isWalkTrip ? '8, 12' : undefined
                                    }}

                                    eventHandlers={{
                                        click: (e) => {
                                            L.DomEvent.stopPropagation(e as any)
                                            if (selectedTripId) {
                                                const trip = trips.find(t => t.id === selectedTripId)
                                                if (trip) {
                                                    const isEdgeInTrip = trip.edgeIds.includes(edge.id)
                                                    const updatedTrip = {
                                                        ...trip,
                                                        edgeIds: isEdgeInTrip
                                                            ? trip.edgeIds.filter(id => id !== edge.id)
                                                            : [...trip.edgeIds, edge.id]
                                                    }
                                                    onTripsChange(trips.map(t => t.id === trip.id ? updatedTrip : t))
                                                }
                                            } else {
                                                setSelectedEdgeId(edge.id)
                                                setSelectedNodeId(null)
                                                setSelectedTripId(null)
                                            }
                                        }
                                    }}
                                />
                            )
                        })}

                        {nodes.map(node => {
                            const isSelected = node.id === selectedNodeId
                            const isEdgeCreationStart = node.id === edgeCreation
                            const shouldHighlight = isSelected || isEdgeCreationStart

                            return (
                                <Marker
                                    key={node.id}
                                    position={[node.latitude, node.longitude]}
                                    icon={createNodeIcon(node.type, shouldHighlight)}
                                    draggable={mode === 'edit' && node.id === selectedNodeId}
                                    eventHandlers={{
                                        click: () => handleNodeClick(node.id),
                                        dragend: (e) => {
                                            const { lat, lng } = e.target.getLatLng()
                                            handleNodeUpdate({ ...node, latitude: lat, longitude: lng })
                                        }
                                    }}
                                />
                            )
                        })}
                    </MapContainer>
                </div>
            </div>

            <div className="panel-section">
                {selectedNode && (
                    <NodePropertiesPanel
                        node={selectedNode}
                        onUpdate={handleNodeUpdate}
                        onDelete={() => handleNodeDelete(selectedNode.id)}
                    />
                )}

                {selectedEdge && (
                    <EdgePanel
                        edge={selectedEdge}
                        nodes={nodes}
                        trips={trips}
                        onUpdateEdge={(edge) => {
                            onEdgesChange(edges.map(e => e.id === edge.id ? edge : e))
                        }}
                        onDeleteEdge={(edgeId) => {
                            onEdgesChange(edges.filter(e => e.id !== edgeId))
                            onTripsChange(trips.map(t => ({
                                ...t,
                                edgeIds: t.edgeIds.filter(id => id !== edgeId)
                            })))
                            setSelectedEdgeId(null)
                        }}
                        onClose={() => setSelectedEdgeId(null)}
                    />
                )}

                <EdgeManager
                    edges={edges}
                    nodes={nodes}
                    selectedEdgeId={selectedEdgeId}
                    onSelectEdge={setSelectedEdgeId}
                    onDeleteEdge={(edgeId) => {
                        onEdgesChange(edges.filter(e => e.id !== edgeId))
                        onTripsChange(trips.map(t => ({
                            ...t,
                            edgeIds: t.edgeIds.filter(id => id !== edgeId)
                        })))
                        if (selectedEdgeId === edgeId) setSelectedEdgeId(null)
                    }}
                />

                <TripManager
                    trips={trips}
                    edges={edges}
                    nodes={nodes}
                    selectedTripId={selectedTripId}
                    onSelectTrip={setSelectedTripId}
                    onAddTrip={(trip) => onTripsChange([...trips, trip])}
                    onUpdateTrip={(trip) => onTripsChange(trips.map(t => t.id === trip.id ? trip : t))}
                    onDeleteTrip={(tripId) => {
                        onTripsChange(trips.filter(t => t.id !== tripId))
                        if (selectedTripId === tripId) setSelectedTripId(null)
                    }}
                />


            </div>
        </div >
    )
}
