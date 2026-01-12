import type { Aircraft } from '@/types/aircraft';
import type { Employee } from '@/types/employee';

interface InputPreviewProps {
    aircrafts: Aircraft[];
    employees: Employee[];
}

function InputPreview({ aircrafts, employees }: InputPreviewProps) {
    const totalTasks = aircrafts.reduce((sum, a) => sum + a.requiredTasks.length, 0);

    return (
        <div className="editor-card">
            <h3 className="editor-card-title">Dữ liệu đầu vào</h3>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
                {/* Máy bay */}
                <div style={{ background: 'var(--color-surface-elevated)', padding: '1rem', borderRadius: '0.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                        <span className="material-symbols-outlined" style={{ color: '#3b82f6' }}>flight</span>
                        <span style={{ fontWeight: 600 }}>Máy bay: {aircrafts.length}</span>
                        <span style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
                            ({totalTasks} tasks)
                        </span>
                    </div>
                    <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                        {aircrafts.length === 0 ? (
                            <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>Chưa có máy bay</p>
                        ) : (
                            aircrafts.map((aircraft) => (
                                <div key={aircraft.aircraftId} style={{
                                    padding: '0.5rem',
                                    borderBottom: '1px solid var(--color-border)',
                                    fontSize: '0.875rem'
                                }}>
                                    <div style={{ fontWeight: 500 }}>{aircraft.aircraftId}</div>
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem', marginTop: '0.25rem' }}>
                                        {aircraft.requiredTasks.map((task, idx) => (
                                            <span key={idx} style={{
                                                fontSize: '0.7rem',
                                                padding: '0.125rem 0.375rem',
                                                borderRadius: '0.75rem',
                                                background: 'rgba(59, 130, 246, 0.2)',
                                                color: '#3b82f6',
                                            }}>
                                                {task.taskCode}
                                            </span>
                                        ))}
                                        {aircraft.requiredTasks.length === 0 && (
                                            <span style={{ color: 'var(--color-text-secondary)', fontSize: '0.75rem' }}>Không có task</span>
                                        )}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Nhân viên */}
                <div style={{ background: 'var(--color-surface-elevated)', padding: '1rem', borderRadius: '0.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                        <span className="material-symbols-outlined" style={{ color: '#10b981' }}>person</span>
                        <span style={{ fontWeight: 600 }}>Nhân viên: {employees.length}</span>
                    </div>
                    <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                        {employees.length === 0 ? (
                            <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>Chưa có nhân viên</p>
                        ) : (
                            employees.map((emp) => (
                                <div key={emp.employeeId} style={{
                                    padding: '0.5rem',
                                    borderBottom: '1px solid var(--color-border)',
                                    fontSize: '0.875rem'
                                }}>
                                    <div style={{ fontWeight: 500 }}>{emp.employeeId} - {emp.name || 'N/A'}</div>
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem', marginTop: '0.25rem' }}>
                                        {(emp.taskCapabilities || []).map((cap, idx) => (
                                            <span key={idx} style={{
                                                fontSize: '0.7rem',
                                                padding: '0.125rem 0.375rem',
                                                borderRadius: '0.75rem',
                                                background: 'rgba(16, 185, 129, 0.2)',
                                                color: '#10b981',
                                            }}>
                                                {cap}
                                            </span>
                                        ))}
                                        {(!emp.taskCapabilities || emp.taskCapabilities.length === 0) && (
                                            <span style={{ color: 'var(--color-text-secondary)', fontSize: '0.75rem' }}>Không có năng lực</span>
                                        )}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default InputPreview;
