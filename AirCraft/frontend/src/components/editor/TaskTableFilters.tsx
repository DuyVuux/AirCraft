import React, { useState, useRef, useEffect } from 'react';
import type { TaskFilters } from '@/hooks/useTaskFilter';
import { AVAILABLE_CERTIFICATIONS } from '@/types/certifications';
import './TaskTableFilters.css';

interface TaskTableFiltersProps {
    filters: TaskFilters;
    onFilterChange: <K extends keyof TaskFilters>(key: K, value: TaskFilters[K]) => void;
    onClearFilters: () => void;
    hasActiveFilters: boolean;
    activeFilterCount: number;
    filteredCount: number;
    totalCount: number;
}

export function TaskTableFilters({
    filters,
    onFilterChange,
    onClearFilters,
    hasActiveFilters,
    activeFilterCount,
    filteredCount,
    totalCount,
}: TaskTableFiltersProps) {
    const [showCertDropdown, setShowCertDropdown] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setShowCertDropdown(false);
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleCertToggle = (cert: string) => {
        const current = filters.certifications;
        if (current.includes(cert)) {
            onFilterChange('certifications', current.filter(c => c !== cert));
        } else {
            onFilterChange('certifications', [...current, cert]);
        }
    };

    const clearCertifications = () => {
        onFilterChange('certifications', []);
    };

    return (
        <div className="task-filter-container">
            <div className="task-filter-header">
                <div className="task-filter-info">
                    <span className="task-filter-count">
                        Hiển thị {filteredCount} / {totalCount} tasks
                    </span>
                    {hasActiveFilters && (
                        <span className="task-filter-badge">{activeFilterCount} bộ lọc</span>
                    )}
                </div>
                {hasActiveFilters && (
                    <button
                        type="button"
                        className="task-filter-clear-btn"
                        onClick={onClearFilters}
                    >
                        <span className="material-symbols-outlined">filter_alt_off</span>
                        Xóa bộ lọc
                    </button>
                )}
            </div>

            <div className="task-filter-row">
                <div className="task-filter-group">
                    <label className="task-filter-label">Mã Task</label>
                    <div className="task-filter-input-wrapper">
                        <span className="material-symbols-outlined task-filter-icon">search</span>
                        <input
                            type="text"
                            className="task-filter-input"
                            placeholder="Tìm theo mã..."
                            value={filters.taskCode}
                            onChange={e => onFilterChange('taskCode', e.target.value)}
                        />
                        {filters.taskCode && (
                            <button
                                type="button"
                                className="task-filter-input-clear"
                                onClick={() => onFilterChange('taskCode', '')}
                            >
                                <span className="material-symbols-outlined">close</span>
                            </button>
                        )}
                    </div>
                </div>

                <div className="task-filter-group">
                    <label className="task-filter-label">Mô tả</label>
                    <div className="task-filter-input-wrapper">
                        <span className="material-symbols-outlined task-filter-icon">search</span>
                        <input
                            type="text"
                            className="task-filter-input"
                            placeholder="Tìm theo mô tả..."
                            value={filters.description}
                            onChange={e => onFilterChange('description', e.target.value)}
                        />
                        {filters.description && (
                            <button
                                type="button"
                                className="task-filter-input-clear"
                                onClick={() => onFilterChange('description', '')}
                            >
                                <span className="material-symbols-outlined">close</span>
                            </button>
                        )}
                    </div>
                </div>

                <div className="task-filter-group task-filter-group-time">
                    <label className="task-filter-label">Thời gian (phút)</label>
                    <div className="task-filter-range">
                        <input
                            type="number"
                            className="task-filter-input task-filter-input-small"
                            placeholder="Min"
                            min={0}
                            value={filters.timeMin ?? ''}
                            onChange={e => {
                                const val = e.target.value === '' ? null : Number(e.target.value);
                                onFilterChange('timeMin', val);
                            }}
                        />
                        <span className="task-filter-range-separator">—</span>
                        <input
                            type="number"
                            className="task-filter-input task-filter-input-small"
                            placeholder="Max"
                            min={0}
                            value={filters.timeMax ?? ''}
                            onChange={e => {
                                const val = e.target.value === '' ? null : Number(e.target.value);
                                onFilterChange('timeMax', val);
                            }}
                        />
                    </div>
                </div>

                <div className="task-filter-group" ref={dropdownRef}>
                    <label className="task-filter-label">Yêu cầu chứng chỉ</label>
                    <button
                        type="button"
                        className={`task-filter-dropdown-btn ${filters.certifications.length > 0 ? 'active' : ''}`}
                        onClick={() => setShowCertDropdown(!showCertDropdown)}
                    >
                        <span className="task-filter-dropdown-text">
                            {filters.certifications.length > 0
                                ? `${filters.certifications.length} đã chọn`
                                : 'Chọn chứng chỉ...'}
                        </span>
                        <span className="material-symbols-outlined">
                            {showCertDropdown ? 'expand_less' : 'expand_more'}
                        </span>
                    </button>

                    {showCertDropdown && (
                        <div className="task-filter-dropdown-menu">
                            <div className="task-filter-dropdown-header">
                                <span>Chọn chứng chỉ</span>
                                {filters.certifications.length > 0 && (
                                    <button
                                        type="button"
                                        className="task-filter-dropdown-clear"
                                        onClick={clearCertifications}
                                    >
                                        Bỏ chọn tất cả
                                    </button>
                                )}
                            </div>
                            <div className="task-filter-dropdown-list">
                                {AVAILABLE_CERTIFICATIONS.map(cert => (
                                    <label key={cert} className="task-filter-dropdown-item">
                                        <input
                                            type="checkbox"
                                            checked={filters.certifications.includes(cert)}
                                            onChange={() => handleCertToggle(cert)}
                                        />
                                        <span>{cert}</span>
                                    </label>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default TaskTableFilters;
