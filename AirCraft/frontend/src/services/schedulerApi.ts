import type { Aircraft } from '@/types/aircraft';
import type { Employee } from '@/types/employee';
import type { ScheduleResult, ScheduledTask } from '@/types/scheduler';
import type { MapRoute } from '@/types/mapEditor';
import type { Task } from '@/components/editor/TaskEditor';
import type { DistanceMatrixEntry, TimeMatrixEntry } from '@/types/matrix';

export interface AlgorithmOption {
    id: string;
    name: string;
    description?: string;
}

export interface OptimizeOption {
    id: string;
    name: string;
}

export interface AlgorithmsResponse {
    algorithms: AlgorithmOption[];
    optimizeOptions: OptimizeOption[];
    defaultTimeLimit: number;
}

export interface SchedulerConfig {
    algorithm: string;
    timeLimit: number;
    optimizeFor: string;
}

export interface SchedulerInput {
    trackingId: string;
    aircrafts: Aircraft[];
    employees: Employee[];
    hubs: any[];
    matrixConfigs: {
        distanceMatrix: DistanceMatrixEntry[];
        timeMatrix: TimeMatrixEntry[];
    };
    config: SchedulerConfig;
}

export interface LogEntry {
    timestamp: string;
    level: 'info' | 'warning' | 'error' | 'success';
    message: string;
    details?: Record<string, unknown>;
}

