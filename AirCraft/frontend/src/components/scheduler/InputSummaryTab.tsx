import type { Aircraft } from '@/types/aircraft';
import type { Employee } from '@/types/employee';

interface InputSummaryTabProps {
    aircrafts: Aircraft[];
    employees: Employee[];
}

function InputSummaryTab({ aircrafts, employees }: InputSummaryTabProps) {
    const formatUTCTime = (isoString: string) => {
        if (!isoString) return '';
        const date = new Date(isoString);
        return `${date.getUTCHours().toString().padStart(2, '0')}:${date.getUTCMinutes().toString().padStart(2, '0')}`;
    };

    const totalTasks = aircrafts.reduce((sum, a) => sum + a.requiredTasks.length, 0);
    const totalCapabilities = employees.reduce((sum, e) => sum + (e.taskCapabilities?.length || 0), 0);

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Tổng quan */}
            <div className="editor-card">
                <h3 className="editor-card-title">Tổng quan dữ liệu</h3>
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(4, 1fr)',
                    gap: '1rem',
                    marginTop: '1rem'
                }}>
                    <div style={{
                        padding: '1rem',
                        background: 'rgba(59, 130, 246, 0.1)',
                        borderRadius: '0.5rem',
                        textAlign: 'center'
                    }}>
                        <div style={{ fontSize: '2rem', fontWeight: 700, color: '#3b82f6' }}>{aircrafts.length}</div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Máy bay</div>
                    </div>
                    <div style={{
                        padding: '1rem',
                        background: 'rgba(16, 185, 129, 0.1)',
                        borderRadius: '0.5rem',
                        textAlign: 'center'
                    }}>
                        <div style={{ fontSize: '2rem', fontWeight: 700, color: '#10b981' }}>{employees.length}</div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Nhân viên</div>
                    </div>
                    <div style={{
                        padding: '1rem',
                        background: 'rgba(245, 158, 11, 0.1)',
                        borderRadius: '0.5rem',
                        textAlign: 'center'
                    }}>
                        <div style={{ fontSize: '2rem', fontWeight: 700, color: '#f59e0b' }}>{totalTasks}</div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Tổng tasks</div>
                    </div>
                    <div style={{
                        padding: '1rem',
                        background: 'rgba(139, 92, 246, 0.1)',
                        borderRadius: '0.5rem',
                        textAlign: 'center'
                    }}>
                        <div style={{ fontSize: '2rem', fontWeight: 700, color: '#8b5cf6' }}>{totalCapabilities}</div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Năng lực NV</div>
                    </div>
                </div>
            </div>

            {/* Chi tiết máy bay */}
            <div className="editor-card">
                <h3 className="editor-card-title">Chi tiết máy bay ({aircrafts.length})</h3>
                <div style={{ marginTop: '1rem', overflowX: 'auto' }}>
                    {aircrafts.length === 0 ? (
                        <p style={{ color: 'var(--color-text-secondary)', textAlign: 'center', padding: '2rem' }}>
                            Chưa có máy bay. Vui lòng nhập dữ liệu ở tab "Nhập dữ liệu".
                        </p>
                    ) : (
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                            <thead>
                                <tr style={{ borderBottom: '2px solid var(--color-border)' }}>
                                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Mã máy bay</th>
                                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Loại</th>
                                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Vị trí đỗ</th>
                                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Time Window</th>
                                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Tasks yêu cầu</th>
                                </tr>
                            </thead>
                            <tbody>
                                {aircrafts.map((ac) => (
                                    <tr key={ac.aircraftId} style={{ borderBottom: '1px solid var(--color-border)' }}>
                                        <td style={{ padding: '0.75rem', fontWeight: 500 }}>{ac.aircraftId}</td>
                                        <td style={{ padding: '0.75rem' }}>{ac.aircraftType || 'N/A'}</td>
                                        <td style={{ padding: '0.75rem' }}>{ac.location?.locationId || 'Chưa gán'}</td>
                                        <td style={{ padding: '0.75rem', fontSize: '0.75rem' }}>
                                            {ac.timeWindow ? (
                                                <>
                                                    {formatUTCTime(ac.timeWindow.start)}
                                                    {' - '}
                                                    {formatUTCTime(ac.timeWindow.end)}
                                                </>
                                            ) : 'N/A'}
                                        </td>
                                        <td style={{ padding: '0.75rem' }}>
                                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                                                {ac.requiredTasks.length > 0 ? (
                                                    ac.requiredTasks.map((task, idx) => (
                                                        <span
                                                            key={idx}
                                                            style={{
                                                                fontSize: '0.7rem',
                                                                padding: '0.125rem 0.5rem',
                                                                borderRadius: '0.75rem',
                                                                background: 'rgba(59, 130, 246, 0.2)',
                                                                color: '#3b82f6',
                                                            }}
                                                        >
                                                            {task.taskCode}
                                                        </span>
                                                    ))
                                                ) : (
                                                    <span style={{ color: 'var(--color-text-secondary)' }}>Không có</span>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>

            {/* Chi tiết nhân viên */}
            <div className="editor-card">
                <h3 className="editor-card-title">Chi tiết nhân viên ({employees.length})</h3>
                <div style={{ marginTop: '1rem', overflowX: 'auto' }}>
                    {employees.length === 0 ? (
                        <p style={{ color: 'var(--color-text-secondary)', textAlign: 'center', padding: '2rem' }}>
                            Chưa có nhân viên. Vui lòng nhập dữ liệu ở tab "Nhập dữ liệu".
                        </p>
                    ) : (
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                            <thead>
                                <tr style={{ borderBottom: '2px solid var(--color-border)' }}>
                                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Mã NV</th>
                                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Tên</th>
                                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Chức danh</th>
                                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Vai trò</th>
                                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Ca làm việc</th>
                                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Năng lực</th>
                                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Chứng chỉ</th>
                                </tr>
                            </thead>
                            <tbody>
                                {employees.map((emp) => (
                                    <tr key={emp.employeeId} style={{ borderBottom: '1px solid var(--color-border)' }}>
                                        <td style={{ padding: '0.75rem', fontWeight: 500 }}>{emp.employeeId}</td>
                                        <td style={{ padding: '0.75rem' }}>{emp.name || 'N/A'}</td>
                                        <td style={{ padding: '0.75rem' }}>{emp.position || 'N/A'}</td>
                                        <td style={{ padding: '0.75rem' }}>{emp.eType?.role || 'N/A'}</td>
                                        <td style={{ padding: '0.75rem', fontSize: '0.75rem' }}>
                                            {emp.workingTimes?.length > 0 ? (
                                                emp.workingTimes.map((wt, idx) => (
                                                    <div key={idx}>
                                                        {wt.start && wt.end ? (
                                                            <>
                                                                {formatUTCTime(wt.start)}
                                                                {' - '}
                                                                {formatUTCTime(wt.end)}
                                                            </>
                                                        ) : 'Chưa cấu hình'}
                                                    </div>
                                                ))
                                            ) : 'N/A'}
                                        </td>
                                        <td style={{ padding: '0.75rem' }}>
                                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                                                {(emp.taskCapabilities || []).length > 0 ? (
                                                    (emp.taskCapabilities || []).map((cap, idx) => (
                                                        <span
                                                            key={idx}
                                                            style={{
                                                                fontSize: '0.7rem',
                                                                padding: '0.125rem 0.5rem',
                                                                borderRadius: '0.75rem',
                                                                background: 'rgba(16, 185, 129, 0.2)',
                                                                color: '#10b981',
                                                            }}
                                                        >
                                                            {cap}
                                                        </span>
                                                    ))
                                                ) : (
                                                    <span style={{ color: 'var(--color-text-secondary)' }}>Không có</span>
                                                )}
                                            </div>
                                        </td>
                                        <td style={{ padding: '0.75rem' }}>
                                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                                                {(emp.certifications || []).length > 0 ? (
                                                    (emp.certifications || []).map((cert, idx) => (
                                                        <span
                                                            key={idx}
                                                            style={{
                                                                fontSize: '0.7rem',
                                                                padding: '0.125rem 0.5rem',
                                                                borderRadius: '0.75rem',
                                                                background: 'rgba(245, 158, 11, 0.2)',
                                                                color: '#f59e0b',
                                                            }}
                                                        >
                                                            {cert}
                                                        </span>
                                                    ))
                                                ) : (
                                                    <span style={{ color: 'var(--color-text-secondary)' }}>Không có</span>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
}

export default InputSummaryTab;
