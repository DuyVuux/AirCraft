import React, { useMemo, useEffect } from 'react';
import type { Aircraft } from '@/types/aircraft';
import type { MapNode } from '@/types/mapEditor';
import type { POIFeature } from '@/services/poiService';
import { DEFAULT_GPS } from '@/utils/constants';
import MapPicker from '@/components/common/MapPicker';
import './Editor.css';

interface AircraftStandMapProps {
    aircraft: Aircraft;
    onChange: (field: keyof Aircraft, value: any) => void;
    mapNodes?: MapNode[];
    allAircrafts?: Aircraft[];
    isReadOnly?: boolean;
}

const AircraftStandMap: React.FC<AircraftStandMapProps> = ({
    aircraft,
    onChange,
    mapNodes = [],
    allAircrafts = [],
    isReadOnly = false,
}) => {
    // Determine occupied OSM IDs
    const occupiedOsmIds = useMemo(() => {
        return allAircrafts
            .filter(a => a.aircraftId !== aircraft.aircraftId && a.location.locationId)
            .map(a => a.location.locationId);
    }, [allAircrafts, aircraft.aircraftId]);

    // Filter stand nodes
    const aircraftStandNodes = useMemo(() => {
        return mapNodes.filter(n => n.type === 'aircraft_stand');
    }, [mapNodes]);

    // Create custom POIs for stands
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

    // Debugging Lifecycle: Log mount/unmount to verification
    useEffect(() => {
        console.group(`[AircraftStandMap] Lifecycle Check`);
        console.log('Mounted with aircraftId:', aircraft.aircraftId);
        console.groupEnd();

        return () => {
            console.log(`[AircraftStandMap] Unmounting`);
        };
    }, []);

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', height: '100%' }}>
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
                    {/* 
                         CRITICAL: We rely on MapPicker's internal key or stable mounting. 
                         If MapPicker itself does not handle remounting gracefully, we might still see issues.
                         However, in this isolated component, we ensure that we don't force unnecessary remounts via props.
                     */}
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
                            if (isReadOnly) return;

                            const currentLocationId = aircraft.location.locationId;

                            if (osmId === currentLocationId) {
                                // Deselect
                                onChange('location', {
                                    ...aircraft.location,
                                    locationId: '',
                                    longitude: DEFAULT_GPS.longitude,
                                    latitude: DEFAULT_GPS.latitude,
                                });
                            } else {
                                // Select
                                onChange('location', {
                                    ...aircraft.location,
                                    locationId: osmId,
                                    longitude: centroid.longitude,
                                    latitude: centroid.latitude,
                                    locationType: 'APRON' as const,
                                });
                            }
                        }}
                        height="100%"
                        hideTitle={true}
                        hideCoordinates={true}
                        hideWrapper={true}
                    />
                </div>

                <p className="editor-form-helper">
                    {aircraft.location.locationId
                        ? 'Click vị trí hiện tại để hủy chọn'
                        : 'Click chọn ô trên bản đồ'}
                </p>
            </div>
        </div>
    );
};

export default AircraftStandMap;
