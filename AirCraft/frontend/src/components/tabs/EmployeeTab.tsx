import type { TabProps, TabConfig } from './types';
import EmployeeEditor from '@/components/editor/EmployeeEditor';
import EmployeeListItem from '@/components/editor/EmployeeListItem';
import UploadButton from '@/components/upload/UploadButton';
import type { ParseResult } from '@/services/csvParser';
import { downloadTemplate } from '@/services/csvParser';
import type { Employee } from '@/types/employee';
import { useState, useEffect } from 'react';
import useEmployeeFilter from '@/hooks/useEmployeeFilter';
import EmployeeTableFilters from '@/components/editor/EmployeeTableFilters';

export const tabConfig: TabConfig = {
    id: 'employees',
    label: 'EMPLOYEES',
    order: 1,
};

const EMPLOYEE_TEMPLATE_HEADERS = [
    'Mã NV',
    'Tên NV',
    'Chức Danh',
    'Vai trò',
    'Ca làm (start)',
    'Ca làm (end)',
    'Lượng nghỉ (phút)',
    'Nghỉ cố định (start;end hoặc nhiều khoảng cách nhau bởi |)',
    'Năng Lực (Tasks)',
    'Chứng Chỉ',
];

const EMPLOYEE_SAMPLE_ROWS = [
    ['NV001', 'Nguyễn Văn A', 'Kỹ sư', 'MECHANIC', '2026-01-02T06:00:00Z', '2026-01-02T14:00:00Z', '60', '2026-01-02T12:00:00Z;2026-01-02T13:00:00Z', 'ARR-M,DEP-M,WO-01', 'A320,B787'],
    ['NV002', 'Trần Thị B', 'Nhân viên', 'CLEANER', '2026-01-02T07:00:00Z', '2026-01-02T15:00:00Z', '30', '', 'WO-05', ''],
];

