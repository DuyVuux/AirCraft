import { useState } from 'react';
import Layout from '@/components/layout/Layout';
import { useGlobalData } from '@/contexts/GlobalDataContext';
import InputSummaryTab from '@/components/scheduler/InputSummaryTab';
import AlgorithmTab from '@/components/scheduler/AlgorithmTab';
import ResultsTab from '@/components/scheduler/ResultsTab';
import type { ScheduleResult } from '@/types/scheduler';

const SCHEDULER_TABS = [
    { id: 'input', label: 'Dữ liệu đầu vào', icon: 'summarize' },
    { id: 'algorithm', label: 'Chạy thuật toán', icon: 'play_circle' },
    { id: 'results', label: 'Kết quả', icon: 'bar_chart' },
];

function SchedulerPage() {
    const { aircrafts, employees, isLoading } = useGlobalData();
    const [activeTab, setActiveTab] = useState(0);
    const [scheduleResult, setScheduleResult] = useState<ScheduleResult | null>(null);

    const handleRunComplete = (result: ScheduleResult) => {
        setScheduleResult(result);
        setActiveTab(2);
    };

    return (
        <Layout title="Scheduler" description="Chạy thuật toán tối ưu và xem kết quả" showSharedHeader={true}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', padding: '1rem' }}>
                {isLoading && (
                    <div style={{ textAlign: 'center', padding: '2rem' }}>
                        <span className="material-symbols-outlined" style={{ animation: 'spin 1s linear infinite' }}>sync</span>
                        <p>Đang tải dữ liệu...</p>
                    </div>
                )}

                {/* Tab navigation */}
                <div style={{
                    display: 'flex',
                    gap: '0.5rem',
                    borderBottom: '1px solid var(--color-border)',
                    paddingBottom: '0.5rem',
                }}>
                    {SCHEDULER_TABS.map((tab, index) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(index)}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                padding: '0.75rem 1.25rem',
                                background: activeTab === index ? 'var(--color-primary)' : 'transparent',
                                color: activeTab === index ? '#fff' : 'var(--color-text-secondary)',
                                border: 'none',
                                borderRadius: '0.5rem 0.5rem 0 0',
                                cursor: 'pointer',
                                fontSize: '0.875rem',
                                fontWeight: activeTab === index ? 600 : 400,
                                transition: 'all 0.2s',
                            }}
                        >
                            <span className="material-symbols-outlined" style={{ fontSize: '1.25rem' }}>{tab.icon}</span>
                            {tab.label}
                            {tab.id === 'results' && scheduleResult && (
                                <span style={{
                                    background: scheduleResult.status === 'OPTIMAL' ? '#10b981' : '#f59e0b',
                                    color: '#fff',
                                    fontSize: '0.7rem',
                                    padding: '0.125rem 0.375rem',
                                    borderRadius: '0.5rem',
                                }}>
                                    {scheduleResult.scheduledTasks.length}
                                </span>
                            )}
                        </button>
                    ))}
                </div>

                {/* Tab content */}
                <div style={{ minHeight: '60vh' }}>
                    {activeTab === 0 && (
                        <InputSummaryTab aircrafts={aircrafts} employees={employees} />
                    )}
                    {activeTab === 1 && (
                        <AlgorithmTab
                            aircrafts={aircrafts}
                            employees={employees}
                            onRunComplete={handleRunComplete}
                        />
                    )}
                    {activeTab === 2 && (
                        <ResultsTab
                            scheduleResult={scheduleResult}
                            employees={employees}
                        />
                    )}
                </div>
            </div>

            <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
        </Layout>
    );
}

export default SchedulerPage;
