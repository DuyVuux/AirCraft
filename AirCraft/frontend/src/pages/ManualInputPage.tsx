import React, { useState, useMemo, useEffect } from 'react';
import Layout from '@/components/layout/Layout';
import { useDataContext } from '@/contexts/DataContext';
import { useGlobalData } from '@/contexts/GlobalDataContext';
import type { Task } from '@/components/editor/TaskEditor';
import { TAB_REGISTRY } from '@/components/tabs';
import { useDataHandlers } from '@/hooks/useDataHandlers';
import './ManualInputPage.css';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel({ children, value, index, ...other }: TabPanelProps) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`manual-input-tabpanel-${index}`}
      aria-labelledby={`manual-input-tab-${index}`}
      {...other}
    >
      {value === index && <div className="manual-input-tabpanel">{children}</div>}
    </div>
  );
}

function ManualInputPage() {
  const { importedData, clearImportedData } = useDataContext();
  const {
    tasks, setTasks,
    employees, setEmployees,
    hubs, setHubs,
    aircrafts, setAircrafts,
    timeMatrix, setTimeMatrix,
    mapNodes, setMapNodes,
    currentAirport,
    isLoading
  } = useGlobalData();

  const [value, setValue] = useState(0);

  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [editingAircraftId, setEditingAircraftId] = useState<string | null>(null);
  const [editingEmployeeId, setEditingEmployeeId] = useState<string | null>(null);
  const [editingHubId, setEditingHubId] = useState<string | null>(null);
  const [editingTimeMatrixIndex, setEditingTimeMatrixIndex] = useState<number | null>(null);

  const handlers = useDataHandlers({
    aircrafts, setAircrafts,
    employees, setEmployees,
    hubs, setHubs,
    tasks, setTasks,
    timeMatrix, setTimeMatrix,
    editingTask, setEditingTask,
    setEditingAircraftId, setEditingEmployeeId, setEditingHubId, setEditingTimeMatrixIndex,
  });

  // No need for local auto-save hooks as they are handled in GlobalDataContext

  useEffect(() => {
    if (!importedData) return;
    if (importedData.aircrafts?.length) {
      setAircrafts(prev => {
        const ids = new Set(prev.map(a => a.aircraftId));
        return [...prev, ...importedData.aircrafts!.filter(a => !ids.has(a.aircraftId))];
      });
    }
    if (importedData.employees?.length) {
      setEmployees(prev => {
        const ids = new Set(prev.map(e => e.employeeId));
        return [...prev, ...importedData.employees!.filter(e => !ids.has(e.employeeId))];
      });
    }
    if (importedData.hubs?.length) {
      setHubs(prev => {
        const ids = new Set(prev.map(h => h.hubId));
        return [...prev, ...importedData.hubs!.filter(h => !ids.has(h.hubId))];
      });
    }
    if (importedData.matrixConfigs?.timeMatrix?.length) {
      setTimeMatrix(prev => {
        const keys = new Set(prev.map(e => `${e.taskCode}-${e.role}-${e.level}-${e.aircraftId || ''}`));
        return [...prev, ...importedData.matrixConfigs!.timeMatrix.filter(
          e => !keys.has(`${e.taskCode}-${e.role}-${e.level}-${e.aircraftId || ''}`)
        )];
      });
    }
    clearImportedData();
  }, [importedData, clearImportedData, setAircrafts, setEmployees, setHubs, setTimeMatrix]);

  const availableAircraftIds = useMemo(() => aircrafts.map(a => a.aircraftId), [aircrafts]);
  const availableTaskCodes = useMemo(() => {
    const set = new Set<string>();
    tasks.forEach(t => set.add(t.taskCode));
    aircrafts.forEach(ac => ac.requiredTasks.forEach(t => set.add(t.taskCode)));
    timeMatrix.forEach(tm => set.add(tm.taskCode));
    return Array.from(set);
  }, [tasks, aircrafts, timeMatrix]);
  const taskMap = useMemo(() => new Map(tasks.map(t => [t.taskCode, t])), [tasks]);

  const tabProps = {
    tasks, employees, hubs, aircrafts, timeMatrix, mapNodes, currentAirport,
    setTasks, setEmployees, setHubs, setAircrafts, setTimeMatrix, setMapNodes,
    editingTask, setEditingTask,
    editingEmployeeId, setEditingEmployeeId,
    editingHubId, setEditingHubId,
    editingAircraftId, setEditingAircraftId,
    editingTimeMatrixIndex, setEditingTimeMatrixIndex,
    ...handlers,
    availableTaskCodes, availableAircraftIds, taskMap,
  };

  return (
    <Layout
      title="Nhập tay"
      description="Nhập và chỉnh sửa dữ liệu trực tiếp trên web"
      showSharedHeader={true}
    >
      <div className="manual-input-page">
        {isLoading && (
          <div className="manual-input-loading">
            <span className="material-symbols-outlined spin">sync</span>
          </div>
        )}
        {(tasks.length > 0 || aircrafts.length > 0 || employees.length > 0 || hubs.length > 0) && (
          <div className="manual-input-info-alert">
            Đã nhập: {tasks.length} tasks, {aircrafts.length} aircrafts, {employees.length} employees, {hubs.length} hubs, {timeMatrix.length} time matrix
          </div>
        )}
        <div className="manual-input-tabs">
          {TAB_REGISTRY.map((tab, index) => (
            <button
              key={tab.id}
              className={`manual-input-tab ${value === index ? 'active' : ''}`}
              onClick={() => setValue(index)}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <div className="manual-input-tab-content-wrapper">
          {TAB_REGISTRY.map((tab, index) => (
            <TabPanel key={tab.id} value={value} index={index}>
              <tab.Component {...tabProps} />
            </TabPanel>
          ))}
        </div>
      </div>
    </Layout>
  );
}

export default ManualInputPage;
