import { useState, useMemo, useCallback } from 'react';
import type { Employee, Role } from '@/types/employee';

export interface EmployeeFilters {
    searchText: string;
    role: Role | 'ALL';
    capabilities: string[];
    certifications: string[];
    shiftStart: string; // HH:mm
    shiftEnd: string; // HH:mm
}

const initialFilters: EmployeeFilters = {
    searchText: '',
    role: 'ALL',
    capabilities: [],
    certifications: [],
    shiftStart: '',
    shiftEnd: '',
};

export function useEmployeeFilter(employees: Employee[]) {
    const [filters, setFilters] = useState<EmployeeFilters>(initialFilters);

    const updateFilter = useCallback(<K extends keyof EmployeeFilters>(
        key: K,
        value: EmployeeFilters[K]
    ) => {
        setFilters(prev => ({ ...prev, [key]: value }));
    }, []);

    const clearFilters = useCallback(() => {
        setFilters(initialFilters);
    }, []);

    const hasActiveFilters = useMemo(() => {
        return (
            filters.searchText !== '' ||
            filters.role !== 'ALL' ||
            filters.capabilities.length > 0 ||
            filters.certifications.length > 0 ||
            filters.shiftStart !== '' ||
            filters.shiftEnd !== ''
        );
    }, [filters]);

    const activeFilterCount = useMemo(() => {
        let count = 0;
        if (filters.searchText) count++;
        if (filters.role !== 'ALL') count++;
        if (filters.capabilities.length > 0) count++;
        if (filters.certifications.length > 0) count++;
        if (filters.shiftStart || filters.shiftEnd) count++;
        return count;
    }, [filters]);

    const filteredEmployees = useMemo(() => {
        return employees.filter(emp => {
            // 1. Search Text (ID or Name)
            if (filters.searchText) {
                const searchTerm = filters.searchText.toLowerCase();
                const idMatch = emp.employeeId.toLowerCase().includes(searchTerm);
                const nameMatch = (emp.name || '').toLowerCase().includes(searchTerm);
                if (!idMatch && !nameMatch) {
                    return false;
                }
            }

            // 2. Role
            if (filters.role !== 'ALL') {
                if (emp.eType.role !== filters.role) {
                    return false;
                }
            }

            // 3. Capabilities (OR logic)
            if (filters.capabilities.length > 0) {
                const empCaps = emp.taskCapabilities || [];
                if (empCaps.length === 0) return false;
                const hasCap = filters.capabilities.some(cap => empCaps.includes(cap));
                if (!hasCap) return false;
            }

            // 4. Certifications (OR logic)
            if (filters.certifications.length > 0) {
                const empCerts = emp.certifications || [];
                if (empCerts.length === 0) return false;
                const hasCert = filters.certifications.some(cert => empCerts.includes(cert));
                if (!hasCert) return false;
            }

            // 5. Shift Time (HH:mm)
            // Check if ANY working time overlaps or starts within range?
            // Let's keep it simple: Start time of the first shift matches criteria
            if (filters.shiftStart || filters.shiftEnd) {
                const firstShift = emp.workingTimes[0];
                if (!firstShift) return false;

                // Extract HH:mm from ISO string
                const shiftDate = new Date(firstShift.start);
                const shiftTime = shiftDate.toISOString().substring(11, 16); // Extract HH:mm part from ISO

                if (filters.shiftStart && shiftTime < filters.shiftStart) return false;
                if (filters.shiftEnd && shiftTime > filters.shiftEnd) return false;
            }

            return true;
        });
    }, [employees, filters]);

    return {
        filters,
        updateFilter,
        clearFilters,
        hasActiveFilters,
        activeFilterCount,
        filteredEmployees,
        totalCount: employees.length,
        filteredCount: filteredEmployees.length,
    };
}

export default useEmployeeFilter;
