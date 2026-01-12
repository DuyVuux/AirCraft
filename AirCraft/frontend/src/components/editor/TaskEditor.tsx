import React, { useState, useEffect } from 'react';
import { AVAILABLE_CERTIFICATIONS } from '@/types/certifications';
import './Editor.css';

export interface Task {
  taskCode: string;
  description?: string;
  requiredCertifications?: string[]; // Yêu cầu chứng chỉ
  timeProcess?: number; // Thời gian thực hiện task (giây)
  defaultMinLevel?: number; // Mức level mặc định cho task này
}

interface TaskEditorProps {
  onSave?: (task: Task) => void;
  onDelete?: (taskCode: string) => void;
  initialData?: Task | null;
  existingTasks?: Task[];
}

const TaskEditor: React.FC<TaskEditorProps> = ({
  onSave,
  onDelete,
  initialData,
  existingTasks = [],
}) => {
  const [task, setTask] = useState<Task>(
    initialData || {
      taskCode: '',
      description: '',
      requiredCertifications: [],
      timeProcess: 0,
    }
  );

  useEffect(() => {
    if (initialData) {
      setTask(initialData);
    } else {
      setTask({
        taskCode: '',
        description: '',
        requiredCertifications: [],
        timeProcess: 0,
      });
    }
  }, [initialData]);

  const handleChange = (field: keyof Task, value: any) => {
    setTask((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = () => {
    if (!task.taskCode.trim()) {
      return;
    }
    onSave?.(task);
    if (!initialData) {
      setTask({
        taskCode: '',
        description: '',
        requiredCertifications: [],
        timeProcess: 0,
      });
    }
  };

  const handleDelete = () => {
    if (task.taskCode && onDelete) {
      onDelete(task.taskCode);
    }
  };

  const isDuplicate = existingTasks.some(
    (t) => t.taskCode === task.taskCode && (!initialData || t.taskCode !== initialData.taskCode)
  );

  return (
    <div className="editor-card">
      <h3 className="editor-card-title">{initialData ? 'Edit Task' : 'Add New Task'}</h3>

      <div className="editor-form-grid">
        <div className="editor-form-group">
          <label className="editor-form-label" htmlFor="task-code">
            Task Code *
          </label>
          <input
            className="editor-form-input"
            id="task-code"
            type="text"
            value={task.taskCode}
            onChange={(e) => handleChange('taskCode', e.target.value.toUpperCase())}
            placeholder="Ví dụ: TASK_TIRE_CHECK"
            required
            style={isDuplicate ? { borderColor: 'var(--color-danger)' } : {}}
          />
          {isDuplicate && (
            <p className="editor-form-helper text-danger">
              Task code đã tồn tại
            </p>
          )}
          {!isDuplicate && (
            <p className="editor-form-helper">Ví dụ: TASK_TIRE_CHECK</p>
          )}
        </div>

        <div className="editor-form-group">
          <label className="editor-form-label" htmlFor="task-description">
            Description (Optional)
          </label>
          <input
            className="editor-form-input"
            id="task-description"
            type="text"
            value={task.description || ''}
            onChange={(e) => handleChange('description', e.target.value)}
            placeholder="Kiểm tra lốp máy bay"
          />
        </div>

        <div className="editor-form-group">
          <label className="editor-form-label" htmlFor="task-time-process">
            Thời gian thực hiện (giây)
          </label>
          <input
            className="editor-form-input"
            id="task-time-process"
            type="number"
            value={task.timeProcess || 0}
            onChange={(e) => handleChange('timeProcess', parseInt(e.target.value) || 0)}
            min={0}
            placeholder="Ví dụ: 1800 (30 phút)"
          />
          <p className="editor-form-helper">Ví dụ: 1800 = 30 phút</p>
        </div>
      </div>

      {/* Required Certifications */}
      <div style={{ marginTop: '1rem' }}>
        <label className="editor-form-label">Yêu Cầu Chứng Chỉ</label>
        <p className="editor-form-helper">Chọn các chứng chỉ mà nhân viên cần có để thực hiện task này</p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: '0.5rem', marginTop: '0.5rem' }}>
          {AVAILABLE_CERTIFICATIONS.map(cert => (
            <label
              key={cert}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.375rem',
                border: '1px solid var(--border-light)',
                borderRadius
                  : '0.375rem',
                cursor: 'pointer',
                background: (task.requiredCertifications || []).includes(cert) ? 'var(--color-primary-10)' : 'transparent',
              }}
            >
              <input
                type="checkbox"
                checked={(task.requiredCertifications || []).includes(cert)}
                onChange={(e) => {
                  const certs = task.requiredCertifications || [];
                  if (e.target.checked) {
                    handleChange('requiredCertifications', [...certs, cert]);
                  } else {
                    handleChange('requiredCertifications', certs.filter(c => c !== cert));
                  }
                }}
                style={{ cursor: 'pointer' }}
              />
              <span style={{ fontSize: '0.875rem' }}>{cert}</span>
            </label>
          ))}
        </div>
      </div>

      <div style={{ marginTop: '1.5rem', display: 'flex', gap: '0.75rem' }}>
        <button
          className="editor-form-button-primary"
          onClick={handleSave}
          disabled={!task.taskCode.trim() || isDuplicate}
          style={{ opacity: (!task.taskCode.trim() || isDuplicate) ? 0.5 : 1, cursor: (!task.taskCode.trim() || isDuplicate) ? 'not-allowed' : 'pointer' }}
        >
          {initialData ? 'Update' : 'Add'} Task
        </button>
        {initialData && onDelete && (
          <button
            className="editor-form-button-secondary text-danger"
            onClick={handleDelete}
            style={{ borderColor: 'var(--color-danger)' }}
          >
            Delete
          </button>
        )}
      </div>
    </div>
  );
};

