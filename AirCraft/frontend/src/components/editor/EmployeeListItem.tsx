import React from 'react';
import type { Employee } from '@/types/employee';

interface EmployeeListItemProps {
    employee: Employee;
    isSelected?: boolean;
    onToggleSelect?: () => void;
    onEdit: () => void;
    onDelete: () => void;
}

const EmployeeListItem: React.FC<EmployeeListItemProps> = ({
    employee,
    isSelected = false,
    onToggleSelect,
    onEdit,
    onDelete,
}) => {
    const formatTime = (isoString: string) => {
        if (!isoString) return '';
        return new Date(isoString).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', hour12: false });
    };

    const formatDuration = (seconds?: number) => {
        if (!seconds) return 'Không';
        const minutes = Math.floor(seconds / 60);
        return `${minutes} phút`;
    };

    const getWorkingTimesSummary = () => {
        if (employee.workingTimes.length === 0) return 'Chưa cài đặt';
        if (employee.workingTimes.length === 1) {
            const wt = employee.workingTimes[0];
            return `${formatTime(wt.start)} - ${formatTime(wt.end)}`;
        }
        return `${employee.workingTimes.length} ca`;
    };

    const getFixedBreaksSummary = () => {
        if (!employee.fixedBreakTimes || employee.fixedBreakTimes.length === 0) return 'Không';
        return `${employee.fixedBreakTimes.length} khoảng`;
    };

    return (
        <div style={{
            marginBottom: '1rem',
            padding: '1rem',
            backgroundColor: isSelected ? 'rgba(59, 130, 246, 0.1)' : 'var(--color-surface)',
            border: isSelected ? '1px solid #3b82f6' : '1px solid var(--color-border)',
            borderRadius: '0.5rem',
        }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    {onToggleSelect && (
                        <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={onToggleSelect}
                            style={{ cursor: 'pointer', width: '18px', height: '18px' }}
                        />
                    )}
                    <span style={{ fontWeight: 700, fontSize: '1.125rem', color: 'var(--color-primary)' }}>
                        {employee.employeeId}
                    </span>
                    {employee.name && (
                        <span style={{ fontSize: '1rem', color: 'var(--color-text-primary)' }}>
                            {employee.name}
                        </span>
                    )}
                    {employee.position && (
                        <span style={{
                            fontSize: '0.75rem',
                            padding: '0.25rem 0.75rem',
                            background: 'var(--color-surface-hover)',
                            borderRadius: '9999px',
                            color: 'var(--color-text-secondary)'
                        }}>
                            {employee.position}
                        </span>
                    )}
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                        className="dataset-btn"
                        onClick={onEdit}
                        title="Edit"
                        style={{ padding: '0.5rem' }}
                    >
                        <span className="material-symbols-outlined">edit</span>
                    </button>
                    <button
                        className="dataset-btn danger"
                        onClick={(e) => {
                            e.stopPropagation();
                            if (window.confirm(`Xóa nhân viên ${employee.employeeId}?`)) {
                                onDelete();
                            }
                        }}
                        title="Delete"
                        style={{ padding: '0.5rem' }}
                    >
                        <span className="material-symbols-outlined">delete</span>
                    </button>
                </div>
            </div>

            {/* Details Grid */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(2, 1fr)',
                gap: '0.75rem',
                fontSize: '0.875rem'
            }}>
                {/* Role */}
                <div>
                    <span style={{ color: 'var(--color-text-secondary)' }}>Vai trò:</span>{' '}
                    <span style={{ color: 'var(--color-text-primary)', fontWeight: 500 }}>{employee.eType.role}</span>
                </div>

                {/* Working Times */}
                <div>
                    <span style={{ color: 'var(--color-text-secondary)' }}>Ca làm việc:</span>{' '}
                    <span style={{ color: 'var(--color-success)', fontWeight: 500 }}>{getWorkingTimesSummary()}</span>
                </div>

                {/* Break Duration */}
                <div>
                    <span style={{ color: 'var(--color-text-secondary)' }}>Lượng nghỉ cần sắp xếp:</span>{' '}
                    <span style={{ color: 'var(--color-text-primary)', fontWeight: 500 }}>
                        {formatDuration(employee.breakDuration)}
                    </span>
                </div>

                {/* Fixed Breaks */}
                <div>
                    <span style={{ color: 'var(--color-text-secondary)' }}>Nghỉ cố định:</span>{' '}
                    <span style={{ color: 'var(--color-text-primary)', fontWeight: 500 }}>
                        {getFixedBreaksSummary()}
                    </span>
                </div>
            </div>

            {/* Task Capabilities */}
            {employee.taskCapabilities && employee.taskCapabilities.length > 0 && (
                <div style={{ marginTop: '0.75rem' }}>
                    <span style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Năng lực: </span>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.375rem', marginTop: '0.25rem' }}>
                        {employee.taskCapabilities.map((task, idx) => (
                            <span
                                key={idx}
                                style={{
                                    fontSize: '0.75rem',
                                    padding: '0.25rem 0.625rem',
                                    borderRadius: '0.375rem',
                                    background: 'var(--color-primary-bg, rgba(59, 130, 246, 0.15))',
                                    color: 'var(--color-primary)',
                                    fontWeight: 500,
                                }}
                            >
                                {task}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {/* Certifications */}
            {employee.certifications && employee.certifications.length > 0 && (
                <div style={{ marginTop: '0.75rem' }}>
                    <span style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Chứng chỉ: </span>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.375rem', marginTop: '0.25rem' }}>
                        {employee.certifications.map((cert, idx) => (
                            <span
                                key={idx}
                                style={{
                                    fontSize: '0.75rem',
                                    padding: '0.25rem 0.625rem',
                                    borderRadius: '0.375rem',
                                    background: 'var(--color-warning-bg)',
                                    color: 'var(--color-warning)',
                                    fontWeight: 500,
                                }}
                            >
                                {cert}
                            </span>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default EmployeeListItem;