export interface SchedulerProgress {
    stage: string;
    progress: number;
    currentBest?: number;
    logs: LogEntry[];
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

const ENDPOINTS = {
    GET_ALGORITHMS: '/api/scheduler/algorithms',
    SCHEDULER_RUN: '/api/scheduler/run',
    SCHEDULER_STATUS: '/api/scheduler/status',
    SCHEDULER_CANCEL: '/api/scheduler/cancel',
};

export async function fetchAlgorithms(): Promise<AlgorithmsResponse> {
    try {
        const token = localStorage.getItem('access_token') || '';
        const response = await fetch(`${API_BASE_URL}${ENDPOINTS.GET_ALGORITHMS}`, {
            headers: token ? { 'Authorization': `Bearer ${token}` } : {},
        });
        if (!response.ok) {
            throw new Error(`Failed to fetch algorithms: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.warn('Failed to fetch algorithms from API, using fallback:', error);
        return {
            algorithms: [
                { id: 'ortools', name: 'Google OR-Tools (CP-SAT)', description: 'Constraint Programming solver' },
                { id: 'genetic', name: 'Genetic Algorithm', description: 'Evolutionary optimization' },
                { id: 'greedy', name: 'Greedy Heuristic', description: 'Fast heuristic solution' },
            ],
            optimizeOptions: [
                { id: 'makespan', name: 'Thời gian hoàn thành (Makespan)' },
                { id: 'cost', name: 'Chi phí nhân công' },
                { id: 'balance', name: 'Cân bằng tải' },
            ],
            defaultTimeLimit: 60,
        };
    }
}

function createLog(level: LogEntry['level'], message: string, details?: Record<string, unknown>): LogEntry {
    return {
        timestamp: new Date().toISOString(),
        level,
        message,
        details,
    };
}

function buildDistanceMatrix(routes: MapRoute[]): DistanceMatrixEntry[] {
    return routes.map(route => {
        // Calculate travel time based on timeMode
        let travelTime = 0;

        if (route.timeMode === 'manual_input') {
            // Sum manual times from segments
            travelTime = route.segments.reduce((sum, seg) => sum + (seg.manualTime || 0), 0);
        } else if (route.fixedVelocity && route.totalDistance) {
            // Distance (m) / Velocity (m/s) = Time (s)
            travelTime = Math.round(route.totalDistance / route.fixedVelocity);
        }

        return {
            srcCode: route.startNodeId,
            destCode: route.endNodeId,
            travelTime,
        };
    });
}

function buildTimeMatrix(
    tasks: Task[],
    employees: Employee[],
    aircrafts: Aircraft[]
): TimeMatrixEntry[] {
    const timeMatrix: TimeMatrixEntry[] = [];

    // For each task, create entries for each role and aircraft combination
    tasks.forEach(task => {
        if (!task.timeProcess || task.timeProcess === 0) return;

        // Get unique roles from employees
        const roles = [...new Set(employees.map(e => e.eType.role))];

        roles.forEach(role => {
            // For each aircraft that requires this task
            aircrafts.forEach(aircraft => {
                const requiresTask = aircraft.requiredTasks.some(rt => rt.taskCode === task.taskCode);
                if (!requiresTask) return;

                timeMatrix.push({
                    taskCode: task.taskCode,
                    role,
                    level: 1, // Always 1, we use certifications instead of levels
                    aircraftId: aircraft.aircraftId,
                    timeProcess: task.timeProcess!,
                });
            });
        });
    });

    return timeMatrix;
}

export async function runScheduler(
    input: {
        aircrafts: Aircraft[];
        employees: Employee[];
        tasks: Task[];
        routes: MapRoute[];
        config: SchedulerConfig;
    },
    onProgress?: (progress: SchedulerProgress) => void
): Promise<{ result: ScheduleResult; logs: LogEntry[] }> {
    const logs: LogEntry[] = [];

    const addLog = (level: LogEntry['level'], message: string, details?: Record<string, unknown>) => {
        const log = createLog(level, message, details);
        logs.push(log);
        onProgress?.({
            stage: message,
            progress: 0,
            logs: [...logs]
        });
    };

    try {
        addLog('info', 'Khởi tạo scheduler...', { config: input.config });

        // Build tracking ID
        const trackingId = `PLAN-${new Date().toISOString().split('T')[0]}-${String(Math.floor(Math.random() * 1000)).padStart(3, '0')}`;
        addLog('info', `Tracking ID: ${trackingId}`);

        // Build matrices
        addLog('info', 'Đang xây dựng distance matrix từ routes...');
        const distanceMatrix = buildDistanceMatrix(input.routes);
        addLog('info', `Distance matrix: ${distanceMatrix.length} entries`);

        addLog('info', 'Đang xây dựng time matrix từ tasks...');
        const timeMatrix = buildTimeMatrix(input.tasks, input.employees, input.aircrafts);
        addLog('info', `Time matrix: ${timeMatrix.length} entries`);

        addLog('info', `Đang chuẩn bị dữ liệu: ${input.aircrafts.length} máy bay, ${input.employees.length} nhân viên`);

        const totalTasks = input.aircrafts.reduce((sum, a) => sum + a.requiredTasks.length, 0);
        addLog('info', `Tổng số tasks cần xếp lịch: ${totalTasks}`);

        // Prepare API input
        const schedulerInput: SchedulerInput = {
            trackingId,
            aircrafts: input.aircrafts,
            employees: input.employees,
            hubs: [], // Empty for now
            matrixConfigs: {
                distanceMatrix,
                timeMatrix,
            },
            config: input.config,
        };

        addLog('info', `Gửi request đến API: ${API_BASE_URL}${ENDPOINTS.SCHEDULER_RUN}`);

        const startTime = performance.now();

        const token = localStorage.getItem('access_token') || '';

        const response = await fetch(`${API_BASE_URL}${ENDPOINTS.SCHEDULER_RUN}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
            },
            body: JSON.stringify(schedulerInput),
        });

        const endTime = performance.now();
        const apiTime = Math.round(endTime - startTime);

        if (!response.ok) {
            const errorText = await response.text();
            addLog('error', `API trả về lỗi: ${response.status}`, { error: errorText });
            throw new Error(`API Error: ${response.status} - ${errorText}`);
        }

        addLog('success', `API phản hồi thành công (${apiTime}ms)`);

        const result: ScheduleResult = await response.json();

        addLog('success', `Kết quả: ${result.status}`, {
            scheduledTasks: result.scheduledTasks.length,
            solveTimeMs: result.solveTimeMs,
        });

        return { result, logs };

    } catch (error) {
        if (error instanceof TypeError && error.message.includes('fetch')) {
            addLog('warning', 'Không thể kết nối đến API. Đang sử dụng mock data...');

            const mockResult = await runMockScheduler(input, (progress) => {
                onProgress?.({ ...progress, logs: [...logs, ...progress.logs] });
            });

            logs.push(...mockResult.logs);
            return { result: mockResult.result, logs };
        }

        addLog('error', `Lỗi: ${error instanceof Error ? error.message : 'Unknown error'}`);
        throw error;
    }
}

