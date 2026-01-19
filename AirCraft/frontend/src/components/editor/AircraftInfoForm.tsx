import React, { useState } from 'react';
import type { Aircraft, AircraftTypeId } from '@/types/aircraft';
import { AIRCRAFT_TYPES } from '@/types/aircraft';
import type { Task } from './TaskEditor';
import './Editor.css';

interface AircraftInfoFormProps {
    aircraft: Aircraft;
    onChange: (field: keyof Aircraft, value: any) => void;
    onSave?: () => void;
    onStartEdit?: () => void;
    isReadOnly?: boolean;
    availableTaskCodes?: string[];
    taskMap?: Map<string, Task>;
    initialData?: Aircraft | null;
}

const AircraftInfoForm: React.FC<AircraftInfoFormProps> = ({
    aircraft,
    onChange,
    onSave,
    onStartEdit,
    isReadOnly = false,
    availableTaskCodes = [],
    taskMap,
    initialData
}) => {
    // Use state for task inputs
    const [newTaskCode, setNewTaskCode] = useState('');
    const [newMinLevel, setNewMinLevel] = useState<number>(1);
    const [errors, setErrors] = useState<Record<string, string>>({});

    // Validation function
    const validateForm = (): boolean => {
        const newErrors: Record<string, string> = {};

        if (!aircraft.aircraftId.trim()) {
            newErrors.aircraftId = 'Aircraft ID là bắt buộc';
        }

        if (!aircraft.location.locationId.trim()) {
            newErrors.locationId = 'Vui lòng chọn vị trí trên bản đồ';
        }

        if (!aircraft.timeWindow.start) {
            newErrors.timeWindowStart = 'Time Window Start là bắt buộc';
        }

        if (!aircraft.timeWindow.end) {
            newErrors.timeWindowEnd = 'Time Window End là bắt buộc';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const isFormValid = (): boolean => {
        // Simple check for button enablement
        return (
            aircraft.aircraftId.trim() !== '' &&
            aircraft.location.locationId.trim() !== '' &&
            aircraft.timeWindow.start !== '' &&
            aircraft.timeWindow.end !== ''
        );
    };

    const handleAircraftTypeChange = (typeId: AircraftTypeId) => {
        onChange('aType', {
            id: typeId,
            desc: AIRCRAFT_TYPES[typeId],
        });
    };

    const handleAddTask = () => {
        if (!newTaskCode) return;

        // Check if task already exists
        const taskExists = aircraft.requiredTasks.some(
            (task) => task.taskCode === newTaskCode
        );

        if (taskExists) return;

        onChange('requiredTasks', [
            ...aircraft.requiredTasks,
            { taskCode: newTaskCode, minLevel: newMinLevel },
        ]);
        setNewTaskCode(''); // Reset selection
        setNewMinLevel(1);
    };

    const handleRemoveTask = (index: number) => {
        onChange('requiredTasks', aircraft.requiredTasks.filter((_, i) => i !== index));
    };

    const handleSaveLocal = () => {
        if (!validateForm()) return;
        onSave?.();
    };

    return (
        <div style={{ height: '100%', overflowY: 'auto', paddingRight: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.75rem', width: '100%' }}>

            {isReadOnly && (
                <div className="editor-readonly-banner">
                    <span className="material-symbols-outlined">lock</span>
                    Chế độ xem chi tiết — Nhấn "Update" để chỉnh sửa
                </div>
            )}

            {/* Basic Info & Time - Grouped */}
            <div className="editor-card">
                <h3 className="editor-card-title">{initialData ? 'Thông tin máy bay' : 'Thêm mới máy bay'}</h3>

                <div className="editor-form-grid">
                    <div className="editor-form-group">
                        <label className="editor-form-label">Aircraft ID *</label>
                        <input
                            className="editor-form-input"
                            value={aircraft.aircraftId}
                            onChange={(e) => {
                                onChange('aircraftId', e.target.value);
                                if (errors.aircraftId) setErrors(p => ({ ...p, aircraftId: '' }));
                            }}
                            placeholder="AIRCRAFT-001"
                            readOnly={isReadOnly}
                            style={errors.aircraftId ? { borderColor: 'var(--color-danger)' } : {}}
                        />
                        {errors.aircraftId && <p className="editor-form-helper text-danger">{errors.aircraftId}</p>}
                    </div>

                    <div className="editor-form-group">
                        <label className="editor-form-label">Registration Number</label>
                        <input
                            className="editor-form-input"
                            value={aircraft.registrationNumber || ''}
                            onChange={(e) => onChange('registrationNumber', e.target.value)}
                            placeholder="VN-A123"
                            readOnly={isReadOnly}
                        />
                        <p className="editor-form-helper">Số đăng ký máy bay (VD: VN-A123)</p>
                    </div>

                    <div className="editor-form-group">
                        <label className="editor-form-label">Flight Number</label>
                        <input
                            className="editor-form-input"
                            value={aircraft.flightNumber || ''}
                            onChange={(e) => onChange('flightNumber', e.target.value)}
                            placeholder="VN123"
                            readOnly={isReadOnly}
                        />
                        <p className="editor-form-helper">Số hiệu chuyến bay (VD: VN123)</p>
                    </div>

                    <div className="editor-form-group">
                        <label className="editor-form-label">Type</label>
                        <div className="editor-form-select-wrapper">
                            <select
                                className="editor-form-select"
                                value={aircraft.aType.id}
                                onChange={(e) => handleAircraftTypeChange(e.target.value as AircraftTypeId)}
                                disabled={isReadOnly}
                            >
                                {Object.entries(AIRCRAFT_TYPES).map(([id, desc]) => (
                                    <option key={id} value={id}>{desc}</option>
                                ))}
                            </select>
                            <span className="material-symbols-outlined editor-form-select-icon">expand_more</span>
                        </div>
                    </div>
                </div>

                <div className="editor-form-grid" style={{ marginTop: '1rem' }}>
                    <div className="editor-form-group">
                        <label className="editor-form-label">Start Time *</label>
                        <input
                            className="editor-date-input"
                            type="datetime-local"
                            value={aircraft.timeWindow.start ? aircraft.timeWindow.start.replace('Z', '').slice(0, 16) : ''}
                            onChange={(e) => onChange('timeWindow', { ...aircraft.timeWindow, start: new Date(e.target.value).toISOString() })}
                            readOnly={isReadOnly}
                        />
                        {errors.timeWindowStart && <p className="editor-form-helper text-danger">{errors.timeWindowStart}</p>}
                    </div>
                    <div className="editor-form-group">
                        <label className="editor-form-label">End Time *</label>
                        <input
                            className="editor-date-input"
                            type="datetime-local"
                            value={aircraft.timeWindow.end ? aircraft.timeWindow.end.replace('Z', '').slice(0, 16) : ''}
                            onChange={(e) => onChange('timeWindow', { ...aircraft.timeWindow, end: new Date(e.target.value).toISOString() })}
                            readOnly={isReadOnly}
                        />
                        {errors.timeWindowEnd && <p className="editor-form-helper text-danger">{errors.timeWindowEnd}</p>}
                    </div>
                </div>
            </div>

            {/* Tasks Section */}
            <div className="editor-card">
                <h3 className="editor-card-title">Tasks yêu cầu</h3>

                {!isReadOnly && (
                    <div className="editor-task-grid" style={{ marginTop: '1rem' }}>
                        <div className="editor-form-group">
                            <label className="editor-form-label">Chọn Task Code</label>
                            <div className="editor-form-select-wrapper">
                                <select
                                    className="editor-form-select"
                                    value={newTaskCode}
                                    onChange={(e) => {
                                        const code = e.target.value;
                                        setNewTaskCode(code);
                                        const t = taskMap?.get(code);
                                        if (t && t.defaultMinLevel) setNewMinLevel(t.defaultMinLevel);
                                    }}
                                >
                                    <option value="">-- Chọn Task --</option>
                                    {availableTaskCodes.map(code => (
                                        <option key={code} value={code}>{code}</option>
                                    ))}
                                </select>
                                <span className="material-symbols-outlined editor-form-select-icon">expand_more</span>
                            </div>
                        </div>

                        <div className="editor-form-group">
                            <label className="editor-form-label">Min Level</label>
                            <input
                                className="editor-form-input editor-task-level-input"
                                type="number"
                                value={newMinLevel}
                                onChange={(e) => setNewMinLevel(parseInt(e.target.value) || 1)}
                                min={1}
                            />
                        </div>

                        <button
                            className="editor-form-button-secondary"
                            onClick={handleAddTask}
                            disabled={!newTaskCode}
                            style={{ alignSelf: 'end' }}
                        >
                            Add
                        </button>
                    </div>
                )}

                <div className="editor-task-chips">
                    {aircraft.requiredTasks.length === 0 && <span className="editor-task-list-empty">Chưa có task nào</span>}
                    {aircraft.requiredTasks.map((task, index) => (
                        <div key={`${task.taskCode}-${index}`} className="editor-task-chip">
                            <span>{task.taskCode} {task.minLevel ? `(L${task.minLevel})` : ''}</span>
                            {!isReadOnly && (
                                <span className="editor-task-chip-remove" onClick={() => handleRemoveTask(index)}>×</span>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Actions */}
            <div style={{ marginTop: 'auto', marginBottom: '0.5rem' }}>
                {isReadOnly ? (
                    <button className="editor-form-button-primary" onClick={onStartEdit}>
                        <span className="material-symbols-outlined">edit</span> Update
                    </button>
                ) : (
                    <button
                        className="editor-form-button-primary"
                        onClick={handleSaveLocal}
                        disabled={!isFormValid()}
                        style={{ opacity: !isFormValid() ? 0.5 : 1 }}
                    >
                        <span className="material-symbols-outlined">save</span> {initialData ? 'Save Changes' : 'Add Aircraft'}
                    </button>
                )}
            </div>
        </div>
    );
};

export default AircraftInfoForm;
