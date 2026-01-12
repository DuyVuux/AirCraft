import React, { useState, useMemo } from 'react';
import type { Aircraft, AircraftTypeId } from '@/types/aircraft';
import { AIRCRAFT_TYPES } from '@/types/aircraft';
import type { Task } from './TaskEditor';
import type { MapNode } from '@/types/mapEditor';
import type { POIFeature } from '@/services/poiService';
import { DEFAULT_GPS } from '@/utils/constants';
import MapPicker from '@/components/common/MapPicker';
import './Editor.css';

interface AircraftEditorProps {
  onSave?: (aircraft: Aircraft) => void;
  onDelete?: (aircraftId: string) => void;
  onStartEdit?: () => void;
  initialData?: Aircraft | null;
  isEditing?: boolean;
  availableTaskCodes?: string[];
  taskMap?: Map<string, Task>;
  allAircrafts?: Aircraft[];
  mapNodes?: MapNode[];
}


const AircraftEditor: React.FC<AircraftEditorProps> = ({
  onSave,
  // onDelete,
  onStartEdit,
  initialData,
  isEditing = false,
  availableTaskCodes = [],
  taskMap,
  allAircrafts = [],
  mapNodes = [],
}) => {
  const [aircraft, setAircraft] = useState<Aircraft>(
    initialData || {
      aircraftId: '',
      registrationNumber: '',
      flightNumber: '',
      aType: { id: 'A320', desc: 'Airbus A320' },
      location: {
        locationId: '',
        locationType: 'GATE',
        longitude: DEFAULT_GPS.longitude,
        latitude: DEFAULT_GPS.latitude,
      },
      timeWindow: { start: '', end: '' },
      requiredTasks: [],
    }
  );

  // Sync state when initialData changes (e.g., after save or when switching aircraft)
  React.useEffect(() => {
    if (initialData) {
      setAircraft(initialData);
    } else {
      setAircraft({
        aircraftId: '',
        registrationNumber: '',
        flightNumber: '',
        aType: { id: 'A320', desc: 'Airbus A320' },
        location: {
          locationId: '',
          locationType: 'GATE',
          longitude: DEFAULT_GPS.longitude,
          latitude: DEFAULT_GPS.latitude,
        },
        timeWindow: { start: '', end: '' },
        requiredTasks: [],
      });
    }
  }, [initialData]);

  // Use state for task inputs
  const [newTaskCode, setNewTaskCode] = useState('');
  const [newMinLevel, setNewMinLevel] = useState<number>(1);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Determine if fields should be read-only
  const isReadOnly = !!(initialData && !isEditing);

  const occupiedOsmIds = useMemo(() => {
    return allAircrafts
      .filter(a => a.aircraftId !== aircraft.aircraftId && a.location.locationId)
      .map(a => a.location.locationId);
  }, [allAircrafts, aircraft.aircraftId]);

  const aircraftStandNodes = useMemo(() => {
    return mapNodes.filter(n => n.type === 'aircraft_stand');
  }, [mapNodes]);

  const customPOIFeatures: POIFeature[] = useMemo(() => {
    if (aircraftStandNodes.length === 0) return [];
    return aircraftStandNodes.map(node => ({
      type: 'Feature' as const,
      geometry: {
        type: 'Point' as const,
        coordinates: [node.longitude, node.latitude] as [number, number],
      },
      properties: {
        locationId: node.id,
        locationType: 'APRON' as const,
        method: 'map_editor',
      },
      osmId: node.id,
    }));
  }, [aircraftStandNodes]);

  // Validation function
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!aircraft.aircraftId.trim()) {
      newErrors.aircraftId = 'Aircraft ID là bắt buộc';
    }

    if (!aircraft.location.locationId.trim()) {
      newErrors.locationId = 'Vui lòng chọn vị trí trên bản đồ';
    }

    if (!aircraft.timeWindow.start) {
      newErrors.timeWindowStart = 'Time Window Start là bắt buộc';
    }

    if (!aircraft.timeWindow.end) {
      newErrors.timeWindowEnd = 'Time Window End là bắt buộc';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const isFormValid = (): boolean => {
    return (
      aircraft.aircraftId.trim() !== '' &&
      aircraft.location.locationId.trim() !== '' &&
      aircraft.timeWindow.start !== '' &&
      aircraft.timeWindow.end !== ''
    );
  };

  const handleChange = (field: keyof Aircraft, value: any) => {
    setAircraft((prev) => ({ ...prev, [field]: value }));
  };

  const handleAircraftTypeChange = (typeId: AircraftTypeId) => {
    setAircraft((prev) => ({
      ...prev,
      aType: {
        id: typeId,
        desc: AIRCRAFT_TYPES[typeId],
      },
    }));
  };

  const handleAddTask = () => {
    if (!newTaskCode) return;

    // Check if task already exists
    const taskExists = aircraft.requiredTasks.some(
      (task) => task.taskCode === newTaskCode
    );

    if (taskExists) return;

    setAircraft((prev) => ({
      ...prev,
      requiredTasks: [
        ...prev.requiredTasks,
        { taskCode: newTaskCode, minLevel: newMinLevel },
      ],
    }));
    setNewTaskCode(''); // Reset selection
    setNewMinLevel(1);
  };

  const handleRemoveTask = (index: number) => {
    setAircraft((prev) => ({
      ...prev,
      requiredTasks: prev.requiredTasks.filter((_, i) => i !== index),
    }));
  };

  const handleSave = () => {
    if (!validateForm()) return;
    onSave?.(aircraft);
  };

  // Render 2-Column Grid
  return (
    <div className="aircraft-editor-container" style={{
      display: 'grid',
      gridTemplateColumns: '450px 1fr', // Form fixed 450px, Map takes rest
      gap: '1rem',
      alignItems: 'start',
      height: '100%',
      overflow: 'hidden'
    }}>

      {/* LEFT COLUMN: Controls (Scrollable) */}
      <div style={{ height: '100%', overflowY: 'auto', paddingRight: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.75rem', width: '100%' }}>

        {isReadOnly && (
          <div className="editor-readonly-banner">
            <span className="material-symbols-outlined">lock</span>
            Chế độ xem chi tiết — Nhấn "Update" để chỉnh sửa
          </div>
        )}

        {/* Basic Info & Time - Grouped */}
        <div className="editor-card">
          <h3 className="editor-card-title">{initialData ? 'Thông tin máy bay' : 'Thêm mới máy bay'}</h3>

          <div className="editor-form-grid">
            <div className="editor-form-group">
              <label className="editor-form-label">Aircraft ID *</label>
              <input
                className="editor-form-input"
                value={aircraft.aircraftId}
                onChange={(e) => {
                  handleChange('aircraftId', e.target.value);
                  if (errors.aircraftId) setErrors(p => ({ ...p, aircraftId: '' }));
                }}
                placeholder="AIRCRAFT-001"
                readOnly={isReadOnly}
                style={errors.aircraftId ? { borderColor: 'var(--color-danger)' } : {}}
              />
              {errors.aircraftId && <p className="editor-form-helper text-danger">{errors.aircraftId}</p>}
            </div>

            <div className="editor-form-group">
              <label className="editor-form-label">Registration Number</label>
              <input
                className="editor-form-input"
                value={aircraft.registrationNumber || ''}
                onChange={(e) => handleChange('registrationNumber', e.target.value)}
                placeholder="VN-A123"
                readOnly={isReadOnly}
              />
              <p className="editor-form-helper">Số đăng ký máy bay (VD: VN-A123)</p>
            </div>

            <div className="editor-form-group">
              <label className="editor-form-label">Flight Number</label>
              <input
                className="editor-form-input"
                value={aircraft.flightNumber || ''}
                onChange={(e) => handleChange('flightNumber', e.target.value)}
                placeholder="VN123"
                readOnly={isReadOnly}
              />
              <p className="editor-form-helper">Số hiệu chuyến bay (VD: VN123)</p>
            </div>

            <div className="editor-form-group">
              <label className="editor-form-label">Type</label>
              <div className="editor-form-select-wrapper">
                <select
                  className="editor-form-select"
                  value={aircraft.aType.id}
                  onChange={(e) => handleAircraftTypeChange(e.target.value as AircraftTypeId)}
                  disabled={isReadOnly}
                >
                  {Object.entries(AIRCRAFT_TYPES).map(([id, desc]) => (
                    <option key={id} value={id}>{desc}</option>
                  ))}
                </select>
                <span className="material-symbols-outlined editor-form-select-icon">expand_more</span>
              </div>
            </div>
          </div>

          <div className="editor-form-grid" style={{ marginTop: '1rem' }}>
            <div className="editor-form-group">
              <label className="editor-form-label">Start Time *</label>
              <input
                className="editor-date-input"
                type="datetime-local"
                value={aircraft.timeWindow.start.replace('Z', '').slice(0, 16)}
                onChange={(e) => handleChange('timeWindow', { ...aircraft.timeWindow, start: new Date(e.target.value).toISOString() })}
                readOnly={isReadOnly}
              />
            </div>
            <div className="editor-form-group">
              <label className="editor-form-label">End Time *</label>
              <input
                className="editor-date-input"
                type="datetime-local"
                value={aircraft.timeWindow.end.replace('Z', '').slice(0, 16)}
                onChange={(e) => handleChange('timeWindow', { ...aircraft.timeWindow, end: new Date(e.target.value).toISOString() })}
                readOnly={isReadOnly}
              />
            </div>
          </div>
        </div>

        {/* Tasks Section */}
        <div className="editor-card">
          <h3 className="editor-card-title">Tasks yêu cầu</h3>

          {!isReadOnly && (
            <div className="editor-task-grid" style={{ marginTop: '1rem' }}>
              <div className="editor-form-group">
                <label className="editor-form-label">Chọn Task Code</label>
                <div className="editor-form-select-wrapper">
                  <select
                    className="editor-form-select"
                    value={newTaskCode}
                    onChange={(e) => {
                      const code = e.target.value;
                      setNewTaskCode(code);
                      const t = taskMap?.get(code);
                      if (t && t.defaultMinLevel) setNewMinLevel(t.defaultMinLevel);
                    }}
                  >
                    <option value="">-- Chọn Task --</option>
                    {availableTaskCodes.map(code => (
                      <option key={code} value={code}>{code}</option>
                    ))}
                  </select>
                  <span className="material-symbols-outlined editor-form-select-icon">expand_more</span>
                </div>
              </div>

              <div className="editor-form-group">
                <label className="editor-form-label">Min Level</label>
                <input
                  className="editor-form-input editor-task-level-input"
                  type="number"
                  value={newMinLevel}
                  onChange={(e) => setNewMinLevel(parseInt(e.target.value) || 1)}
                  min={1}
                />
              </div>

              <button
                className="editor-form-button-secondary"
                onClick={handleAddTask}
                disabled={!newTaskCode}
                style={{ alignSelf: 'end' }}
              >
                Add
              </button>
            </div>
          )}

          <div className="editor-task-chips">
            {aircraft.requiredTasks.length === 0 && <span className="editor-task-list-empty">Chưa có task nào</span>}
            {aircraft.requiredTasks.map((task, index) => (
              <div key={`${task.taskCode}-${index}`} className="editor-task-chip">
                <span>{task.taskCode} {task.minLevel ? `(L${task.minLevel})` : ''}</span>
                {!isReadOnly && (
                  <span className="editor-task-chip-remove" onClick={() => handleRemoveTask(index)}>×</span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div style={{ marginTop: 'auto', marginBottom: '1rem' }}>
          {isReadOnly ? (
            <button className="editor-form-button-primary" onClick={onStartEdit}>
              <span className="material-symbols-outlined">edit</span> Update
            </button>
          ) : (
            <button
              className="editor-form-button-primary"
              onClick={handleSave}
              disabled={!isFormValid()}
              style={{ opacity: !isFormValid() ? 0.5 : 1 }}
            >
              <span className="material-symbols-outlined">save</span> {initialData ? 'Save Changes' : 'Add Aircraft'}
            </button>
          )}
        </div>
      </div>

      {/* RIGHT COLUMN: Map - Sticky */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', position: 'sticky', top: 0, height: '100%' }}>
        <div className="editor-card" style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <h3 className="editor-card-title" style={{ margin: 0 }}>Vị trí đỗ</h3>
            {aircraft.location.locationId && (
              <span className="text-success" style={{
                fontSize: '0.875rem',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: '0.25rem'
              }}>
                <span className="material-symbols-outlined" style={{ fontSize: '1rem' }}>location_on</span>
                {aircraft.location.locationId}
              </span>
            )}
          </div>

          <div className="editor-map-container" style={{ flex: 1, minHeight: '200px', marginBottom: 0 }}>
            <MapPicker
              longitude={aircraft.location.longitude}
              latitude={aircraft.location.latitude}
              onLocationChange={() => { }}
              showPOI={true}
              poiType="aircraft"
              showHubs={true}
              occupiedOsmIds={occupiedOsmIds}
              selectedLocationId={aircraft.location.locationId}
              customPOIFeatures={customPOIFeatures.length > 0 ? customPOIFeatures : undefined}
              onPOIClick={async (osmId, centroid) => {
                const currentLocationId = aircraft.location.locationId;

                if (osmId === currentLocationId) {
                  const updatedAircraft = {
                    ...aircraft,
                    location: {
                      ...aircraft.location,
                      locationId: '',
                      longitude: DEFAULT_GPS.longitude,
                      latitude: DEFAULT_GPS.latitude,
                    }
                  };
                  setAircraft(updatedAircraft);
                  if (initialData) {
                    onSave?.(updatedAircraft);
                  }
                } else {
                  const updatedAircraft = {
                    ...aircraft,
                    location: {
                      ...aircraft.location,
                      locationId: osmId,
                      longitude: centroid.longitude,
                      latitude: centroid.latitude,
                      locationType: 'APRON' as const,
                    }
                  };
                  setAircraft(updatedAircraft);
                  if (initialData) {
                    onSave?.(updatedAircraft);
                  }
                }
                if (errors.locationId) setErrors(p => ({ ...p, locationId: '' }));
              }}
              height="100%"
              hideTitle={true}
              hideCoordinates={true}
              hideWrapper={true}
            />
          </div>

          {errors.locationId ? (
            <p className="editor-form-helper text-danger">{errors.locationId}</p>
          ) : (
            <p className="editor-form-helper">
              {aircraft.location.locationId
                ? 'Click vị trí hiện tại để hủy chọn'
                : 'Click chọn ô trên bản đồ'}
            </p>
          )}
        </div>
      </div>

    </div>
  );
};

export default AircraftEditor;
