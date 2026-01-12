import { useState } from 'react';
import type { ScheduleResult } from '@/types/scheduler';

interface AlgorithmRunnerProps {
    onRunComplete: (result: ScheduleResult) => void;
    disabled?: boolean;
}

function AlgorithmRunner({ onRunComplete, disabled = false }: AlgorithmRunnerProps) {
    const [isRunning, setIsRunning] = useState(false);
    const [lastResult, setLastResult] = useState<ScheduleResult | null>(null);

    const handleRun = async () => {
        setIsRunning(true);
        setLastResult(null);

        try {
            // TODO: Call actual API endpoint
            // Simulating API call for now
            await new Promise(resolve => setTimeout(resolve, 2000));

            const mockResult: ScheduleResult = {
                status: 'OPTIMAL',
                message: 'Tìm được lịch tối ưu',
                scheduledTasks: [],
                totalCost: 0,
                solveTimeMs: 1234,
            };

            setLastResult(mockResult);
            onRunComplete(mockResult);
        } catch (error) {
            const errorResult: ScheduleResult = {
                status: 'ERROR',
                message: error instanceof Error ? error.message : 'Có lỗi xảy ra',
                scheduledTasks: [],
            };
            setLastResult(errorResult);
            onRunComplete(errorResult);
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

    return (
        <div className="editor-card">
            <h3 className="editor-card-title">Chạy thuật toán</h3>

            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginTop: '1rem' }}>
                <button
                    className="editor-form-button-primary"
                    onClick={handleRun}
                    disabled={disabled || isRunning}
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        opacity: (disabled || isRunning) ? 0.6 : 1,
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

                {lastResult && (
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.5rem 1rem',
                        borderRadius: '0.5rem',
                        background: `${getStatusColor(lastResult.status)}20`,
                        color: getStatusColor(lastResult.status),
                    }}>
                        <span className="material-symbols-outlined">{getStatusIcon(lastResult.status)}</span>
                        <span style={{ fontWeight: 500 }}>{lastResult.status}</span>
                        {lastResult.solveTimeMs && (
                            <span style={{ fontSize: '0.875rem', opacity: 0.8 }}>
                                ({lastResult.solveTimeMs}ms)
                            </span>
                        )}
                    </div>
                )}
            </div>

            {lastResult?.message && (
                <p style={{ marginTop: '0.75rem', fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>
                    {lastResult.message}
                </p>
            )}

            <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
        </div>
    );
}

export default AlgorithmRunner;
