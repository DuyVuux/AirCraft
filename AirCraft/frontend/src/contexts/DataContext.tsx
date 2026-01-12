import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { InputData } from '@/types/input';
import type { Aircraft } from '@/types/aircraft';
import type { Employee } from '@/types/employee';
import type { Hub } from '@/types/hub';
import type { TimeMatrixEntry } from '@/types/matrix';
import type { Task } from '@/components/editor/TaskEditor';

interface DataContextType {
  // Data from upload/developer mode
  importedData: Partial<InputData> | null;
  
  // Methods to set data
  setImportedData: (data: Partial<InputData> | null) => void;
  addAircrafts: (aircrafts: Aircraft[]) => void;
  addEmployees: (employees: Employee[]) => void;
  addHubs: (hubs: Hub[]) => void;
  addTimeMatrix: (timeMatrix: TimeMatrixEntry[]) => void;
  addTasks: (tasks: Task[]) => void;
  
  // Clear imported data
  clearImportedData: () => void;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export const useDataContext = () => {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error('useDataContext must be used within DataProvider');
  }
  return context;
};

interface DataProviderProps {
  children: ReactNode;
}

export const DataProvider: React.FC<DataProviderProps> = ({ children }) => {
  const [importedData, setImportedDataState] = useState<Partial<InputData> | null>(null);

  const setImportedData = (data: Partial<InputData> | null) => {
    setImportedDataState(data);
  };

  const addAircrafts = (aircrafts: Aircraft[]) => {
    setImportedDataState((prev) => ({
      ...prev,
      aircrafts: [...(prev?.aircrafts || []), ...aircrafts],
    }));
  };

  const addEmployees = (employees: Employee[]) => {
    setImportedDataState((prev) => ({
      ...prev,
      employees: [...(prev?.employees || []), ...employees],
    }));
  };

  const addHubs = (hubs: Hub[]) => {
    setImportedDataState((prev) => ({
      ...prev,
      hubs: [...(prev?.hubs || []), ...hubs],
    }));
  };

  const addTimeMatrix = (timeMatrix: TimeMatrixEntry[]) => {
    setImportedDataState((prev) => ({
      ...prev,
      matrixConfigs: {
        ...prev?.matrixConfigs,
        timeMatrix: [...(prev?.matrixConfigs?.timeMatrix || []), ...timeMatrix],
        distanceMatrix: prev?.matrixConfigs?.distanceMatrix || [],
      },
    }));
  };

  const addTasks = (tasks: Task[]) => {
    // Tasks are not part of InputData, but we can store them separately
    // For now, we'll handle tasks differently in ManualInputPage
    setImportedDataState((prev) => ({
      ...prev,
      // Store tasks in a custom field
      _tasks: tasks,
    } as any));
  };

  const clearImportedData = () => {
    setImportedDataState(null);
  };

  const value: DataContextType = {
    importedData,
    setImportedData,
    addAircrafts,
    addEmployees,
    addHubs,
    addTimeMatrix,
    addTasks,
    clearImportedData,
  };

  return <DataContext.Provider value={value}>{children}</DataContext.Provider>;
};

