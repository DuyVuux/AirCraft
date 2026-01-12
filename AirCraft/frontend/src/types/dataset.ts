import type { Task } from '@/components/editor/TaskEditor';
import type { Aircraft } from '@/types/aircraft';
import type { Employee } from '@/types/employee';
import type { TimeMatrixEntry } from '@/types/matrix';

export interface DatasetMeta {
    id: string;
    name: string;
    createdAt: string;
    updatedAt: string;
    itemCounts: {
        tasks: number;
        employees: number;
        aircrafts: number;
        timeMatrix: number;
    };
}

export interface DatasetData {
    tasks: Task[];
    employees: Employee[];
    aircrafts: Aircraft[];
    timeMatrix: TimeMatrixEntry[];
}

const API_BASE = '/api/datasets';
console.log('dataset.ts API_BASE:', API_BASE);

export const api = {
    async listDatasets(): Promise<DatasetMeta[] | null> {
        try {
            const res = await fetch(API_BASE);
            if (!res.ok) throw new Error('Failed to fetch datasets');
            return await res.json();
        } catch (e) {
            console.error(e);
            return null;
        }
    },

    async createDataset(name: string): Promise<{ meta: DatasetMeta; data: DatasetData }> {
        const res = await fetch(API_BASE, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name }),
        });
        if (!res.ok) throw new Error('Failed to create dataset');
        return await res.json();
    },

    async getDataset(id: string): Promise<DatasetData | null> {
        try {
            const res = await fetch(`${API_BASE}/${id}`);
            if (!res.ok) return null;
            return await res.json();
        } catch (e) {
            console.error(e);
            return null;
        }
    },

    async saveDataset(id: string, data: DatasetData): Promise<void> {
        try {
            await fetch(`${API_BASE}/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
        } catch (e) {
            console.error('Failed to save dataset:', e);
        }
    },

    async deleteDataset(id: string): Promise<void> {
        await fetch(`${API_BASE}/${id}`, { method: 'DELETE' });
    },

    async renameDataset(id: string, name: string): Promise<void> {
        await fetch(`${API_BASE}/${id}/rename`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name }),
        });
    }
};

// Deprecated local storage functions kept for migration reference if needed
export const DATASETS_META_KEY = 'aircraft-datasets';
export const DATASET_DATA_PREFIX = 'aircraft-dataset-';

export function createEmptyDataset(name: string): { meta: DatasetMeta; data: DatasetData } {
    const now = new Date().toISOString();
    const id = `ds-${Date.now()}`;

    return {
        meta: {
            id,
            name,
            createdAt: now,
            updatedAt: now,
            itemCounts: {
                tasks: 0,
                employees: 0,
                aircrafts: 0,
                timeMatrix: 0,
            },
        },
        data: {
            tasks: [],
            employees: [],
            aircrafts: [],
            timeMatrix: [],
        },
    };
}
