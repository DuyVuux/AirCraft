import React, { useState, useRef, useEffect } from 'react';
import type { EmployeeFilters } from '@/hooks/useEmployeeFilter';
import { ROLES } from '@/types/employee';
import { AVAILABLE_TASKS } from '@/types/tasks';
import { AVAILABLE_CERTIFICATIONS } from '@/types/certifications';
import './EmployeeTableFilters.css';

interface EmployeeTableFiltersProps {
    filters: EmployeeFilters;
    onFilterChange: <K extends keyof EmployeeFilters>(key: K, value: EmployeeFilters[K]) => void;
    onClearFilters: () => void;
    hasActiveFilters: boolean;
    activeFilterCount: number;
    filteredCount: number;
    totalCount: number;
}

export function EmployeeTableFilters({
    filters,
    onFilterChange,
    onClearFilters,
    hasActiveFilters,
    activeFilterCount,
    filteredCount,
    totalCount,
}: EmployeeTableFiltersProps) {
    const [showCapsDropdown, setShowCapsDropdown] = useState(false);
    const [showCertsDropdown, setShowCertsDropdown] = useState(false);

    const capsDropdownRef = useRef<HTMLDivElement>(null);
    const certsDropdownRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (capsDropdownRef.current && !capsDropdownRef.current.contains(event.target as Node)) {
                setShowCapsDropdown(false);
            }
            if (certsDropdownRef.current && !certsDropdownRef.current.contains(event.target as Node)) {
                setShowCertsDropdown(false);
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleCapToggle = (cap: string) => {
        const current = filters.capabilities;
        if (current.includes(cap)) {
            onFilterChange('capabilities', current.filter(c => c !== cap));
        } else {
            onFilterChange('capabilities', [...current, cap]);
        }
    };

    const handleCertToggle = (cert: string) => {
        const current = filters.certifications;
        if (current.includes(cert)) {
            onFilterChange('certifications', current.filter(c => c !== cert));
        } else {
            onFilterChange('certifications', [...current, cert]);
        }
    };

    return (
        <div className="employee-filter-container">
            <div className="employee-filter-header">
                <div className="employee-filter-info">
                    <span className="employee-filter-count">
                        Hiển thị {filteredCount} / {totalCount} nhân viên
                    </span>
                    {hasActiveFilters && (
                        <span className="employee-filter-badge">{activeFilterCount} bộ lọc</span>
                    )}
                </div>
                {hasActiveFilters && (
                    <button
                        type="button"
                        className="employee-filter-clear-btn"
                        onClick={onClearFilters}
                    >
                        <span className="material-symbols-outlined">filter_alt_off</span>
                        Xóa bộ lọc
                    </button>
                )}
            </div>

            <div className="employee-filter-row">
                {/* Search Text */}
                <div className="employee-filter-group">
                    <label className="employee-filter-label">Tìm kiếm (ID/Tên)</label>
                    <div className="employee-filter-input-wrapper">
                        <span className="material-symbols-outlined employee-filter-icon">search</span>
                        <input
                            type="text"
                            className="employee-filter-input"
                            placeholder="Nhập ID hoặc tên..."
                            value={filters.searchText}
                            onChange={e => onFilterChange('searchText', e.target.value)}
                        />
                        {filters.searchText && (
                            <button
                                type="button"
                                className="employee-filter-input-clear"
                                onClick={() => onFilterChange('searchText', '')}
                            >
                                <span className="material-symbols-outlined">close</span>
                            </button>
                        )}
                    </div>
                </div>

                {/* Role Select */}
                <div className="employee-filter-group">
                    <label className="employee-filter-label">Vai trò</label>
                    <div className="employee-filter-input-wrapper">
                        <select
                            className="employee-filter-select"
                            value={filters.role}
                            onChange={e => onFilterChange('role', e.target.value as any)}
                        >
                            <option value="ALL">Tất cả vai trò</option>
                            {ROLES.map(role => (
                                <option key={role} value={role}>{role}</option>
                            ))}
                        </select>
                        <span className="material-symbols-outlined employee-filter-icon" style={{ right: '0.625rem', left: 'auto' }}>expand_more</span>
                    </div>
                </div>

                {/* Capabilities Dropdown */}
                <div className="employee-filter-group" ref={capsDropdownRef}>
                    <label className="employee-filter-label">Năng lực (Tasks)</label>
                    <button
                        type="button"
                        className={`employee-filter-dropdown-btn ${filters.capabilities.length > 0 ? 'active' : ''}`}
                        onClick={() => setShowCapsDropdown(!showCapsDropdown)}
                    >
                        <span className="employee-filter-dropdown-text">
                            {filters.capabilities.length > 0
                                ? `${filters.capabilities.length} đã chọn`
                                : 'Chọn năng lực...'}
                        </span>
                        <span className="material-symbols-outlined">
                            {showCapsDropdown ? 'expand_less' : 'expand_more'}
                        </span>
                    </button>

                    {showCapsDropdown && (
                        <div className="employee-filter-dropdown-menu">
                            <div className="employee-filter-dropdown-header">
                                <span>Chọn tasks</span>
                                {filters.capabilities.length > 0 && (
                                    <button
                                        type="button"
                                        className="employee-filter-dropdown-clear"
                                        onClick={() => onFilterChange('capabilities', [])}
                                    >
                                        Bỏ chọn tất cả
                                    </button>
                                )}
                            </div>
                            <div className="employee-filter-dropdown-list">
                                {AVAILABLE_TASKS.map(task => (
                                    <label key={task} className="employee-filter-dropdown-item">
                                        <input
                                            type="checkbox"
                                            checked={filters.capabilities.includes(task)}
                                            onChange={() => handleCapToggle(task)}
                                        />
                                        <span>{task}</span>
                                    </label>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                {/* Certifications Dropdown */}
                <div className="employee-filter-group" ref={certsDropdownRef}>
                    <label className="employee-filter-label">Chứng chỉ</label>
                    <button
                        type="button"
                        className={`employee-filter-dropdown-btn ${filters.certifications.length > 0 ? 'active' : ''}`}
                        onClick={() => setShowCertsDropdown(!showCertsDropdown)}
                    >
                        <span className="employee-filter-dropdown-text">
                            {filters.certifications.length > 0
                                ? `${filters.certifications.length} đã chọn`
                                : 'Chọn chứng chỉ...'}
                        </span>
                        <span className="material-symbols-outlined">
                            {showCertsDropdown ? 'expand_less' : 'expand_more'}
                        </span>
                    </button>

                    {showCertsDropdown && (
                        <div className="employee-filter-dropdown-menu">
                            <div className="employee-filter-dropdown-header">
                                <span>Chọn chứng chỉ</span>
                                {filters.certifications.length > 0 && (
                                    <button
                                        type="button"
                                        className="employee-filter-dropdown-clear"
                                        onClick={() => onFilterChange('certifications', [])}
                                    >
                                        Bỏ chọn tất cả
                                    </button>
                                )}
                            </div>
                            <div className="employee-filter-dropdown-list">
                                {AVAILABLE_CERTIFICATIONS.map(cert => (
                                    <label key={cert} className="employee-filter-dropdown-item">
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

                {/* Shift Time Range */}
                <div className="employee-filter-group">
                    <label className="employee-filter-label">Ca làm việc (Bắt đầu)</label>
                    <div className="employee-filter-range">
                        <input
                            type="time"
                            className="employee-filter-input employee-filter-input-small"
                            value={filters.shiftStart}
                            onChange={e => onFilterChange('shiftStart', e.target.value)}
                        />
                        <span className="employee-filter-range-separator">—</span>
                        <input
                            type="time"
                            className="employee-filter-input employee-filter-input-small"
                            value={filters.shiftEnd}
                            onChange={e => onFilterChange('shiftEnd', e.target.value)}
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}

export default EmployeeTableFilters;
