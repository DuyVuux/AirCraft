import { useRef, useState } from 'react';
import type { TabProps, TabConfig } from './types';
import type { Hub } from '@/types/hub';
import HubEditor from '@/components/editor/HubEditor';

export const tabConfig: TabConfig = {
    id: 'hubs',
    label: 'HUBS',
    order: 2,
};

function parseHubsCSV(text: string): { hubs: Hub[]; errors: string[] } {
    const lines = text.split('\n').filter(line => line.trim());
    if (lines.length < 2) return { hubs: [], errors: ['File rỗng'] };

    const delimiter = lines[0].includes(';') ? ';' : ',';
    const headers = lines[0].split(delimiter).map(h => h.trim());

    const hubs: Hub[] = [];
    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(delimiter).map(v => v.trim());
        const row: Record<string, string> = {};
        headers.forEach((h, idx) => row[h] = values[idx] || '');

        hubs.push({
            hubId: row['hubId'] || row['Hub ID'] || `hub-${i}`,
            name: row['name'] || row['Tên Hub'] || '',
            latitude: parseFloat(row['latitude'] || row['Latitude']) || 0,
            longitude: parseFloat(row['longitude'] || row['Longitude']) || 0,
        });
    }

    return { hubs, errors: [] };
}

export default function HubTab({
    hubs,
    setHubs,
    editingHubId,
    setEditingHubId,
    handleHubSave,
    handleHubDelete,
}: TabProps) {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [importing, setImporting] = useState(false);

    const handleImportCSV = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        setImporting(true);
        try {
            const text = await file.text();
            const result = parseHubsCSV(text);
            if (result.hubs.length > 0) {
                alert(`✅ Import thành công ${result.hubs.length} hubs!`);
                const existingIds = new Set(hubs.map(h => h.hubId));
                const newHubs = result.hubs.filter(h => !existingIds.has(h.hubId));
                setHubs([...hubs, ...newHubs]);
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
                <h3 style={{ margin: 0 }}>Quản lý Hubs</h3>
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

            <HubEditor onSave={handleHubSave} onDelete={handleHubDelete} />
            {hubs.length > 0 && (
                <div className="layout-form-card" style={{ marginTop: '1.5rem' }}>
                    <h3 className="layout-form-card-title">Hubs List ({hubs.length})</h3>
                    {hubs.map((hub) => (
                        <div key={hub.hubId} style={{ marginBottom: '1rem' }}>
                            <HubEditor
                                initialData={hub}
                                isEditing={editingHubId === hub.hubId}
                                onSave={handleHubSave}
                                onDelete={handleHubDelete}
                                onStartEdit={() => setEditingHubId(hub.hubId)}
                            />
                        </div>
                    ))}
                </div>
            )}
        </>
    );
}
