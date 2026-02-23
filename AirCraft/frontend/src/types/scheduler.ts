/**
 * Types cho Scheduler module
 */

export interface ScheduledTask {
    taskId: string;
    taskCode: string;
    aircraftId: string;
    employeeId: string;
    employeeName?: string;
    startTime: string;
    endTime: string;
    duration: number;
    type?: 'TASK' | 'BREAK' | 'WALK' | 'BUS';
}

export interface ScheduleResult {
    status: 'OPTIMAL' | 'FEASIBLE' | 'INFEASIBLE' | 'ERROR';
    message?: string;
    scheduledTasks: ScheduledTask[];
    totalCost?: number;
    solveTimeMs?: number;
}

export interface GanttRow {
    id: string;
    label: string;
    tasks: ScheduledTask[];
}

export interface SchedulerState {
    isRunning: boolean;
    result: ScheduleResult | null;
    error: string | null;
}
