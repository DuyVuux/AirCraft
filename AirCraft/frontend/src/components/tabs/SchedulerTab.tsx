import { useState } from 'react';
import type { TabProps } from './types';
import type { ScheduleResult, ScheduledTask } from '@/types/scheduler';
import InputPreview from '@/components/scheduler/InputPreview';
import AlgorithmRunner from '@/components/scheduler/AlgorithmRunner';
import GanttChart from '@/components/scheduler/GanttChart';

export const tabConfig = {
    id: 'scheduler',
    label: 'Scheduler',
    icon: 'schedule',
    order: 5,
};

function SchedulerTab({ aircrafts, employees }: TabProps) {
    const [scheduleResult, setScheduleResult] = useState<ScheduleResult | null>(null);
    const [selectedTask, setSelectedTask] = useState<ScheduledTask | null>(null);

    const handleRunComplete = (result: ScheduleResult) => {
        setScheduleResult(result);
    };

    const handleTaskClick = (task: ScheduledTask) => {
        setSelectedTask(task);
    };

    const isInputValid = aircrafts.length > 0 && employees.length > 0;

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {/* Section 1: Input Preview */}
            <InputPreview aircrafts={aircrafts} employees={employees} />

            {/* Section 2: Algorithm Runner */}
            <AlgorithmRunner
                onRunComplete={handleRunComplete}
                disabled={!isInputValid}
            />

            {/* Section 3: Gantt Chart */}
            <GanttChart
                scheduledTasks={scheduleResult?.scheduledTasks || []}
                employees={employees}
                viewMode="employee"
                onTaskClick={handleTaskClick}
            />

            {/* Task Detail Modal (TODO) */}
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
                        style={{
                            minWidth: '300px',
                            maxWidth: '400px',
                        }}
                    >
                        <h3 className="editor-card-title">Chi tiết Task</h3>
                        <div style={{ marginTop: '1rem' }}>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.875rem' }}>
                                <span style={{ color: 'var(--color-text-secondary)' }}>Task:</span>
                                <span style={{ fontWeight: 500 }}>{selectedTask.taskCode}</span>

                                <span style={{ color: 'var(--color-text-secondary)' }}>Máy bay:</span>
                                <span>{selectedTask.aircraftId}</span>

                                <span style={{ color: 'var(--color-text-secondary)' }}>Nhân viên:</span>
                                <span>{selectedTask.employeeName || selectedTask.employeeId}</span>

                                <span style={{ color: 'var(--color-text-secondary)' }}>Bắt đầu:</span>
                                <span>{new Date(selectedTask.startTime).toLocaleString('vi-VN')}</span>

                                <span style={{ color: 'var(--color-text-secondary)' }}>Kết thúc:</span>
                                <span>{new Date(selectedTask.endTime).toLocaleString('vi-VN')}</span>
                            </div>
                        </div>
                        <button
                            className="editor-form-button-secondary"
                            onClick={() => setSelectedTask(null)}
                            style={{ marginTop: '1rem' }}
                        >
                            Đóng
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default SchedulerTab;
