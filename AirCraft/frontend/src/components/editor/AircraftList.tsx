import React, { useState } from 'react';
import type { Aircraft } from '@/types/aircraft';
import './Editor.css';

interface AircraftListProps {
    aircrafts: Aircraft[];
    onEdit: (aircraft: Aircraft) => void;
    onDelete: (aircraftId: string) => void;
    onBulkDelete?: (aircraftIds: string[]) => void;
    selectedId?: string | null;
}

const getTaskColor = (code: string) => {
    const colors = [
        { bg: '#fee2e2', text: '#991b1b' },
        { bg: '#ffedd5', text: '#9a3412' },
        { bg: '#fef9c3', text: '#854d0e' },
        { bg: '#dcfce7', text: '#166534' },
        { bg: '#dbeafe', text: '#1e40af' },
        { bg: '#e0e7ff', text: '#3730a3' },
        { bg: '#f3e8ff', text: '#6b21a8' },
        { bg: '#fae8ff', text: '#86198f' },
    ];
    let hash = 0;
    for (let i = 0; i < code.length; i++) {
        hash = code.charCodeAt(i) + ((hash << 5) - hash);
    }
    return colors[Math.abs(hash) % colors.length];
};

function AircraftList({
    aircrafts,
    onEdit,
    onDelete,
    onBulkDelete,
    selectedId
}: AircraftListProps) {
    const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

    const handleToggleSelect = (id: string, e: React.MouseEvent) => {
        e.stopPropagation();
        setSelectedIds(prev => {
            const newSet = new Set(prev);
            if (newSet.has(id)) {
                newSet.delete(id);
            } else {
                newSet.add(id);
            }
            return newSet;
        });
    };

    const handleSelectAll = () => {
        if (selectedIds.size === aircrafts.length) {
            setSelectedIds(new Set());
        } else {
            setSelectedIds(new Set(aircrafts.map(a => a.aircraftId)));
        }
    };

    const handleBulkDelete = () => {
        if (selectedIds.size === 0) return;
        if (!confirm(`Bạn có chắc muốn xóa ${selectedIds.size} máy bay?`)) return;

        if (onBulkDelete) {
            onBulkDelete(Array.from(selectedIds));
        } else {
            selectedIds.forEach(id => onDelete(id));
        }
        setSelectedIds(new Set());
    };

    if (aircrafts.length === 0) {
        return (
            <div className="editor-card">
                <p className="editor-task-list-empty">Chưa có máy bay nào. Thêm máy bay mới ở nút bên trên.</p>
            </div>
        );
    }

    const allSelected = selectedIds.size === aircrafts.length;

    return (
        <div className="editor-card" style={{ padding: '0.75rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', paddingLeft: '0.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <input
                        type="checkbox"
                        checked={allSelected}
                        onChange={handleSelectAll}
                        style={{ width: '16px', height: '16px', cursor: 'pointer' }}
                        title="Chọn tất cả"
                    />
                    <h3 className="editor-card-title" style={{ margin: 0 }}>
                        Danh sách tàu bay ({aircrafts.length})
                    </h3>
                </div>
                {selectedIds.size > 0 && (
                    <button
                        className="dataset-btn danger"
                        onClick={handleBulkDelete}
                    >
                        <span className="material-symbols-outlined" style={{ fontSize: '1rem' }}>delete</span>
                        Xóa ({selectedIds.size})
                    </button>
                )}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {aircrafts.map((aircraft) => {
                    const isSelected = selectedId === aircraft.aircraftId;
                    const isChecked = selectedIds.has(aircraft.aircraftId);
                    return (
                        <div
                            key={aircraft.aircraftId}
                            style={{
                                display: 'flex',
                                gap: '0.75rem',
                                padding: '0.75rem',
                                border: `1px solid ${isSelected ? 'var(--color-primary)' : isChecked ? 'var(--color-primary)' : 'var(--color-border)'}`,
                                borderRadius: '0.375rem',
                                backgroundColor: isChecked ? 'rgba(59, 130, 246, 0.1)' : isSelected ? 'rgba(14, 165, 233, 0.05)' : 'var(--color-surface)',
                                cursor: 'pointer',
                                transition: 'all 0.2s ease',
                            }}
                        >
                            <input
                                type="checkbox"
                                checked={isChecked}
                                onClick={(e) => handleToggleSelect(aircraft.aircraftId, e)}
                                onChange={() => { }}
                                style={{ width: '16px', height: '16px', cursor: 'pointer', flexShrink: 0, marginTop: '2px' }}
                            />

                            <div style={{ flex: 1 }} onClick={() => onEdit(aircraft)}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                        <span style={{ fontWeight: 600, fontSize: '0.925rem', color: 'var(--color-primary)' }}>
                                            {aircraft.aircraftId}
                                        </span>
                                        <span style={{
                                            fontSize: '0.75rem',
                                            padding: '0.125rem 0.375rem',
                                            borderRadius: '0.25rem',
                                            backgroundColor: 'var(--color-surface-hover)',
                                            border: '1px solid var(--color-border)',
                                            color: 'var(--color-text-secondary)'
                                        }}>
                                            {aircraft.aType.id}
                                        </span>
                                    </div>

                                    <div style={{ display: 'flex', gap: '0.25rem' }}>
                                        <button
                                            className="editor-form-button-secondary"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                onEdit(aircraft);
                                            }}
                                            style={{ padding: '0.25rem', border: 'none', color: 'var(--color-primary)', minWidth: 'auto' }}
                                            title="Chỉnh sửa"
                                        >
                                            <span className="material-symbols-outlined" style={{ fontSize: '1.25rem' }}>edit</span>
                                        </button>
                                        <button
                                            className="editor-form-button-secondary"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                onDelete(aircraft.aircraftId);
                                            }}
                                            style={{ padding: '0.25rem', border: 'none', color: '#ef4444', minWidth: 'auto' }}
                                            title="Xóa"
                                        >
                                            <span className="material-symbols-outlined" style={{ fontSize: '1.25rem' }}>delete</span>
                                        </button>
                                    </div>
                                </div>

                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.75rem', color: 'var(--color-text-secondary)', marginTop: '0.5rem' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                                        <span className="material-symbols-outlined" style={{ fontSize: '0.875rem' }}>location_on</span>
                                        {aircraft.location.locationId || '---'}
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                                        <span className="material-symbols-outlined" style={{ fontSize: '0.875rem' }}>schedule</span>
                                        {aircraft.timeWindow.start ? aircraft.timeWindow.start.slice(11, 16) : '--:--'} - {aircraft.timeWindow.end ? aircraft.timeWindow.end.slice(11, 16) : '--:--'}
                                    </div>
                                </div>

                                {aircraft.requiredTasks.length > 0 && (
                                    <div style={{ display: 'flex', gap: '0.25rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
                                        {aircraft.requiredTasks.map((task, idx) => {
                                            const theme = getTaskColor(task.taskCode);
                                            return (
                                                <span key={idx} style={{
                                                    fontSize: '0.7rem',
                                                    padding: '0.125rem 0.375rem',
                                                    borderRadius: '0.75rem',
                                                    backgroundColor: theme.bg,
                                                    color: theme.text,
                                                    fontWeight: 500,
                                                    border: `1px solid ${theme.bg}`
                                                }}>
                                                    {task.taskCode}
                                                </span>
                                            );
                                        })}
                                    </div>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

export default AircraftList;
