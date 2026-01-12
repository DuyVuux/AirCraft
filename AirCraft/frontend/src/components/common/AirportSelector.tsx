import { useState, useEffect } from 'react';
import type { AirportConfig, AirportsConfig } from '@/types/airport';
import { airportApi } from '@/types/airport';
import './AirportSelector.css';

interface AirportSelectorProps {
    selectedAirportId: string | null;
    onAirportChange: (airport: AirportConfig) => void;
    onAirportDeleted?: () => void;
}

export default function AirportSelector({
    selectedAirportId,
    onAirportChange,
    onAirportDeleted
}: AirportSelectorProps) {
    const [config, setConfig] = useState<AirportsConfig | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [showUploadModal, setShowUploadModal] = useState(false);
    const [newAirportName, setNewAirportName] = useState('');
    const [newAirportLat, setNewAirportLat] = useState('');
    const [newAirportLng, setNewAirportLng] = useState('');
    const [uploadFile, setUploadFile] = useState<File | null>(null);

    useEffect(() => {
        loadConfig();
    }, []);

    const loadConfig = async () => {
        try {
            const data = await airportApi.getConfig();
            setConfig(data);

            if (!selectedAirportId && data.defaultAirportId) {
                const defaultAirport = data.airports.find(a => a.id === data.defaultAirportId);
                if (defaultAirport) {
                    onAirportChange(defaultAirport);
                }
            }
        } catch (error) {
            console.error('Failed to load airports config:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const handleAirportSelect = (airportId: string) => {
        if (!config) return;
        const airport = config.airports.find(a => a.id === airportId);
        if (airport) {
            onAirportChange(airport);
        }
    };

    const handleCreateAirport = async () => {
        if (!newAirportName || !newAirportLat || !newAirportLng) return;

        try {
            const newAirport = await airportApi.createAirport({
                name: newAirportName,
                center: {
                    lat: parseFloat(newAirportLat),
                    lng: parseFloat(newAirportLng)
                },
                defaultZoom: 15
            });

            await loadConfig();
            onAirportChange(newAirport);
            setShowCreateModal(false);
            setNewAirportName('');
            setNewAirportLat('');
            setNewAirportLng('');
        } catch (error) {
            console.error('Failed to create airport:', error);
        }
    };

    const handleUploadGeoJSON = async () => {
        if (!uploadFile || !newAirportName || !newAirportLat || !newAirportLng) return;

        try {
            const newAirport = await airportApi.uploadGeoJSON(
                uploadFile,
                newAirportName,
                {
                    lat: parseFloat(newAirportLat),
                    lng: parseFloat(newAirportLng)
                }
            );

            await loadConfig();
            onAirportChange(newAirport);
            setShowUploadModal(false);
            setUploadFile(null);
            setNewAirportName('');
            setNewAirportLat('');
            setNewAirportLng('');
        } catch (error) {
            console.error('Failed to upload GeoJSON:', error);
        }
    };

    const handleDeleteAirport = async (airportId: string) => {
        if (!confirm('Bạn có chắc muốn xóa sân bay này?')) return;

        try {
            await airportApi.deleteAirport(airportId);
            await loadConfig();
            onAirportDeleted?.();
        } catch (error) {
            console.error('Failed to delete airport:', error);
        }
    };

    if (isLoading) {
        return <div className="airport-selector-loading">Đang tải...</div>;
    }

    const selectedAirport = config?.airports.find(a => a.id === selectedAirportId);

    return (
        <div className="airport-selector">
            <div className="airport-selector-main">
                <span className="material-symbols-outlined">flight_takeoff</span>
                <select
                    value={selectedAirportId || ''}
                    onChange={(e) => handleAirportSelect(e.target.value)}
                    className="airport-select"
                >
                    <option value="" disabled>Chọn sân bay</option>
                    {config?.airports.map(airport => (
                        <option key={airport.id} value={airport.id}>
                            {airport.name}
                        </option>
                    ))}
                </select>

                <button
                    className="airport-btn"
                    onClick={() => setShowCreateModal(true)}
                    title="Tạo sân bay mới"
                >
                    <span className="material-symbols-outlined">add</span>
                </button>

                <button
                    className="airport-btn"
                    onClick={() => setShowUploadModal(true)}
                    title="Upload GeoJSON"
                >
                    <span className="material-symbols-outlined">upload_file</span>
                </button>

                {selectedAirport && config && config.airports.length > 1 && (
                    <button
                        className="airport-btn danger"
                        onClick={() => handleDeleteAirport(selectedAirport.id)}
                        title="Xóa sân bay"
                    >
                        <span className="material-symbols-outlined">delete</span>
                    </button>
                )}
            </div>

            {showCreateModal && (
                <div className="airport-modal-overlay" onClick={() => setShowCreateModal(false)}>
                    <div className="airport-modal" onClick={e => e.stopPropagation()}>
                        <h3>Tạo sân bay mới</h3>
                        <div className="airport-form">
                            <label>
                                Tên sân bay
                                <input
                                    type="text"
                                    value={newAirportName}
                                    onChange={e => setNewAirportName(e.target.value)}
                                    placeholder="Sân bay Tân Sơn Nhất"
                                />
                            </label>
                            <div className="airport-form-row">
                                <label>
                                    Vĩ độ (Lat)
                                    <input
                                        type="number"
                                        step="0.0001"
                                        value={newAirportLat}
                                        onChange={e => setNewAirportLat(e.target.value)}
                                        placeholder="10.8188"
                                    />
                                </label>
                                <label>
                                    Kinh độ (Lng)
                                    <input
                                        type="number"
                                        step="0.0001"
                                        value={newAirportLng}
                                        onChange={e => setNewAirportLng(e.target.value)}
                                        placeholder="106.6520"
                                    />
                                </label>
                            </div>
                        </div>
                        <div className="airport-modal-actions">
                            <button onClick={() => setShowCreateModal(false)}>Hủy</button>
                            <button className="primary" onClick={handleCreateAirport}>Tạo</button>
                        </div>
                    </div>
                </div>
            )}

            {showUploadModal && (
                <div className="airport-modal-overlay" onClick={() => setShowUploadModal(false)}>
                    <div className="airport-modal" onClick={e => e.stopPropagation()}>
                        <h3>Upload GeoJSON</h3>
                        <div className="airport-form">
                            <label>
                                File GeoJSON
                                <input
                                    type="file"
                                    accept=".geojson,.json"
                                    onChange={e => setUploadFile(e.target.files?.[0] || null)}
                                />
                            </label>
                            <label>
                                Tên sân bay
                                <input
                                    type="text"
                                    value={newAirportName}
                                    onChange={e => setNewAirportName(e.target.value)}
                                    placeholder="Sân bay Đà Nẵng"
                                />
                            </label>
                            <div className="airport-form-row">
                                <label>
                                    Vĩ độ tâm (Lat)
                                    <input
                                        type="number"
                                        step="0.0001"
                                        value={newAirportLat}
                                        onChange={e => setNewAirportLat(e.target.value)}
                                        placeholder="16.0544"
                                    />
                                </label>
                                <label>
                                    Kinh độ tâm (Lng)
                                    <input
                                        type="number"
                                        step="0.0001"
                                        value={newAirportLng}
                                        onChange={e => setNewAirportLng(e.target.value)}
                                        placeholder="108.1992"
                                    />
                                </label>
                            </div>
                        </div>
                        <div className="airport-modal-actions">
                            <button onClick={() => setShowUploadModal(false)}>Hủy</button>
                            <button className="primary" onClick={handleUploadGeoJSON}>Upload</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
