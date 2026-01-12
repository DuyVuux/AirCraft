import { useState } from 'react';
import { useHistory, type HistoryEntry } from '@/contexts/HistoryContext';
import Layout from '@/components/layout/Layout';
import './HistoryPage.css';

function StatusBadge({ status }: { status: HistoryEntry['status'] }) {
    const statusConfig = {
        OPTIMAL: { label: 'Tối ưu', className: 'status-optimal' },
        FEASIBLE: { label: 'Khả thi', className: 'status-feasible' },
        INFEASIBLE: { label: 'Không khả thi', className: 'status-infeasible' },
        ERROR: { label: 'Lỗi', className: 'status-error' },
    };
    const config = statusConfig[status];
    return <span className={`status-badge ${config.className}`}>{config.label}</span>;
}

function LogLevelBadge({ level }: { level: 'info' | 'warning' | 'error' | 'success' }) {
    const levelConfig = {
        info: { label: 'INFO', className: 'log-info' },
        warning: { label: 'WARN', className: 'log-warning' },
        error: { label: 'ERROR', className: 'log-error' },
        success: { label: 'OK', className: 'log-success' },
    };
    const config = levelConfig[level];
    return <span className={`log-badge ${config.className}`}>{config.label}</span>;
}

export default function HistoryPage() {
    const { entries, clearHistory, deleteEntry } = useHistory();
    const [selectedEntry, setSelectedEntry] = useState<HistoryEntry | null>(null);
    const [activeTab, setActiveTab] = useState<'logs' | 'result'>('logs');

    const formatTime = (isoString: string) => {
        const date = new Date(isoString);
        return date.toLocaleString('vi-VN', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
        });
    };

    const handleClearAll = () => {
        if (window.confirm('Xóa toàn bộ lịch sử?')) {
            clearHistory();
            setSelectedEntry(null);
        }
    };

    return (
        <Layout>
            <div className="history-page">
                <div className="history-header">
                    <h1>Lịch sử hoạt động</h1>
                    {entries.length > 0 && (
                        <button className="btn-clear" onClick={handleClearAll}>
                            <span className="material-symbols-outlined">delete_sweep</span>
                            Xóa tất cả
                        </button>
                    )}
                </div>

                {entries.length === 0 ? (
                    <div className="empty-state">
                        <span className="material-symbols-outlined">history</span>
                        <p>Chưa có lịch sử chạy scheduler</p>
                        <p className="hint">Chạy scheduler để xem kết quả ở đây</p>
                    </div>
                ) : (
                    <div className="history-content">
                        <div className="history-list">
                            {entries.map(entry => (
                                <div
                                    key={entry.id}
                                    className={`history-item ${selectedEntry?.id === entry.id ? 'selected' : ''}`}
                                    onClick={() => setSelectedEntry(entry)}
                                >
                                    <div className="history-item-header">
                                        <StatusBadge status={entry.status} />
                                        <span className="history-time">{formatTime(entry.timestamp)}</span>
                                    </div>
                                    <div className="history-item-stats">
                                        <span>{entry.taskCount} tasks</span>
                                        <span>{entry.employeeCount} NV</span>
                                        <span>{entry.aircraftCount} MB</span>
                                    </div>
                                    <button
                                        className="btn-delete-item"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            deleteEntry(entry.id);
                                            if (selectedEntry?.id === entry.id) setSelectedEntry(null);
                                        }}
                                    >
                                        <span className="material-symbols-outlined">close</span>
                                    </button>
                                </div>
                            ))}
                        </div>

                        {selectedEntry && (
                            <div className="history-detail">
                                <div className="detail-header">
                                    <h2>Chi tiết</h2>
                                    <div className="detail-tabs">
                                        <button
                                            className={activeTab === 'logs' ? 'active' : ''}
                                            onClick={() => setActiveTab('logs')}
                                        >
                                            Logs ({selectedEntry.logs.length})
                                        </button>
                                        <button
                                            className={activeTab === 'result' ? 'active' : ''}
                                            onClick={() => setActiveTab('result')}
                                        >
                                            Kết quả
                                        </button>
                                    </div>
                                </div>

                                {activeTab === 'logs' && (
                                    <div className="logs-container">
                                        {selectedEntry.logs.map((log, idx) => (
                                            <div key={idx} className="log-entry">
                                                <span className="log-time">
                                                    {new Date(log.timestamp).toLocaleTimeString('vi-VN')}
                                                </span>
                                                <LogLevelBadge level={log.level} />
                                                <span className="log-message">{log.message}</span>
                                            </div>
                                        ))}
                                        {selectedEntry.error && (
                                            <div className="error-block">
                                                <h4>Lỗi:</h4>
                                                <pre>{selectedEntry.error}</pre>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {activeTab === 'result' && selectedEntry.result && (
                                    <div className="result-container">
                                        <div className="result-stats">
                                            <div className="stat">
                                                <span className="stat-label">Trạng thái</span>
                                                <StatusBadge status={selectedEntry.status} />
                                            </div>
                                            <div className="stat">
                                                <span className="stat-label">Tasks đã xếp</span>
                                                <span className="stat-value">{selectedEntry.result.scheduledTasks.length}</span>
                                            </div>
                                            {selectedEntry.result.solveTimeMs && (
                                                <div className="stat">
                                                    <span className="stat-label">Thời gian solve</span>
                                                    <span className="stat-value">{selectedEntry.result.solveTimeMs}ms</span>
                                                </div>
                                            )}
                                        </div>
                                        {selectedEntry.result.message && (
                                            <div className="result-message">
                                                <p>{selectedEntry.result.message}</p>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </Layout>
    );
}
