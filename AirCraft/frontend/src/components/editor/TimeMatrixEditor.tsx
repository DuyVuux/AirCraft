import React, { useState } from 'react';
import type { TimeMatrixEntry } from '@/types/matrix';
import { ROLES } from '@/types/employee';
import './Editor.css';

interface TimeMatrixEditorProps {
  onSave?: (entry: TimeMatrixEntry) => void;
  onDelete?: (index: number) => void;
  onStartEdit?: () => void;
  initialData?: TimeMatrixEntry | null;
  isEditing?: boolean;
  availableAircraftIds?: string[];
  availableTaskCodes?: string[];
}

const TimeMatrixEditor: React.FC<TimeMatrixEditorProps> = ({
  onSave,
  onDelete,
  onStartEdit,
  initialData,
  isEditing = false,
  availableAircraftIds = [],
  availableTaskCodes = [],
}) => {
  const [entry, setEntry] = useState<TimeMatrixEntry>(
    initialData || {
      taskCode: '',
      role: '',
      level: 1,
      aircraftId: '',
      timeProcess: 0,
    }
  );
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Determine if fields should be read-only
  const isReadOnly = !!(initialData && !isEditing);

  // Validation function
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!entry.taskCode.trim()) {
      newErrors.taskCode = 'Task Code là bắt buộc';
    }

    if (!entry.role.trim()) {
      newErrors.role = 'Role là bắt buộc';
    }

    if (!entry.timeProcess || entry.timeProcess <= 0) {
      newErrors.timeProcess = 'Time Process phải lớn hơn 0';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Check if form is valid
  const isFormValid = (): boolean => {
    return (
      entry.taskCode.trim() !== '' &&
      entry.role.trim() !== '' &&
      entry.timeProcess > 0
    );
  };

  const handleChange = (field: keyof TimeMatrixEntry, value: any) => {
    setEntry((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = () => {
    if (!validateForm()) {
      return;
    }
    onSave?.(entry);
    // Reset form after save
    if (!initialData) {
      setEntry({
        taskCode: '',
        role: '',
        level: 1,
        aircraftId: '',
        timeProcess: 0,
      });
      setErrors({});
    }
  };

  const handleDelete = () => {
    if (window.confirm('Bạn có chắc chắn muốn xóa time matrix entry này không?')) {
      if (initialData && onDelete) {
        onDelete(0); // Index will be handled by parent
      }
    }
  };

  return (
    <>
      {isReadOnly && (
        <div className="editor-readonly-banner">
          <span className="material-symbols-outlined">lock</span>
          Chế độ chỉ đọc — Nhấn "Update" để chỉnh sửa
        </div>
      )}

      {/* Add New Time Matrix Entry */}
      <div className="editor-card">
        <h3 className="editor-card-title">{initialData ? 'Edit Time Matrix Entry' : 'Add New Time Matrix Entry'}</h3>
        <div className="editor-form-grid">
          <div className="editor-form-group">
            <label className="editor-form-label" htmlFor="task-code">
              Task Code *
            </label>
            <input
              className="editor-form-input"
              id="task-code"
              type="text"
              value={entry.taskCode}
              onChange={(e) => {
                handleChange('taskCode', e.target.value);
                if (errors.taskCode) {
                  setErrors((prev) => ({ ...prev, taskCode: '' }));
                }
              }}
              placeholder="TASK_TIRE_CHECK hoặc chọn từ danh sách"
              required
              readOnly={isReadOnly}
              style={errors.taskCode ? { borderColor: 'var(--color-danger)' } : {}}
              list="task-codes-list"
            />
            <datalist id="task-codes-list">
              {availableTaskCodes.map((code) => (
                <option key={code} value={code} />
              ))}
            </datalist>
            {errors.taskCode && (
              <p className="editor-form-helper text-danger" style={{ marginTop: '0.25rem' }}>
                {errors.taskCode}
              </p>
            )}
          </div>

          <div className="editor-form-group">
            <label className="editor-form-label" htmlFor="role">
              Role *
            </label>
            <div className="editor-form-select-wrapper">
              <select
                className="editor-form-select"
                id="role"
                value={entry.role || ''}
                onChange={(e) => {
                  handleChange('role', e.target.value);
                  if (errors.role) {
                    setErrors((prev) => ({ ...prev, role: '' }));
                  }
                }}
                disabled={isReadOnly}
                style={errors.role ? { borderColor: 'var(--color-danger)' } : {}}
              >
                <option value="">Chọn Role</option>
                {ROLES.map((role) => (
                  <option key={role} value={role}>
                    {role}
                  </option>
                ))}
              </select>
              <span className="material-symbols-outlined editor-form-select-icon">expand_more</span>
            </div>
            {errors.role && (
              <p className="editor-form-helper text-danger" style={{ marginTop: '0.25rem' }}>
                {errors.role}
              </p>
            )}
          </div>

          <div className="editor-form-group">
            <label className="editor-form-label" htmlFor="level">
              Level
            </label>
            <input
              className="editor-form-input"
              id="level"
              type="number"
              value={entry.level || 1}
              onChange={(e) => handleChange('level', parseInt(e.target.value) || 1)}
              min={1}
              readOnly={isReadOnly}
            />
          </div>

          <div className="editor-form-group">
            <label className="editor-form-label" htmlFor="time-process">
              Time Process (seconds) *
            </label>
            <input
              className="editor-form-input"
              id="time-process"
              type="number"
              value={entry.timeProcess || 0}
              onChange={(e) => {
                handleChange('timeProcess', parseInt(e.target.value) || 0);
                if (errors.timeProcess) {
                  setErrors((prev) => ({ ...prev, timeProcess: '' }));
                }
              }}
              min={0}
              required
              readOnly={isReadOnly}
              style={errors.timeProcess ? { borderColor: 'var(--color-danger)' } : {}}
            />
            <p className="editor-form-helper">
              {Math.round((entry.timeProcess || 0) / 60)} minutes
            </p>
            {errors.timeProcess && (
              <p className="editor-form-helper text-danger" style={{ marginTop: '0.25rem' }}>
                {errors.timeProcess}
              </p>
            )}
          </div>

          {availableAircraftIds.length > 0 && (
            <div className="editor-form-group">
              <label className="editor-form-label" htmlFor="aircraft-id">
                Aircraft ID (Optional)
              </label>
              <div className="editor-form-select-wrapper">
                <select
                  className="editor-form-select"
                  id="aircraft-id"
                  value={entry.aircraftId || ''}
                  onChange={(e) => handleChange('aircraftId', e.target.value)}
                  disabled={isReadOnly}
                >
                  <option value="">All Aircrafts</option>
                  {availableAircraftIds.map((id) => (
                    <option key={id} value={id}>
                      {id}
                    </option>
                  ))}
                </select>
                <span className="material-symbols-outlined editor-form-select-icon">expand_more</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div style={{ marginTop: '2rem' }}>
        {isReadOnly ? (
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              className="editor-form-button-primary"
              onClick={onStartEdit}
            >
              Update
            </button>
            {onDelete && (
              <button
                className="editor-form-button-secondary"
                onClick={handleDelete}
                className="text-danger"
                style={{ borderColor: 'var(--color-danger)' }}
              >
                Delete
              </button>
            )}
          </div>
        ) : (
          <button
            className="editor-form-button-primary"
            onClick={handleSave}
            disabled={!isFormValid()}
            style={{
              opacity: !isFormValid() ? 0.5 : 1,
              cursor: !isFormValid() ? 'not-allowed' : 'pointer',
            }}
          >
            {initialData ? 'SAVE CHANGES' : 'ADD ENTRY'}
          </button>
        )}
      </div>
    </>
  );
};

export default TimeMatrixEditor;

