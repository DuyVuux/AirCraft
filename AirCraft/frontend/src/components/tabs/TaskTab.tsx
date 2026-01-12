import type { TabProps, TabConfig } from './types';
import TaskEditor, { TaskList, type Task } from '@/components/editor/TaskEditor';
import UploadButton from '@/components/upload/UploadButton';
import type { ParseResult } from '@/services/csvParser';
import { downloadTemplate } from '@/services/csvParser';

export const tabConfig: TabConfig = {
    id: 'tasks',
    label: 'TASKS',
    order: 0,
};

const TASK_TEMPLATE_HEADERS = [
    'Mã Task',
    'Tên Task (Viết tắt)',
    'Tên Đầy Đủ (Tiếng Việt)',
    'Thời Gian (giây)',
    'Mô Tả & Ý Nghĩa Thực Tế',
];

const TASK_SAMPLE_ROWS = [
    ['ARR-M', 'Arrival (Main)', 'Thợ chính Đón tàu', '600', 'Kỹ sư chịu trách nhiệm chính tại bãi đỗ khi tàu về'],
    ['DEP-A', 'Departure (Assist)', 'Trợ lý Tiễn tàu', '600', 'Thợ máy hỗ trợ: Rút chèn, ngắt điện, đóng cửa'],
    ['WO-01', 'Work Order 01', 'Kiểm tra Quá cảnh', '600', 'Kiểm tra kỹ thuật nhanh giữa 2 chuyến bay'],
];

export default function TaskTab({
    tasks,
    setTasks,
    editingTask,
    handleTaskSave,
    handleTaskDelete,
    handleTaskEdit,
}: TabProps) {

    const handleUpload = (result: ParseResult) => {
        if (result.errors.length > 0) {
            console.error('Upload errors:', result.errors);
            return;
        }

        const newTasks: Task[] = result.rows.map((row) => {
            const timeSeconds = parseInt(row['Thời Gian (giây)'] || '600'); // Default 10 minutes

            return {
                taskCode: row['Mã Task'] || '',
                description: row['Tên Đầy Đủ (Tiếng Việt)'] || row['Mô Tả & Ý Nghĩa Thực Tế'] || '',
                timeProcess: timeSeconds, // Already in seconds
                requiredCertifications: [], // Can be added manually later
            };
        });

        const existingCodes = new Set(tasks.map(t => t.taskCode));
        const uniqueTasks = newTasks.filter(t => !existingCodes.has(t.taskCode));
        setTasks([...tasks, ...uniqueTasks]);
    };

    const handleDownload = () => {
        const rows = tasks.map(task => [
            task.taskCode,
            '', // Tên Task (Viết tắt) - không có trong data
            task.description || '',
            String(task.timeProcess || 600),
            task.description || '', // Mô Tả
        ]);
        downloadTemplate('tasks_export.csv', TASK_TEMPLATE_HEADERS, rows);
    };

    return (
        <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ margin: 0 }}>Thêm Task Mới</h3>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                        onClick={handleDownload}
                        disabled={tasks.length === 0}
                        className="dataset-btn"
                        style={{
                            opacity: tasks.length === 0 ? 0.5 : 1,
                            cursor: tasks.length === 0 ? 'not-allowed' : 'pointer'
                        }}
                    >
                        <span className="material-symbols-outlined">download</span>
                        Download CSV ({tasks.length})
                    </button>
                    <UploadButton
                        label="Upload Tasks"
                        templateHeaders={TASK_TEMPLATE_HEADERS}
                        templateFilename="tasks_template.csv"
                        sampleRows={TASK_SAMPLE_ROWS}
                        onDataParsed={handleUpload}
                    />
                </div>
            </div>
            <TaskEditor
                onSave={handleTaskSave}
                onDelete={handleTaskDelete}
                initialData={editingTask}
                existingTasks={tasks}
            />
            <TaskList
                tasks={tasks}
                onEdit={handleTaskEdit}
                onDelete={handleTaskDelete}
            />
        </>
    );
}
