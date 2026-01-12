import { useRef, useState } from 'react';
import type { TabProps, TabConfig } from './types';
import type { TimeMatrixEntry } from '@/types/matrix';
import TimeMatrixEditor from '@/components/editor/TimeMatrixEditor';

export const tabConfig: TabConfig = {
    id: 'time-matrix',
    label: 'TIME MATRIX',
    order: 4,
};

function parseTimeMatrixCSV(text: string): { entries: TimeMatrixEntry[]; errors: string[] } {
    const lines = text.split('\n').filter(line => line.trim());
    if (lines.length < 2) return { entries: [], errors: ['File rỗng'] };

    const delimiter = lines[0].includes(';') ? ';' : ',';
    const headers = lines[0].split(delimiter).map(h => h.trim());

    const entries: TimeMatrixEntry[] = [];
    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(delimiter).map(v => v.trim());
        const row: Record<string, string> = {};
        headers.forEach((h, idx) => row[h] = values[idx] || '');

        entries.push({
            taskCode: row['taskCode'] || row['Task Code'] || '',
            role: row['role'] || row['Role'] || 'MECHANIC',
            level: parseInt(row['level'] || row['Level']) || 1,
            aircraftId: row['aircraftId'] || row['Aircraft ID'] || undefined,
            timeProcess: parseInt(row['timeProcess'] || row['Time (seconds)']) || 0,
        });
    }

    return { entries, errors: [] };
}

export default function TimeMatrixTab({
    timeMatrix,
    setTimeMatrix,
    editingTimeMatrixIndex,
    setEditingTimeMatrixIndex,
    handleTimeMatrixSave,
    handleTimeMatrixDelete,
    availableTaskCodes,
    availableAircraftIds,
}: TabProps) {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [importing, setImporting] = useState(false);

    const handleImportCSV = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        setImporting(true);
        try {
            const text = await file.text();
            const result = parseTimeMatrixCSV(text);
            if (result.entries.length > 0) {
                alert(`✅ Import thành công ${result.entries.length} entries!`);
                setTimeMatrix([...timeMatrix, ...result.entries]);
            }
        } catch (err) {
            alert(`Lỗi: ${err instanceof Error ? err.message : 'Unknown error'}`);
        } finally {
            setImporting(false);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    return (
        <>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ margin: 0 }}>Quản lý Time Matrix</h3>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
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
                        {importing ? 'Importing...' : 'Import CSV'}
                    </button>
                </div>
            </div>

            <TimeMatrixEditor
                onSave={handleTimeMatrixSave}
                availableAircraftIds={availableAircraftIds}
                availableTaskCodes={availableTaskCodes}
            />
            {timeMatrix.length > 0 && (
                <div className="layout-form-card" style={{ marginTop: '1.5rem' }}>
                    <h3 className="layout-form-card-title">Time Matrix Entries ({timeMatrix.length})</h3>
                    {timeMatrix.map((entry, index) => (
                        <div key={index} style={{ marginBottom: '1rem' }}>
                            <TimeMatrixEditor
                                initialData={entry}
                                isEditing={editingTimeMatrixIndex === index}
                                onSave={(e) => handleTimeMatrixSave(e, index)}
                                onDelete={() => handleTimeMatrixDelete(index)}
                                onStartEdit={() => setEditingTimeMatrixIndex(index)}
                                availableAircraftIds={availableAircraftIds}
                                availableTaskCodes={availableTaskCodes}
                            />
                        </div>
                    ))}
                </div>
            )}
        </>
    );
}
