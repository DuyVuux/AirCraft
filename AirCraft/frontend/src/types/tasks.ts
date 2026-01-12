/**
 * Danh sách các task có sẵn trong hệ thống
 * Đọc từ file config/tasks.txt
 */
import tasksRaw from '../../config/tasks.txt?raw';

export const AVAILABLE_TASKS = tasksRaw
    .split('\n')
    .map((line: string) => line.trim())
    .filter((line: string) => line.length > 0);

export type TaskCode = string;
