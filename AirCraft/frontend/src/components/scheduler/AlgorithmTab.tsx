import { useState, useEffect } from 'react';
import type { ScheduleResult } from '@/types/scheduler';
import type { Aircraft } from '@/types/aircraft';
import type { Employee } from '@/types/employee';
import { runScheduler, getApiConfig, fetchAlgorithms, type LogEntry, type SchedulerConfig, type AlgorithmOption, type OptimizeOption } from '@/services/schedulerApi';
import { useGlobalData } from '@/contexts/GlobalDataContext';
import { useHistory } from '@/contexts/HistoryContext';

interface AlgorithmTabProps {
    aircrafts: Aircraft[];
    employees: Employee[];
    onRunComplete: (result: ScheduleResult) => void;
}

function AlgorithmTab({ aircrafts, employees, onRunComplete }: AlgorithmTabProps) {
    const { tasks, mapRoutes } = useGlobalData();
    const { addEntry } = useHistory();
    const [isRunning, setIsRunning] = useState(false);
    const [lastResult, setLastResult] = useState<ScheduleResult | null>(null);
    const [logs, setLogs] = useState<LogEntry[]>([]);

    const [algorithms, setAlgorithms] = useState<AlgorithmOption[]>([]);
    const [optimizeOptions, setOptimizeOptions] = useState<OptimizeOption[]>([]);
    const [isLoadingConfig, setIsLoadingConfig] = useState(true);
    const [config, setConfig] = useState<SchedulerConfig>({
        algorithm: '',
        timeLimit: 60,
        optimizeFor: '',
    });

    useEffect(() => {
        const loadAlgorithms = async () => {
            setIsLoadingConfig(true);
            const response = await fetchAlgorithms();
            setAlgorithms(response.algorithms);
            setOptimizeOptions(response.optimizeOptions);
            setConfig({
                algorithm: response.algorithms[0]?.id || '',
                timeLimit: response.defaultTimeLimit,
                optimizeFor: response.optimizeOptions[0]?.id || '',
            });
            setIsLoadingConfig(false);
        };
        loadAlgorithms();
    }, []);

    const apiConfig = getApiConfig();
    const totalTasks = aircrafts.reduce((sum, a) => sum + a.requiredTasks.length, 0);
    const isInputValid = aircrafts.length > 0 && employees.length > 0 && totalTasks > 0 && config.algorithm !== '';

    const handleRun = async () => {
        setIsRunning(true);
        setLastResult(null);
        setLogs([]);

        let finalLogs: LogEntry[] = [];
        let errorMessage: string | undefined;

        try {
            const { result, logs: executionLogs } = await runScheduler(
                {
                    aircrafts,
                    employees,
                    tasks,
                    routes: mapRoutes,
                    config
                },
                (progress) => {
                    setLogs([...progress.logs]);
                }
            );

            finalLogs = executionLogs;
            setLastResult(result);
            setLogs(executionLogs);
            onRunComplete(result);

            addEntry({
                status: result.status,
                result,
                logs: executionLogs,
                config,
                taskCount: totalTasks,
                employeeCount: employees.length,
                aircraftCount: aircrafts.length,
            });
        } catch (error) {
            errorMessage = error instanceof Error ? error.message : 'Có lỗi xảy ra';
            const errorResult: ScheduleResult = {
                status: 'ERROR',
                message: errorMessage,
                scheduledTasks: [],
            };
            setLastResult(errorResult);
            onRunComplete(errorResult);

            addEntry({
                status: 'ERROR',
                result: errorResult,
                logs: finalLogs,
                error: errorMessage,
                config,
                taskCount: totalTasks,
                employeeCount: employees.length,
                aircraftCount: aircrafts.length,
            });
        } finally {
            setIsRunning(false);
        }
    };

    const getStatusColor = (status: ScheduleResult['status']) => {
        switch (status) {
            case 'OPTIMAL': return '#10b981';
            case 'FEASIBLE': return '#f59e0b';
            case 'INFEASIBLE': return '#ef4444';
            case 'ERROR': return '#ef4444';
            default: return 'var(--color-text-secondary)';
        }
    };

    const getStatusIcon = (status: ScheduleResult['status']) => {
        switch (status) {
            case 'OPTIMAL': return 'check_circle';
            case 'FEASIBLE': return 'info';
            case 'INFEASIBLE': return 'error';
            case 'ERROR': return 'error';
            default: return 'help';
        }
    };

    const getLogColor = (level: LogEntry['level']) => {
        switch (level) {
            case 'info': return '#3b82f6';
            case 'warning': return '#f59e0b';
            case 'error': return '#ef4444';
            case 'success': return '#10b981';
            default: return 'var(--color-text-secondary)';
        }
    };

    const getLogIcon = (level: LogEntry['level']) => {
        switch (level) {
            case 'info': return 'info';
            case 'warning': return 'warning';
            case 'error': return 'error';
            case 'success': return 'check_circle';
            default: return 'circle';
        }
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* API Configuration */}
            <div className="editor-card">
                <h3 className="editor-card-title">Cấu hình API</h3>
                <div style={{
                    marginTop: '1rem',
                    padding: '0.75rem',
                    background: 'var(--color-surface-elevated)',
                    borderRadius: '0.5rem',
                    fontSize: '0.875rem',
                    fontFamily: 'monospace',
                }}>
                    <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem' }}>
                        <span style={{ color: 'var(--color-text-secondary)' }}>Base URL:</span>
                        <span style={{ color: '#3b82f6' }}>{apiConfig.baseUrl}</span>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <span style={{ color: 'var(--color-text-secondary)' }}>Endpoint:</span>
                        <span style={{ color: '#10b981' }}>{apiConfig.endpoints.SCHEDULER_RUN}</span>
                    </div>
                </div>
            </div>

            {/* Cấu hình thuật toán */}
            <div className="editor-card">
                <h3 className="editor-card-title">Cấu hình thuật toán</h3>
                {isLoadingConfig ? (
                    <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--color-text-secondary)' }}>
                        Đang tải cấu hình...
                    </div>
                ) : (
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(3, 1fr)',
                        gap: '1.5rem',
                        marginTop: '1rem'
                    }}>
                        <div className="editor-form-group">
                            <label className="editor-form-label">Thuật toán</label>
                            <select
                                className="editor-form-input"
                                value={config.algorithm}
                                onChange={(e) => setConfig({ ...config, algorithm: e.target.value })}
                                disabled={isRunning}
                            >
                                {algorithms.map(algo => (
                                    <option key={algo.id} value={algo.id}>{algo.name}</option>
                                ))}
                            </select>
                        </div>
                        <div className="editor-form-group">
                            <label className="editor-form-label">Giới hạn thời gian (giây)</label>
                            <input
                                type="number"
                                className="editor-form-input"
                                value={config.timeLimit}
                                onChange={(e) => setConfig({ ...config, timeLimit: parseInt(e.target.value) || 60 })}
                                min={1}
                                max={3600}
                                disabled={isRunning}
                            />
                        </div>
                        <div className="editor-form-group">
                            <label className="editor-form-label">Tối ưu theo</label>
                            <select
                                className="editor-form-input"
                                value={config.optimizeFor}
                                onChange={(e) => setConfig({ ...config, optimizeFor: e.target.value })}
                                disabled={isRunning}
                            >
                                {optimizeOptions.map(opt => (
                                    <option key={opt.id} value={opt.id}>{opt.name}</option>
                                ))}
                            </select>
                        </div>
                    </div>
                )}
            </div>

            {/* Kiểm tra điều kiện */}
            <div className="editor-card">
                <h3 className="editor-card-title">Kiểm tra điều kiện</h3>
                <div style={{ marginTop: '1rem' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            padding: '0.75rem',
                            background: aircrafts.length > 0 ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                            borderRadius: '0.5rem',
                        }}>
                            <span
                                className="material-symbols-outlined"
                                style={{ color: aircrafts.length > 0 ? '#10b981' : '#ef4444' }}
                            >
                                {aircrafts.length > 0 ? 'check_circle' : 'cancel'}
                            </span>
                            <span>Có máy bay: {aircrafts.length} máy bay</span>
                        </div>
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            padding: '0.75rem',
                            background: employees.length > 0 ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                            borderRadius: '0.5rem',
                        }}>
                            <span
                                className="material-symbols-outlined"
                                style={{ color: employees.length > 0 ? '#10b981' : '#ef4444' }}
                            >
                                {employees.length > 0 ? 'check_circle' : 'cancel'}
                            </span>
                            <span>Có nhân viên: {employees.length} nhân viên</span>
                        </div>
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            padding: '0.75rem',
                            background: totalTasks > 0 ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                            borderRadius: '0.5rem',
                        }}>
                            <span
                                className="material-symbols-outlined"
                                style={{ color: totalTasks > 0 ? '#10b981' : '#ef4444' }}
                            >
                                {totalTasks > 0 ? 'check_circle' : 'cancel'}
                            </span>
                            <span>Có tasks cần xếp lịch: {totalTasks} tasks</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Nút chạy */}
            <div className="editor-card">
                <h3 className="editor-card-title">Chạy thuật toán</h3>
                <div style={{ marginTop: '1rem' }}>
                    <button
                        className="editor-form-button-primary"
                        onClick={handleRun}
                        disabled={!isInputValid || isRunning}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            padding: '0.75rem 1.5rem',
                            fontSize: '1rem',
                            opacity: (!isInputValid || isRunning) ? 0.6 : 1,
                        }}
                    >
                        {isRunning ? (
                            <>
                                <span className="material-symbols-outlined" style={{ animation: 'spin 1s linear infinite' }}>sync</span>
                                Đang chạy...
                            </>
                        ) : (
                            <>
                                <span className="material-symbols-outlined">play_arrow</span>
                                Chạy Scheduler
                            </>
                        )}
                    </button>

                    {!isInputValid && (
                        <p style={{ marginTop: '0.75rem', color: '#ef4444', fontSize: '0.875rem' }}>
                            Vui lòng đảm bảo có đủ máy bay, nhân viên và tasks trước khi chạy.
                        </p>
                    )}
                </div>

                {lastResult && (
                    <div style={{
                        marginTop: '1.5rem',
                        padding: '1rem',
                        borderRadius: '0.5rem',
                        background: `${getStatusColor(lastResult.status)}15`,
                        border: `1px solid ${getStatusColor(lastResult.status)}40`,
                    }}>
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem',
                            color: getStatusColor(lastResult.status),
                            fontWeight: 600,
                        }}>
                            <span className="material-symbols-outlined">{getStatusIcon(lastResult.status)}</span>
                            <span>{lastResult.status}</span>
                            {lastResult.solveTimeMs && (
                                <span style={{ fontWeight: 400, opacity: 0.8 }}>
                                    ({lastResult.solveTimeMs}ms)
                                </span>
                            )}
                        </div>
                        {lastResult.message && (
                            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
                                {lastResult.message}
                            </p>
                        )}
                    </div>
                )}
            </div>

            {/* Execution Logs */}
            <div className="editor-card">
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <h3 className="editor-card-title">Execution Logs</h3>
                    {logs.length > 0 && (
                        <button
                            className="editor-form-button-secondary"
                            onClick={() => setLogs([])}
                            style={{ padding: '0.25rem 0.75rem', fontSize: '0.75rem' }}
                        >
                            Xóa logs
                        </button>
                    )}
                </div>
                <div style={{
                    marginTop: '1rem',
                    maxHeight: '300px',
                    overflowY: 'auto',
                    background: '#0d1117',
                    borderRadius: '0.5rem',
                    padding: '1rem',
                    fontFamily: 'monospace',
                    fontSize: '0.8rem',
                }}>
                    {logs.length === 0 ? (
                        <div style={{ color: '#8b949e', textAlign: 'center', padding: '2rem' }}>
                            Chưa có logs. Nhấn "Chạy Scheduler" để bắt đầu.
                        </div>
                    ) : (
                        logs.map((log, index) => (
                            <div
                                key={index}
                                style={{
                                    display: 'flex',
                                    gap: '0.75rem',
                                    padding: '0.375rem 0',
                                    borderBottom: index < logs.length - 1 ? '1px solid #21262d' : 'none',
                                }}
                            >
                                <span style={{ color: '#8b949e', fontSize: '0.7rem', minWidth: '80px' }}>
                                    {new Date(log.timestamp).toLocaleTimeString('vi-VN', {
                                        hour: '2-digit',
                                        minute: '2-digit',
                                        second: '2-digit'
                                    })}
                                </span>
                                <span
                                    className="material-symbols-outlined"
                                    style={{ color: getLogColor(log.level), fontSize: '1rem' }}
                                >
                                    {getLogIcon(log.level)}
                                </span>
                                <span style={{ color: '#c9d1d9', flex: 1 }}>{log.message}</span>
                                {log.details && (
                                    <span style={{ color: '#8b949e', fontSize: '0.7rem' }}>
                                        {JSON.stringify(log.details)}
                                    </span>
                                )}
                            </div>
                        ))
                    )}
                </div>
            </div>

            <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
        </div>
    );
}

export default AlgorithmTab;
