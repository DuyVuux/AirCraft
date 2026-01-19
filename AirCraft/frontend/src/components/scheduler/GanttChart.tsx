import { useMemo } from 'react';
import type { ScheduledTask, GanttRow } from '@/types/scheduler';
import type { Employee } from '@/types/employee';
import GanttTaskBar from './GanttTaskBar';

interface GanttChartProps {
    scheduledTasks: ScheduledTask[];
    employees: Employee[];
    viewMode?: 'employee' | 'aircraft';
    onTaskClick?: (task: ScheduledTask) => void;
}

function GanttChart({
    scheduledTasks,
    employees,
    viewMode = 'employee',
    onTaskClick
}: GanttChartProps) {
    const rows: GanttRow[] = useMemo(() => {
        if (viewMode === 'employee') {
            return employees.map(emp => ({
                id: emp.employeeId,
                label: emp.name || emp.employeeId,
                tasks: scheduledTasks.filter(t => t.employeeId === emp.employeeId),
            }));
        } else {
            const aircraftIds = [...new Set(scheduledTasks.map(t => t.aircraftId))];
            return aircraftIds.map(id => ({
                id,
                label: id,
                tasks: scheduledTasks.filter(t => t.aircraftId === id),
            }));
        }
    }, [scheduledTasks, employees, viewMode]);

    const timeRange = useMemo(() => {
        if (scheduledTasks.length === 0) {
            const now = new Date();
            return {
                start: now.getTime(),
                end: now.getTime() + 8 * 60 * 60 * 1000,
            };
        }

        const times = scheduledTasks.flatMap(t => [
            new Date(t.startTime).getTime(),
            new Date(t.endTime).getTime(),
        ]);
        return {
            start: Math.min(...times),
            end: Math.max(...times),
        };
    }, [scheduledTasks]);

    const totalDuration = timeRange.end - timeRange.start;
    const hourWidth = 100;
    const hours = Math.ceil(totalDuration / (60 * 60 * 1000));
    const chartWidth = hours * hourWidth;
    const rowHeight = 50;

    const formatHour = (timestamp: number) => {
        const date = new Date(timestamp);
        return `${date.getUTCHours().toString().padStart(2, '0')}:${date.getUTCMinutes().toString().padStart(2, '0')}`;
    };

    if (scheduledTasks.length === 0) {
        return (
            <div className="editor-card">
                <h3 className="editor-card-title">Biểu đồ Gantt</h3>
                <div style={{
                    padding: '3rem',
                    textAlign: 'center',
                    color: 'var(--color-text-secondary)',
                    background: 'var(--color-surface-elevated)',
                    borderRadius: '0.5rem',
                    marginTop: '1rem',
                }}>
                    <span className="material-symbols-outlined" style={{ fontSize: '3rem', opacity: 0.5 }}>bar_chart</span>
                    <p style={{ marginTop: '0.5rem' }}>Chưa có lịch. Chạy thuật toán để xem kết quả.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="editor-card">
            <h3 className="editor-card-title">Biểu đồ Gantt</h3>

            <div style={{ marginTop: '1rem', overflowX: 'auto' }}>
                <div style={{ display: 'flex', minWidth: `${chartWidth + 150}px` }}>
                    {/* Row Labels */}
                    <div style={{ width: '150px', flexShrink: 0 }}>
                        <div style={{ height: '30px', borderBottom: '1px solid var(--color-border)' }} />
                        {rows.map(row => (
                            <div
                                key={row.id}
                                style={{
                                    height: `${rowHeight}px`,
                                    display: 'flex',
                                    alignItems: 'center',
                                    padding: '0 0.5rem',
                                    borderBottom: '1px solid var(--color-border)',
                                    fontSize: '0.875rem',
                                    fontWeight: 500,
                                }}
                            >
                                {row.label}
                            </div>
                        ))}
                    </div>

                    {/* Chart Area */}
                    <div style={{ flex: 1, position: 'relative' }}>
                        {/* Time Headers */}
                        <div style={{ display: 'flex', height: '30px', borderBottom: '1px solid var(--color-border)' }}>
                            {Array.from({ length: hours }).map((_, i) => (
                                <div
                                    key={i}
                                    style={{
                                        width: `${hourWidth}px`,
                                        fontSize: '0.75rem',
                                        color: 'var(--color-text-secondary)',
                                        borderRight: '1px solid var(--color-border)',
                                        padding: '0.25rem',
                                    }}
                                >
                                    {formatHour(timeRange.start + i * 60 * 60 * 1000)}
                                </div>
                            ))}
                        </div>

                        {/* Rows */}
                        {rows.map(row => (
                            <div
                                key={row.id}
                                style={{
                                    height: `${rowHeight}px`,
                                    position: 'relative',
                                    borderBottom: '1px solid var(--color-border)',
                                    background: 'var(--color-surface-elevated)',
                                }}
                            >
                                {row.tasks.map(task => {
                                    const taskStart = new Date(task.startTime).getTime();
                                    const taskEnd = new Date(task.endTime).getTime();
                                    const left = ((taskStart - timeRange.start) / totalDuration) * chartWidth;
                                    const width = ((taskEnd - taskStart) / totalDuration) * chartWidth;

                                    return (
                                        <GanttTaskBar
                                            key={task.taskId}
                                            task={task}
                                            left={left}
                                            width={Math.max(width, 30)}
                                            onClick={() => onTaskClick?.(task)}
                                        />
                                    );
                                })}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default GanttChart;
