import { useState, useEffect } from 'react';
import type { Employee, Role } from '@/types/employee';
import { ROLES } from '@/types/employee';
import { AVAILABLE_CERTIFICATIONS } from '@/types/certifications';
import { AVAILABLE_TASKS } from '@/types/tasks';
import './Editor.css';

interface EmployeeEditorProps {
  onSave?: (employee: Employee) => void;
  onDelete?: (employeeId: string) => void;
  onStartEdit?: () => void;
  initialData?: Employee | null;
  isEditing?: boolean;
}

const DEFAULT_EMPLOYEE: Employee = {
  employeeId: '',
  name: '',
  position: '',
  taskCapabilities: [],
  certifications: [],
  eType: { role: 'MECHANIC' },
  workingTimes: [{ start: '', end: '' }],
  breakDuration: 3600,
  fixedBreakTimes: [],
};

function EmployeeEditor({
  onSave,
  onDelete,
  onStartEdit,
  initialData,
  isEditing = false,
}: EmployeeEditorProps) {
  const [employee, setEmployee] = useState<Employee>(initialData || DEFAULT_EMPLOYEE);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    setEmployee(initialData || DEFAULT_EMPLOYEE);
  }, [initialData]);

  const isReadOnly = !!(initialData && !isEditing);

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!employee.employeeId.trim()) {
      newErrors.employeeId = 'Mã NV là bắt buộc';
    }
    if (employee.workingTimes.length === 0 || employee.workingTimes.some(wt => !wt.start || !wt.end)) {
      newErrors.workingTimes = 'Cần ít nhất một ca làm việc';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const isFormValid = (): boolean => {
    return (
      employee.employeeId.trim() !== '' &&
      employee.workingTimes.length > 0 &&
      employee.workingTimes.every(wt => wt.start && wt.end)
    );
  };

  const handleChange = (field: keyof Employee, value: unknown) => {
    setEmployee((prev) => ({ ...prev, [field]: value }));
  };

  const handleWorkingTimeChange = (index: number, field: 'start' | 'end', value: string) => {
    setEmployee((prev) => {
      const newWorkingTimes = [...prev.workingTimes];
      newWorkingTimes[index] = { ...newWorkingTimes[index], [field]: value };
      return { ...prev, workingTimes: newWorkingTimes };
    });
  };

  const handleAddWorkingTime = () => {
    setEmployee((prev) => ({
      ...prev,
      workingTimes: [...prev.workingTimes, { start: '', end: '' }],
    }));
  };

  const handleRemoveWorkingTime = (index: number) => {
    setEmployee((prev) => ({
      ...prev,
      workingTimes: prev.workingTimes.filter((_, i) => i !== index),
    }));
  };

  const handleSave = () => {
    if (validateForm() && onSave) {
      onSave(employee);
    }
  };

  const handleDelete = () => {
    if (onDelete && employee.employeeId) {
      onDelete(employee.employeeId);
    }
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
      {/* CỘT TRÁI */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {/* Thông tin cơ bản */}
        <div className="editor-card">
          <h3 className="editor-card-title">Thông tin cơ bản</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginTop: '0.75rem' }}>
            <div className="editor-form-group">
              <label className="editor-form-label">Mã NV *</label>
              <input
                className="editor-form-input"
                type="text"
                value={employee.employeeId}
                onChange={(e) => {
                  handleChange('employeeId', e.target.value);
                  if (errors.employeeId) setErrors((p) => ({ ...p, employeeId: '' }));
                }}
                placeholder="VD: NV001"
                readOnly={isReadOnly}
                style={errors.employeeId ? { borderColor: 'var(--color-danger)' } : {}}
              />
              {errors.employeeId && <p className="editor-form-helper text-danger">{errors.employeeId}</p>}
            </div>
            <div className="editor-form-group">
              <label className="editor-form-label">Tên NV</label>
              <input
                className="editor-form-input"
                type="text"
                value={employee.name || ''}
                onChange={(e) => handleChange('name', e.target.value)}
                placeholder="Nguyễn Văn A"
                readOnly={isReadOnly}
              />
            </div>
            <div className="editor-form-group">
              <label className="editor-form-label">Chức danh</label>
              <input
                className="editor-form-input"
                type="text"
                value={employee.position || ''}
                onChange={(e) => handleChange('position', e.target.value)}
                placeholder="Kỹ thuật viên"
                readOnly={isReadOnly}
              />
            </div>
            <div className="editor-form-group">
              <label className="editor-form-label">Vai trò</label>
              <div className="editor-form-select-wrapper">
                <select
                  className="editor-form-select"
                  value={employee.eType.role}
                  onChange={(e) => handleChange('eType', { role: e.target.value as Role })}
                  disabled={isReadOnly}
                >
                  {ROLES.map((role) => (
                    <option key={role} value={role}>{role}</option>
                  ))}
                </select>
                <span className="material-symbols-outlined editor-form-select-icon">expand_more</span>
              </div>
            </div>
          </div>
        </div>

        {/* Năng lực */}
        <div className="editor-card">
          <h3 className="editor-card-title">Năng lực (Tasks)</h3>
          <p className="editor-card-description">Chọn các task nhân viên có thể thực hiện</p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem', marginTop: '0.75rem', maxHeight: '180px', overflowY: 'auto' }}>
            {AVAILABLE_TASKS.map(task => (
              <label
                key={task}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.375rem 0.5rem',
                  border: '1px solid var(--color-border)',
                  borderRadius: '0.25rem',
                  cursor: isReadOnly ? 'not-allowed' : 'pointer',
                  background: (employee.taskCapabilities || []).includes(task) ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                  fontSize: '0.8rem',
                }}
              >
                <input
                  type="checkbox"
                  checked={(employee.taskCapabilities || []).includes(task)}
                  onChange={(e) => {
                    if (isReadOnly) return;
                    const caps = employee.taskCapabilities || [];
                    if (e.target.checked) {
                      handleChange('taskCapabilities', [...caps, task]);
                    } else {
                      handleChange('taskCapabilities', caps.filter(c => c !== task));
                    }
                  }}
                  disabled={isReadOnly}
                />
                {task}
              </label>
            ))}
          </div>
        </div>

        {/* Ca làm việc */}
        <div className="editor-card">
          <h3 className="editor-card-title">Ca làm việc *</h3>
          <div style={{ marginTop: '0.75rem' }}>
            {employee.workingTimes.map((wt, index) => (
              <div key={index} style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem', alignItems: 'end' }}>
                <div className="editor-form-group" style={{ flex: 1 }}>
                  <label className="editor-form-label">Bắt đầu</label>
                  <input
                    className="editor-form-input"
                    type="datetime-local"
                    value={wt.start.replace('Z', '').slice(0, 16)}
                    onChange={(e) => handleWorkingTimeChange(index, 'start', new Date(e.target.value).toISOString())}
                    readOnly={isReadOnly}
                  />
                </div>
                <div className="editor-form-group" style={{ flex: 1 }}>
                  <label className="editor-form-label">Kết thúc</label>
                  <input
                    className="editor-form-input"
                    type="datetime-local"
                    value={wt.end.replace('Z', '').slice(0, 16)}
                    onChange={(e) => handleWorkingTimeChange(index, 'end', new Date(e.target.value).toISOString())}
                    readOnly={isReadOnly}
                  />
                </div>
                <button
                  className="editor-form-button-secondary text-danger"
                  onClick={() => handleRemoveWorkingTime(index)}
                  disabled={employee.workingTimes.length === 1 || isReadOnly}
                  type="button"
                  style={{ padding: '0.5rem', minWidth: 'auto' }}
                >
                  <span className="material-symbols-outlined">delete</span>
                </button>
              </div>
            ))}
            {!isReadOnly && (
              <button className="editor-form-button-secondary" onClick={handleAddWorkingTime} type="button" style={{ marginTop: '0.25rem' }}>
                <span className="material-symbols-outlined">add</span> Thêm ca
              </button>
            )}
            {errors.workingTimes && <p className="editor-form-helper text-danger">{errors.workingTimes}</p>}
          </div>
        </div>
      </div>

      {/* CỘT PHẢI */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {/* Chứng chỉ */}
        <div className="editor-card">
          <h3 className="editor-card-title">Chứng chỉ</h3>
          <p className="editor-card-description">Chọn các chứng chỉ nhân viên sở hữu</p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem', marginTop: '0.75rem', maxHeight: '200px', overflowY: 'auto' }}>
            {AVAILABLE_CERTIFICATIONS.map(cert => (
              <label
                key={cert}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.375rem 0.5rem',
                  border: '1px solid var(--color-border)',
                  borderRadius: '0.25rem',
                  cursor: isReadOnly ? 'not-allowed' : 'pointer',
                  background: (employee.certifications || []).includes(cert) ? 'rgba(16, 185, 129, 0.1)' : 'transparent',
                  fontSize: '0.8rem',
                }}
              >
                <input
                  type="checkbox"
                  checked={(employee.certifications || []).includes(cert)}
                  onChange={(e) => {
                    if (isReadOnly) return;
                    const certs = employee.certifications || [];
                    if (e.target.checked) {
                      handleChange('certifications', [...certs, cert]);
                    } else {
                      handleChange('certifications', certs.filter(c => c !== cert));
                    }
                  }}
                  disabled={isReadOnly}
                />
                {cert}
              </label>
            ))}
          </div>
        </div>

        {/* Thời gian nghỉ */}
        <div className="editor-card">
          <h3 className="editor-card-title">Thời gian nghỉ</h3>
          <div className="editor-form-group" style={{ marginTop: '0.75rem' }}>
            <label className="editor-form-label">Thời lượng nghỉ (phút)</label>
            <input
              className="editor-form-input"
              type="number"
              value={Math.round((employee.breakDuration || 0) / 60)}
              onChange={(e) => handleChange('breakDuration', (parseInt(e.target.value) || 0) * 60)}
              min={0}
              readOnly={isReadOnly}
              style={{ maxWidth: '120px' }}
            />
            <p className="editor-form-helper">Tổng thời gian nghỉ trong ca</p>
          </div>
        </div>

        {/* Nút hành động */}
        <div style={{ marginTop: 'auto' }}>
          {isReadOnly ? (
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button className="editor-form-button-primary" onClick={onStartEdit}>
                <span className="material-symbols-outlined">edit</span> Chỉnh sửa
              </button>
              {onDelete && (
                <button
                  className="editor-form-button-secondary text-danger"
                  onClick={handleDelete}
                  style={{ borderColor: 'var(--color-danger)' }}
                >
                  <span className="material-symbols-outlined">delete</span> Xóa
                </button>
              )}
            </div>
          ) : (
            <button
              className="editor-form-button-primary"
              onClick={handleSave}
              disabled={!isFormValid()}
              style={{ opacity: !isFormValid() ? 0.5 : 1, cursor: !isFormValid() ? 'not-allowed' : 'pointer' }}
            >
              <span className="material-symbols-outlined">save</span>
              {initialData ? 'Lưu thay đổi' : 'Thêm nhân viên'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default EmployeeEditor;
