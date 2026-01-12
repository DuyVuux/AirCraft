import { useState } from 'react';
import type { ScheduledTask, ScheduleResult } from '@/types/scheduler';
import type { Employee } from '@/types/employee';
import GanttChart from './GanttChart';

interface ResultsTabProps {
    scheduleResult: ScheduleResult | null;
    employees: Employee[];
}

function ResultsTab({ scheduleResult, employees }: ResultsTabProps) {
    const [selectedTask, setSelectedTask] = useState<ScheduledTask | null>(null);
    const [viewMode, setViewMode] = useState<'employee' | 'aircraft'>('employee');

    const handleTaskClick = (task: ScheduledTask) => {
        setSelectedTask(task);
    };

    if (!scheduleResult) {
        return (
            <div className="editor-card">
                <h3 className="editor-card-title">Kết quả</h3>
                <div style={{
                    padding: '4rem',
                    textAlign: 'center',
                    color: 'var(--color-text-secondary)',
                }}>
                    <span className="material-symbols-outlined" style={{ fontSize: '4rem', opacity: 0.3 }}>
                        bar_chart
                    </span>
                    <p style={{ marginTop: '1rem', fontSize: '1.125rem' }}>
                        Chưa có kết quả
                    </p>
                    <p style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>
                        Chuyển sang tab "Chạy thuật toán" để thực thi scheduling.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Tóm tắt kết quả */}
            <div className="editor-card">
                <h3 className="editor-card-title">Tóm tắt kết quả</h3>
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(4, 1fr)',
                    gap: '1rem',
                    marginTop: '1rem'
                }}>
                    <div style={{
                        padding: '1rem',
                        background: scheduleResult.status === 'OPTIMAL' ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                        borderRadius: '0.5rem',
                        textAlign: 'center'
                    }}>
                        <div style={{
                            fontSize: '1.5rem',
                            fontWeight: 700,
                            color: scheduleResult.status === 'OPTIMAL' ? '#10b981' : '#f59e0b'
                        }}>
                            {scheduleResult.status}
                        </div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Trạng thái</div>
                    </div>
                    <div style={{
                        padding: '1rem',
                        background: 'rgba(59, 130, 246, 0.1)',
                        borderRadius: '0.5rem',
                        textAlign: 'center'
                    }}>
                        <div style={{ fontSize: '2rem', fontWeight: 700, color: '#3b82f6' }}>
                            {scheduleResult.scheduledTasks.length}
                        </div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Tasks đã xếp</div>
                    </div>
                    <div style={{
                        padding: '1rem',
                        background: 'rgba(139, 92, 246, 0.1)',
                        borderRadius: '0.5rem',
                        textAlign: 'center'
                    }}>
                        <div style={{ fontSize: '2rem', fontWeight: 700, color: '#8b5cf6' }}>
                            {scheduleResult.solveTimeMs || 0}ms
                        </div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Thời gian giải</div>
                    </div>
                    <div style={{
                        padding: '1rem',
                        background: 'rgba(236, 72, 153, 0.1)',
                        borderRadius: '0.5rem',
                        textAlign: 'center'
                    }}>
                        <div style={{ fontSize: '2rem', fontWeight: 700, color: '#ec4899' }}>
                            {new Set(scheduleResult.scheduledTasks.map(t => t.employeeId)).size}
                        </div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>NV được gán</div>
                    </div>
                </div>
            </div>

            {/* View mode toggle */}
            <div className="editor-card">
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <h3 className="editor-card-title">Biểu đồ Gantt</h3>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button
                            className={viewMode === 'employee' ? 'editor-form-button-primary' : 'editor-form-button-secondary'}
                            onClick={() => setViewMode('employee')}
                            style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
                        >
                            Theo nhân viên
                        </button>
                        <button
                            className={viewMode === 'aircraft' ? 'editor-form-button-primary' : 'editor-form-button-secondary'}
                            onClick={() => setViewMode('aircraft')}
                            style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}
                        >
                            Theo máy bay
                        </button>
                    </div>
                </div>
                <div style={{ marginTop: '1rem' }}>
                    <GanttChart
                        scheduledTasks={scheduleResult.scheduledTasks}
                        employees={employees}
                        viewMode={viewMode}
                        onTaskClick={handleTaskClick}
                    />
                </div>
            </div>

            {/* Danh sách chi tiết */}
            <div className="editor-card">
                <h3 className="editor-card-title">Chi tiết lịch trình ({scheduleResult.scheduledTasks.length} tasks)</h3>
                <div style={{ marginTop: '1rem', overflowX: 'auto' }}>
                    {scheduleResult.scheduledTasks.length === 0 ? (
                        <p style={{ color: 'var(--color-text-secondary)', textAlign: 'center', padding: '2rem' }}>
                            Không có task nào được xếp lịch.
                        </p>
                    ) : (
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                            <thead>
                                <tr style={{ borderBottom: '2px solid var(--color-border)' }}>
                                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Task</th>
                                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Máy bay</th>
                                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Nhân viên</th>
                                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Bắt đầu</th>
                                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Kết thúc</th>
                                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Thời lượng</th>
                                </tr>
                            </thead>
                            <tbody>
                                {scheduleResult.scheduledTasks.map((task) => (
                                    <tr
                                        key={task.taskId}
                                        style={{
                                            borderBottom: '1px solid var(--color-border)',
                                            cursor: 'pointer',
                                            background: selectedTask?.taskId === task.taskId ? 'rgba(59, 130, 246, 0.1)' : 'transparent',
                                        }}
                                        onClick={() => handleTaskClick(task)}
                                    >
                                        <td style={{ padding: '0.75rem', fontWeight: 500 }}>{task.taskCode}</td>
                                        <td style={{ padding: '0.75rem' }}>{task.aircraftId}</td>
                                        <td style={{ padding: '0.75rem' }}>{task.employeeName || task.employeeId}</td>
                                        <td style={{ padding: '0.75rem' }}>
                                            {new Date(task.startTime).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
                                        </td>
                                        <td style={{ padding: '0.75rem' }}>
                                            {new Date(task.endTime).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
                                        </td>
                                        <td style={{ padding: '0.75rem' }}>{task.duration} phút</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>

            {/* Modal chi tiết task */}
            {selectedTask && (
                <div
                    style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        background: 'rgba(0,0,0,0.5)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 1000,
                    }}
                    onClick={() => setSelectedTask(null)}
                >
                    <div
                        className="editor-card"
                        onClick={(e) => e.stopPropagation()}
                        style={{ minWidth: '350px', maxWidth: '450px' }}
                    >
                        <h3 className="editor-card-title">Chi tiết Task</h3>
                        <div style={{ marginTop: '1rem' }}>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.875rem' }}>
                                <span style={{ color: 'var(--color-text-secondary)' }}>Task Code:</span>
                                <span style={{ fontWeight: 600 }}>{selectedTask.taskCode}</span>

                                <span style={{ color: 'var(--color-text-secondary)' }}>Máy bay:</span>
                                <span>{selectedTask.aircraftId}</span>

                                <span style={{ color: 'var(--color-text-secondary)' }}>Nhân viên:</span>
                                <span>{selectedTask.employeeName || selectedTask.employeeId}</span>

                                <span style={{ color: 'var(--color-text-secondary)' }}>Bắt đầu:</span>
                                <span>{new Date(selectedTask.startTime).toLocaleString('vi-VN')}</span>

                                <span style={{ color: 'var(--color-text-secondary)' }}>Kết thúc:</span>
                                <span>{new Date(selectedTask.endTime).toLocaleString('vi-VN')}</span>

                                <span style={{ color: 'var(--color-text-secondary)' }}>Thời lượng:</span>
                                <span>{selectedTask.duration} phút</span>
                            </div>
                        </div>
                        <button
                            className="editor-form-button-secondary"
                            onClick={() => setSelectedTask(null)}
                            style={{ marginTop: '1.5rem', width: '100%' }}
                        >
                            Đóng
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default ResultsTab;