export default function EmployeeTab({
    employees,
    setEmployees,
    editingEmployeeId,
    setEditingEmployeeId,
    handleEmployeeSave,
    handleEmployeeDelete,
}: TabProps) {
    const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

    const {
        filters,
        updateFilter,
        clearFilters,
        hasActiveFilters,
        activeFilterCount,
        filteredEmployees,
        totalCount,
        filteredCount,
    } = useEmployeeFilter(employees);

    // Cleanup selectedIds when employees OR filters change to ensure valid selection
    useEffect(() => {
        // When filters change, we might want to keep selection if the item is still visible?
        // Or clear selection to avoid confusion? 
        // TaskList cleared it. Let's keep consistent and clear it, or at least validate it against filtered list?
        // TaskList logic: useEffect(() => setSelectedIds(new Set()), [filters]);
        // Let's do the same for simplicity and avoiding hidden selections.
        setSelectedIds(new Set());
    }, [filters]);

    // Cleanup selectedIds when employees change
    useEffect(() => {
        const validIds = new Set(employees.map(e => e.employeeId));
        setSelectedIds(prev => {
            const cleaned = new Set<string>();
            prev.forEach(id => {
                if (validIds.has(id)) {
                    cleaned.add(id);
                }
            });
            // Only update if there were invalid IDs
            return cleaned.size !== prev.size ? cleaned : prev;
        });
    }, [employees]);

    const handleUpload = (result: ParseResult) => {
        if (result.errors.length > 0) {
            console.error('Upload errors:', result.errors);
            return;
        }

        if (result.warnings && result.warnings.length > 0) {
            console.warn('Upload warnings:', result.warnings);
            alert(`⚠️ Cảnh báo trùng lặp:\n${result.warnings.join('\n')}`);
        }

        const newEmployees: Employee[] = result.rows.map((row) => {
            const breakMinutes = parseInt(row['Lượng nghỉ (phút)'] || '0');
            const tasksString = row['Năng Lực (Tasks)'] || '';
            const certsString = row['Chứng Chỉ'] || row['Chứng Chỉ (Certs)'] || '';
            const fixedBreaksString = row['Nghỉ cố định (start;end hoặc nhiều khoảng cách nhau bởi |)'] || '';

            const tasks = tasksString ? tasksString.split(',').map(t => t.trim()).filter(t => t) : [];
            const certs = certsString ? certsString.split(',').map(c => c.trim()).filter(c => c) : [];

            const fixedBreakTimes = fixedBreaksString
                ? fixedBreaksString.split('|').map(pair => {
                    const [start, end] = pair.split(';');
                    return { start: start.trim(), end: end.trim() };
                }).filter(b => b.start && b.end)
                : [];

            return {
                employeeId: row['Mã NV'] || '',
                name: row['Tên NV'] || undefined,
                position: row['Chức Danh'] || undefined,
                eType: { role: (row['Vai trò'] as any) || 'MECHANIC' },
                workingTimes: [
                    {
                        start: row['Ca làm (start)'] || new Date().toISOString(),
                        end: row['Ca làm (end)'] || new Date(Date.now() + 8 * 3600 * 1000).toISOString(),
                    },
                ],
                breakDuration: breakMinutes * 60,
                fixedBreakTimes,
                taskCapabilities: tasks.length > 0 ? tasks : undefined,
                certifications: certs.length > 0 ? certs : undefined,
            };
        });

        const existingIds = new Set(employees.map(e => e.employeeId));
        const uniqueEmployees = newEmployees.filter(e => !existingIds.has(e.employeeId));
        setEmployees([...employees, ...uniqueEmployees]);
    };

    const handleToggleSelect = (id: string) => {
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
        if (selectedIds.size === filteredEmployees.length) {
            setSelectedIds(new Set());
        } else {
            const allIds = filteredEmployees.map(e => e.employeeId);
            setSelectedIds(new Set(allIds));
        }
    };

    const handleBulkDelete = () => {
        if (selectedIds.size === 0) return;
        if (window.confirm(`Xóa ${selectedIds.size} nhân viên?`)) {
            selectedIds.forEach(id => handleEmployeeDelete(id));
            setSelectedIds(new Set());
        }
    };

    const handleDownload = () => {
        const rows = employees.map(emp => [
            emp.employeeId,
            emp.name || '',
            emp.position || '',
            emp.eType.role,
            emp.workingTimes[0]?.start || '',
            emp.workingTimes[0]?.end || '',
            String(Math.round((emp.breakDuration || 0) / 60)),
            emp.fixedBreakTimes?.map(b => `${b.start};${b.end}`).join('|') || '',
            emp.taskCapabilities?.join(',') || '',
            emp.certifications?.join(',') || '',
        ]);
        downloadTemplate('employees_export.csv', EMPLOYEE_TEMPLATE_HEADERS, rows);
    };

    const allSelected = selectedIds.size === filteredEmployees.length && filteredEmployees.length > 0;

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflowY: 'auto', paddingRight: '0.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexShrink: 0 }}>
                <h3 style={{ margin: 0 }}>Quản lý Nhân viên</h3>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                        onClick={handleDownload}
                        disabled={employees.length === 0}
                        className="dataset-btn"
                        style={{
                            opacity: employees.length === 0 ? 0.5 : 1,
                            cursor: employees.length === 0 ? 'not-allowed' : 'pointer'
                        }}
                    >
                        <span className="material-symbols-outlined">download</span>
                        Download CSV ({employees.length})
                    </button>
                    <UploadButton
                        label="Upload Employees"
                        templateHeaders={EMPLOYEE_TEMPLATE_HEADERS}
                        templateFilename="employees_template.csv"
                        sampleRows={EMPLOYEE_SAMPLE_ROWS}
                        onDataParsed={handleUpload}
                        duplicateKeyField="Mã NV"
                    />
                </div>
            </div>

            {(!employees.length || editingEmployeeId === 'new' || (editingEmployeeId && editingEmployeeId !== 'new')) && (
                <div className="layout-form-card" style={{ marginBottom: '1.5rem', flexShrink: 0 }}>
                    <h3 className="layout-form-card-title">
                        {editingEmployeeId && editingEmployeeId !== 'new' ? `Edit Employee: ${editingEmployeeId}` : 'Add New Employee'}
                    </h3>
                    {editingEmployeeId && (
                        <button
                            onClick={() => setEditingEmployeeId(null)}
                            style={{ marginBottom: '1rem', background: 'none', border: 'none', color: 'var(--color-primary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.25rem' }}
                        >
                            <span className="material-symbols-outlined">arrow_back</span>
                            {editingEmployeeId === 'new' ? 'Hủy thêm mới' : 'Cancel Editing'}
                        </button>
                    )}
                    <EmployeeEditor
                        onSave={(emp) => {
                            handleEmployeeSave(emp);
                            setEditingEmployeeId(null);
                        }}
                        onDelete={handleEmployeeDelete}
                        initialData={editingEmployeeId && editingEmployeeId !== 'new' ? employees.find(e => e.employeeId === editingEmployeeId) : undefined}
                    />
                </div>
            )}

            {employees.length > 0 && !editingEmployeeId && (
                <div className="layout-form-card" style={{ marginTop: '1.5rem', flex: 1, display: 'flex', flexDirection: 'column' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexShrink: 0 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                            {employees.length > 0 && (
                                <label style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '0.5rem',
                                    fontSize: '0.875rem',
                                    fontWeight: 500,
                                    cursor: 'pointer',
                                    padding: '0.5rem 0.75rem',
                                    background: 'var(--color-surface-hover)',
                                    borderRadius: '0.375rem',
                                }}>
                                    <input
                                        type="checkbox"
                                        checked={allSelected}
                                        onChange={handleSelectAll}
                                        style={{ cursor: 'pointer', width: '16px', height: '16px' }}
                                    />
                                    Chọn tất cả ({selectedIds.size}/{filteredEmployees.length})
                                </label>
                            )}
                            <h3 className="layout-form-card-title" style={{ margin: 0 }}>Employees List</h3>
                        </div>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                            {selectedIds.size > 0 && (
                                <button
                                    className="dataset-btn danger"
                                    onClick={handleBulkDelete}
                                >
                                    Xóa {selectedIds.size} nhân viên
                                </button>
                            )}
                            <button
                                className="dataset-btn primary"
                                onClick={() => setEditingEmployeeId('new')}
                            >
                                <span className="material-symbols-outlined">add</span>
                                Add Employee
                            </button>
                        </div>
                    </div>

                    <div style={{ flexShrink: 0 }}>
                        <EmployeeTableFilters
                            filters={filters}
                            onFilterChange={updateFilter}
                            onClearFilters={clearFilters}
                            hasActiveFilters={hasActiveFilters}
                            activeFilterCount={activeFilterCount}
                            filteredCount={filteredCount}
                            totalCount={totalCount}
                        />
                    </div>

                    <div style={{ flex: 1, overflowY: 'auto' }}>
                        {filteredEmployees.length === 0 ? (
                            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--color-text-secondary)', background: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
                                Không tìm thấy nhân viên phù hợp với bộ lọc hiện tại.
                            </div>
                        ) : (
                            filteredEmployees.map((employee) => (
                                <EmployeeListItem
                                    key={employee.employeeId}
                                    employee={employee}
                                    isSelected={selectedIds.has(employee.employeeId)}
                                    onToggleSelect={() => handleToggleSelect(employee.employeeId)}
                                    onEdit={() => setEditingEmployeeId(employee.employeeId)}
                                    onDelete={() => handleEmployeeDelete(employee.employeeId)}
                                />
                            )))}
                    </div>
                </div>
            )}
        </div>
    );
}
