import { useRef, useState, useMemo } from 'react';
import type { TabProps, TabConfig } from './types';
import type { Aircraft } from '@/types/aircraft';
import { AIRCRAFT_TYPES } from '@/types/aircraft';
import AircraftEditor from '@/components/editor/AircraftEditor';
import AircraftList from '@/components/editor/AircraftList';
import { downloadTemplate } from '@/services/csvParser';

export const tabConfig: TabConfig = {
    id: 'aircrafts',
    label: 'AIRCRAFTS',
    order: 3,
};

function parseFlightsCSV(text: string): { aircrafts: Aircraft[]; errors: string[] } {
    const lines = text.split('\n').filter(line => line.trim());
    if (lines.length < 2) return { aircrafts: [], errors: ['File rỗng'] };

    const delimiter = lines[0].includes(';') ? ';' : ',';
    const headers = lines[0].split(delimiter).map(h => h.trim());

    const aircrafts: Aircraft[] = [];

    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(delimiter).map(v => v.trim());
        const row: Record<string, string> = {};
        headers.forEach((h, idx) => row[h] = values[idx] || '');

        const aTypeId = row['A/C Type'] || '';
        const aTypeDesc = AIRCRAFT_TYPES[aTypeId as keyof typeof AIRCRAFT_TYPES] || aTypeId;
        const etdStr = row['ETD'] || '';

        let startTime = etdStr;
        let endTime = '';
        if (etdStr) {
            try {
                const etdDate = new Date(etdStr);
                etdDate.setMinutes(etdDate.getMinutes() + 60);
                endTime = etdDate.toISOString().replace('T', ' ').substring(0, 19);
            } catch { endTime = etdStr; }
        }

        aircrafts.push({
            aircraftId: `${row['Flight']}-${i}`,
            flightNumber: row['Flight'] || '',
            aType: { id: aTypeId, desc: aTypeDesc },
            location: { locationId: '', locationType: 'APRON', longitude: 0, latitude: 0 },
            timeWindow: { start: startTime, end: endTime },
            requiredTasks: [{ taskCode: 'DEP-M' }, { taskCode: 'DEP-A' }],
        });
    }

    return { aircrafts, errors: [] };
}

