import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import type { ScheduleResult } from '@/types/scheduler';
import type { LogEntry, SchedulerConfig } from '@/services/schedulerApi';

export interface HistoryEntry {
    id: string;
    timestamp: string;
    status: 'OPTIMAL' | 'FEASIBLE' | 'INFEASIBLE' | 'ERROR';
    result: ScheduleResult | null;
    logs: LogEntry[];
    error?: string;
    config: SchedulerConfig;
    taskCount: number;
    employeeCount: number;
    aircraftCount: number;
}

interface HistoryContextType {
    entries: HistoryEntry[];
    addEntry: (entry: Omit<HistoryEntry, 'id' | 'timestamp'>) => void;
    clearHistory: () => void;
    deleteEntry: (id: string) => void;
}

const HistoryContext = createContext<HistoryContextType | null>(null);

const STORAGE_KEY = 'aircraft_scheduler_history';

export function HistoryProvider({ children }: { children: ReactNode }) {
    const [entries, setEntries] = useState<HistoryEntry[]>(() => {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            try {
                return JSON.parse(stored);
            } catch {
                return [];
            }
        }
        return [];
    });

    useEffect(() => {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
    }, [entries]);

    const addEntry = (entry: Omit<HistoryEntry, 'id' | 'timestamp'>) => {
        const newEntry: HistoryEntry = {
            ...entry,
            id: `run-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            timestamp: new Date().toISOString(),
        };
        setEntries(prev => [newEntry, ...prev]);
    };

    const clearHistory = () => {
        setEntries([]);
    };

    const deleteEntry = (id: string) => {
        setEntries(prev => prev.filter(e => e.id !== id));
    };

    return (
        <HistoryContext.Provider value={{ entries, addEntry, clearHistory, deleteEntry }}>
            {children}
        </HistoryContext.Provider>
    );
}

export function useHistory() {
    const context = useContext(HistoryContext);
    if (!context) {
        throw new Error('useHistory must be used within a HistoryProvider');
    }
    return context;
}
