import type { TabProps, TabConfig } from './types';
import MapEditorTab from '@/components/editor/MapEditorTab';

export const tabConfig: TabConfig = {
    id: 'edit-map',
    label: 'EDIT MAP',
    order: 5,
};

export default function MapTab({
    mapNodes,
    setMapNodes,
    currentAirport,
}: TabProps) {
    // MapEditorTab expects: nodes, edges, trips
    // We'll use empty arrays for edges and trips if not provided
    return (
        <MapEditorTab
            nodes={mapNodes}
            edges={[]}
            trips={[]}
            onNodesChange={setMapNodes}
            onEdgesChange={() => { }}
            onTripsChange={() => { }}
            center={currentAirport?.center}
            defaultZoom={currentAirport?.defaultZoom}
        />
    );
}