export default function AircraftTab({
    aircrafts,
    setAircrafts,
    editingAircraftId,
    setEditingAircraftId,
    handleAircraftSave,
    handleAircraftDelete,
    handleAircraftBulkDelete,
    availableTaskCodes,
    taskMap,
    mapNodes,
}: TabProps) {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [importing, setImporting] = useState(false);

    const standStatus = useMemo(() => {
        const occupiedLocationIds = new Set(
            aircrafts
                .filter(a => a.location?.locationId)
                .map(a => a.location.locationId)
        );

        const stands = (mapNodes || []).filter(n => n.type === 'aircraft_stand');
        const occupied = stands.filter(s => occupiedLocationIds.has(s.id));
        const available = stands.filter(s => !occupiedLocationIds.has(s.id));

        return { stands, occupied, available, occupiedLocationIds };
    }, [aircrafts, mapNodes]);

    const handleImportCSV = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        setImporting(true);
        try {
            const text = await file.text();
            const result = parseFlightsCSV(text);

            if (result.errors.length > 0) {
                alert(`Lỗi:\n${result.errors.join('\n')}`);
            } else {
                alert(`✅ Import thành công ${result.aircrafts.length} chuyến bay!`);
            }

            const existingIds = new Set(aircrafts.map(a => a.aircraftId));
            const newAircrafts = result.aircrafts.filter(a => !existingIds.has(a.aircraftId));
            setAircrafts([...aircrafts, ...newAircrafts]);
        } catch (err) {
            alert(`Lỗi đọc file: ${err instanceof Error ? err.message : 'Unknown error'}`);
        } finally {
            setImporting(false);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const handleDownload = () => {
        const headers = ['Aircraft ID', 'Flight Number', 'A/C Type', 'Location ID', 'Start Time', 'End Time', 'Required Tasks'];
        const rows = aircrafts.map(aircraft => [
            aircraft.aircraftId,
            aircraft.flightNumber || '',
            aircraft.aType.id,
            aircraft.location?.locationId || '',
            aircraft.timeWindow?.start || '',
            aircraft.timeWindow?.end || '',
            aircraft.requiredTasks?.map(t => t.taskCode).join(',') || '',
        ]);
        downloadTemplate('aircrafts_export.csv', headers, rows);
    };

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', height: 'calc(100vh - 200px)' }}>
            <div style={{
                display: 'flex',
                gap: '1rem',
                padding: '0.75rem',
                background: 'var(--color-surface-elevated, #1e293b)',
                borderRadius: '0.5rem',
                flexWrap: 'wrap',
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Tổng bãi đỗ:</span>
                    <span style={{ fontWeight: 600 }}>{standStatus.stands.length}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{
                        width: '12px', height: '12px',
                        borderRadius: '50%',
                        background: 'var(--color-success)',
                    }} />
                    <span style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Trống:</span>
                    <span className="text-success" style={{ fontWeight: 600 }}>{standStatus.available.length}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{
                        width: '12px', height: '12px',
                        borderRadius: '50%',
                        background: 'var(--color-danger)',
                    }} />
                    <span style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)' }}>Có máy bay:</span>
                    <span className="text-danger" style={{ fontWeight: 600 }}>{standStatus.occupied.length}</span>
                </div>
                <div style={{ marginLeft: 'auto', display: 'flex', gap: '0.5rem' }}>
                    <button
                        className="dataset-btn"
                        onClick={handleDownload}
                        disabled={aircrafts.length === 0}
                        style={{
                            opacity: aircrafts.length === 0 ? 0.5 : 1,
                            cursor: aircrafts.length === 0 ? 'not-allowed' : 'pointer'
                        }}
                    >
                        <span className="material-symbols-outlined">download</span>
                        Download CSV ({aircrafts.length})
                    </button>
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept=".csv"
                        onChange={handleImportCSV}
                        style={{ display: 'none' }}
                    />
                    <button
                        className="dataset-btn"
                        onClick={() => fileInputRef.current?.click()}
                        disabled={importing}
                    >
                        <span className="material-symbols-outlined">upload_file</span>
                        {importing ? 'Importing...' : 'Import Flights'}
                    </button>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '0.75rem', flex: 1, minHeight: 0 }}>
                <div style={{ height: '100%', overflowY: 'auto', paddingRight: '0.5rem' }}>
                    <button
                        className="dataset-btn primary"
                        onClick={() => setEditingAircraftId(null)}
                        style={{ marginBottom: '1rem', width: '100%' }}
                    >
                        <span className="material-symbols-outlined">add</span>
                        Add New Aircraft
                    </button>
                    <AircraftList
                        aircrafts={aircrafts}
                        onEdit={(a) => setEditingAircraftId(a.aircraftId)}
                        onDelete={handleAircraftDelete}
                        onBulkDelete={handleAircraftBulkDelete}
                        selectedId={editingAircraftId}
                    />
                </div>

                <div style={{ height: '100%', overflowY: 'auto' }}>
                    <AircraftEditor
                        key={editingAircraftId || 'new'}
                        initialData={editingAircraftId ? aircrafts.find(a => a.aircraftId === editingAircraftId) : null}
                        isEditing={!!editingAircraftId}
                        onSave={handleAircraftSave}
                        onDelete={handleAircraftDelete}
                        onStartEdit={() => { }}
                        availableTaskCodes={availableTaskCodes}
                        taskMap={taskMap}
                        allAircrafts={aircrafts}
                        mapNodes={mapNodes}
                    />
                </div>
            </div>
        </div>
    );
}