async function runMockScheduler(
    input: {
        aircrafts: Aircraft[];
        employees: Employee[];
        tasks: Task[];
        routes: MapRoute[];
        config: SchedulerConfig;
    },
    onProgress?: (progress: SchedulerProgress) => void
): Promise<{ result: ScheduleResult; logs: LogEntry[] }> {
    const logs: LogEntry[] = [];

    const addLog = (level: LogEntry['level'], message: string, details?: Record<string, unknown>) => {
        const log = createLog(level, message, details);
        logs.push(log);
        onProgress?.({
            stage: message,
            progress: 0,
            logs: [...logs]
        });
    };

    addLog('info', '[MOCK] Bắt đầu chạy thuật toán giả lập...');

    await new Promise(resolve => setTimeout(resolve, 500));
    addLog('info', '[MOCK] Xây dựng mô hình...', { algorithm: input.config.algorithm });

    await new Promise(resolve => setTimeout(resolve, 500));
    addLog('info', '[MOCK] Thêm ràng buộc time window...');

    await new Promise(resolve => setTimeout(resolve, 500));
    addLog('info', '[MOCK] Thêm ràng buộc năng lực nhân viên...');

    await new Promise(resolve => setTimeout(resolve, 500));
    addLog('info', '[MOCK] Chạy solver...', { timeLimit: input.config.timeLimit });

    await new Promise(resolve => setTimeout(resolve, 1000));

    const scheduledTasks: ScheduledTask[] = [];
    const now = new Date();
    let taskIndex = 0;

    for (const aircraft of input.aircrafts) {
        for (const reqTask of aircraft.requiredTasks) {
            const assignedEmployee = input.employees[taskIndex % input.employees.length];
            const startTime = new Date(now.getTime() + taskIndex * 30 * 60 * 1000);

            // Find task duration from tasks list
            const taskDef = input.tasks.find(t => t.taskCode === reqTask.taskCode);
            const duration = taskDef?.timeProcess ? Math.round(taskDef.timeProcess / 60) : 30; // Convert to minutes

            const endTime = new Date(startTime.getTime() + duration * 60 * 1000);

            scheduledTasks.push({
                taskId: `task-${taskIndex}`,
                taskCode: reqTask.taskCode,
                aircraftId: aircraft.aircraftId,
                employeeId: assignedEmployee.employeeId,
                employeeName: assignedEmployee.name,
                startTime: startTime.toISOString(),
                endTime: endTime.toISOString(),
                duration,
            });
            taskIndex++;
        }
    }

    addLog('success', `[MOCK] Hoàn thành! Đã xếp ${scheduledTasks.length} tasks`);

    const result: ScheduleResult = {
        status: 'OPTIMAL',
        message: '[MOCK] Tìm được lịch tối ưu (dữ liệu giả lập)',
        scheduledTasks,
        totalCost: scheduledTasks.length * 100,
        solveTimeMs: 2500,
    };

    return { result, logs };
}

export function getApiConfig() {
    return {
        baseUrl: API_BASE_URL,
        endpoints: ENDPOINTS,
        debugEnabled: import.meta.env.VITE_ENABLE_DEBUG_LOGS === 'true',
    };
}
