import type { ScheduledTask } from '@/types/scheduler';

interface GanttTaskBarProps {
    task: ScheduledTask;
    left: number;
    width: number;
    onClick?: () => void;
}

const TASK_COLORS: Record<string, string> = {
    'DEP-M': '#3b82f6',
    'DEP-A': '#60a5fa',
    'ARR-M': '#10b981',
    'ARR-A': '#34d399',
    'FUEL': '#f59e0b',
    'LOAD': '#8b5cf6',
    'UNLOAD': '#a78bfa',
    'CLEAN': '#ec4899',
    'CATERING': '#f43f5e',
    'PUSHBACK': '#6366f1',
    'TOWING': '#4f46e5',
};

function GanttTaskBar({ task, left, width, onClick }: GanttTaskBarProps) {
    let color = '#64748b'; // default gray

    if (task.type === 'BREAK') color = '#F97316'; // Orange
    else if (task.type === 'WALK') color = '#10B981'; // Green
    else if (task.type === 'BUS') color = '#8B5CF6'; // Purple
    else {
        // Default task colors based on task code
        color = TASK_COLORS[task.taskCode] || '#3b82f6'; // Default Blue
    }

    return (
        <div
            onClick={onClick}
            style={{
                position: 'absolute',
                left: `${left}px`,
                top: '8px',
                width: `${width}px`,
                height: '34px',
                background: color,
                borderRadius: '4px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                fontSize: '0.75rem',
                fontWeight: 500,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
                padding: '0 0.25rem',
                boxShadow: '0 1px 3px rgba(0,0,0,0.2)',
                transition: 'transform 0.1s, box-shadow 0.1s',
            }}
            onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'scale(1.02)';
                e.currentTarget.style.boxShadow = '0 2px 6px rgba(0,0,0,0.3)';
            }}
            onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'scale(1)';
                e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.2)';
            }}
            title={`${task.taskCode} - ${task.aircraftId}`}
        >
            {task.taskCode}
        </div>
    );
}

export default GanttTaskBar;
