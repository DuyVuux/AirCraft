import { useState, useMemo, useCallback } from 'react';
import type { Task } from '@/components/editor/TaskEditor';

export interface TaskFilters {
    taskCode: string;
    description: string;
    timeMin: number | null;
    timeMax: number | null;
    certifications: string[];
}

const initialFilters: TaskFilters = {
    taskCode: '',
    description: '',
    timeMin: null,
    timeMax: null,
    certifications: [],
};

export function useTaskFilter(tasks: Task[]) {
    const [filters, setFilters] = useState<TaskFilters>(initialFilters);

    const updateFilter = useCallback(<K extends keyof TaskFilters>(
        key: K,
        value: TaskFilters[K]
    ) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    }, []);

    const clearFilters = useCallback(() => {
        setFilters(initialFilters);
    }, []);

    const hasActiveFilters = useMemo(() => {
        return (
            filters.taskCode !== '' ||
            filters.description !== '' ||
            filters.timeMin !== null ||
            filters.timeMax !== null ||
            filters.certifications.length > 0
        );
    }, [filters]);

    const activeFilterCount = useMemo(() => {
        let count = 0;
        if (filters.taskCode) count++;
        if (filters.description) count++;
        if (filters.timeMin !== null || filters.timeMax !== null) count++;
        if (filters.certifications.length > 0) count++;
        return count;
    }, [filters]);

    const filteredTasks = useMemo(() => {
        return tasks.filter(task => {
            if (filters.taskCode) {
                const searchTerm = filters.taskCode.toLowerCase();
                if (!task.taskCode.toLowerCase().includes(searchTerm)) {
                    return false;
                }
            }

            if (filters.description) {
                const searchTerm = filters.description.toLowerCase();
                const taskDesc = (task.description || '').toLowerCase();
                if (!taskDesc.includes(searchTerm)) {
                    return false;
                }
            }

            const taskTimeMinutes = (task.timeProcess || 0) / 60;
            if (filters.timeMin !== null && taskTimeMinutes < filters.timeMin) {
                return false;
            }
            if (filters.timeMax !== null && taskTimeMinutes > filters.timeMax) {
                return false;
            }

            if (filters.certifications.length > 0) {
                const taskCerts = task.requiredCertifications || [];
                if (taskCerts.length === 0) {
                    return false;
                }
                const hasMatchingCert = filters.certifications.some(cert =>
                    taskCerts.includes(cert)
                );
                if (!hasMatchingCert) {
                    return false;
                }
            }

            return true;
        });
    }, [tasks, filters]);

    return {
        filters,
        updateFilter,
        clearFilters,
        hasActiveFilters,
        activeFilterCount,
        filteredTasks,
        totalCount: tasks.length,
        filteredCount: filteredTasks.length,
    };
}

export default useTaskFilter;
