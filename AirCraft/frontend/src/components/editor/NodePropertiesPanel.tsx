import React from 'react'
import type { MapNode, NodeType } from '@/types/mapEditor'
import { NODE_TYPE_LABELS, NODE_TYPE_COLORS } from '@/types/mapEditor'

interface NodePropertiesPanelProps {
    node: MapNode
    onUpdate: (node: MapNode) => void
    onDelete: () => void
}

export default function NodePropertiesPanel({ node, onUpdate, onDelete }: NodePropertiesPanelProps) {
    const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        onUpdate({ ...node, name: e.target.value || undefined })
    }

    const handleTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        onUpdate({ ...node, type: e.target.value as NodeType })
    }

    return (
        <div className="properties-panel">
            <div className="panel-header">
                <h3>Thuộc tính Node</h3>
                <button className="delete-btn" onClick={onDelete} title="Xóa node">
                    <span className="material-symbols-outlined">delete</span>
                </button>
            </div>

            <div className="form-group">
                <label>Tên</label>
                <input
                    type="text"
                    value={node.name || ''}
                    onChange={handleNameChange}
                    placeholder="Nhập tên node..."
                />
            </div>

            <div className="form-group">
                <label>Loại</label>
                <select value={node.type} onChange={handleTypeChange}>
                    {(Object.keys(NODE_TYPE_LABELS) as NodeType[]).map(type => (
                        <option key={type} value={type}>
                            {NODE_TYPE_LABELS[type]}
                        </option>
                    ))}
                </select>
            </div>

            <div className="form-group">
                <label>Màu</label>
                <div className="color-preview">
                    <span
                        className="color-dot"
                        style={{ backgroundColor: NODE_TYPE_COLORS[node.type].fill }}
                    />
                    <span className="color-text">{NODE_TYPE_COLORS[node.type].fill}</span>
                </div>
            </div>

            <div className="form-group">
                <label>Tọa độ</label>
                <div className="coordinates">
                    <span>Lat: {node.latitude.toFixed(6)}</span>
                    <span>Lng: {node.longitude.toFixed(6)}</span>
                </div>
            </div>
        </div>
    )
}