interface TaskListProps {
  tasks: Task[];
  onEdit: (task: Task) => void;
  onDelete: (taskCode: string) => void;
}

export const TaskList: React.FC<TaskListProps> = ({ tasks, onEdit, onDelete }) => {
  const [selectedIds, setSelectedIds] = React.useState<Set<string>>(new Set());

  if (tasks.length === 0) {
    return (
      <div className="editor-card">
        <p className="editor-task-list-empty">Chưa có task nào. Thêm task mới ở trên.</p>
      </div>
    );
  }

  const formatTime = (seconds?: number) => {
    if (!seconds || seconds === 0) return 'Chưa cài đặt';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    if (remainingSeconds === 0) return `${minutes} phút`;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const handleToggleSelect = (taskCode: string) => {
    setSelectedIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(taskCode)) {
        newSet.delete(taskCode);
      } else {
        newSet.add(taskCode);
      }
      return newSet;
    });
  };

  const handleSelectAll = () => {
    if (selectedIds.size === tasks.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(tasks.map(t => t.taskCode)));
    }
  };

  const handleBulkDelete = () => {
    if (selectedIds.size === 0) return;
    if (window.confirm(`Xóa ${selectedIds.size} tasks?`)) {
      selectedIds.forEach(id => onDelete(id));
      setSelectedIds(new Set());
    }
  };

  const allSelected = selectedIds.size === tasks.length && tasks.length > 0;

  return (
    <div className="editor-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h3 className="editor-card-title">Tasks List ({tasks.length})</h3>
        {selectedIds.size > 0 && (
          <button
            onClick={handleBulkDelete}
            style={{
              padding: '0.5rem 1rem',
              background: '#ef4444',
              color: 'white',
              border: 'none',
              borderRadius: '0.375rem',
              cursor: 'pointer',
              fontSize: '0.875rem',
              fontWeight: 500,
            }}
          >
            Xóa {selectedIds.size} tasks
          </button>
        )}
      </div>
      <div style={{ marginTop: '1rem', overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid var(--color-border)' }}>
              <th style={{ padding: '0.75rem', textAlign: 'left', width: '40px' }}>
                <input
                  type="checkbox"
                  checked={allSelected}
                  onChange={handleSelectAll}
                  style={{ cursor: 'pointer' }}
                />
              </th>
              <th style={{ padding: '0.75rem', textAlign: 'left' }}>Mã Task</th>
              <th style={{ padding: '0.75rem', textAlign: 'left' }}>Mô tả</th>
              <th style={{ padding: '0.75rem', textAlign: 'left' }}>Thời gian</th>
              <th style={{ padding: '0.75rem', textAlign: 'left' }}>Yêu cầu chứng chỉ</th>
              <th style={{ padding: '0.75rem', textAlign: 'right' }}>Hành động</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((task) => {
              const isSelected = selectedIds.has(task.taskCode);
              return (
                <tr
                  key={task.taskCode}
                  style={{
                    borderBottom: '1px solid var(--color-border)',
                    backgroundColor: isSelected ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                  }}
                >
                  <td style={{ padding: '0.75rem' }}>
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => handleToggleSelect(task.taskCode)}
                      style={{ cursor: 'pointer' }}
                    />
                  </td>
                  <td style={{ padding: '0.75rem', fontWeight: 600 }}>
                    <span className="editor-task-chip">{task.taskCode}</span>
                  </td>
                  <td style={{ padding: '0.75rem', color: 'var(--color-text-secondary)' }}>
                    {task.description || '—'}
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    <span style={{
                      color: task.timeProcess && task.timeProcess > 0 ? 'var(--color-success)' : 'var(--color-warning)',
                      fontWeight: 500
                    }}>
                      {formatTime(task.timeProcess)}
                    </span>
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    {task.requiredCertifications && task.requiredCertifications.length > 0 ? (
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                        {task.requiredCertifications.map((cert, idx) => (
                          <span
                            key={idx}
                            style={{
                              fontSize: '0.7rem',
                              padding: '0.125rem 0.5rem',
                              borderRadius: '0.75rem',
                              background: 'var(--color-warning-bg)',
                              color: 'var(--color-warning)',
                            }}
                          >
                            {cert}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span style={{ color: 'var(--color-text-secondary)' }}>Không yêu cầu</span>
                    )}
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                      <button
                        className="editor-form-button-secondary"
                        onClick={() => onEdit(task)}
                        style={{ padding: '0.375rem 0.75rem', fontSize: '0.875rem' }}
                      >
                        <span className="material-symbols-outlined" style={{ fontSize: '1rem' }}>edit</span>
                        Edit
                      </button>
                      <button
                        className="editor-form-button-secondary"
                        onClick={() => onDelete(task.taskCode)}
                        style={{ padding: '0.375rem 0.75rem', fontSize: '0.875rem' }}
                      >
                        <span className="material-symbols-outlined text-danger" style={{ fontSize: '1rem' }}>delete</span>
                        <span className="text-danger">Delete</span>
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TaskEditor;

