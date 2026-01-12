import { useGlobalData } from '@/contexts/GlobalDataContext';
import DatasetManager from '@/components/common/DatasetManager';
import AirportSelector from '@/components/common/AirportSelector';

function SharedHeaderActions() {
    const {
        currentAirport,
        handleAirportChange,
        setCurrentAirport,
        setMapNodes,
        setMapRoutes,
        handleExportJSON,
        aircrafts,
        employees,
        hubs,
        datasetManager,
    } = useGlobalData();

    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <AirportSelector
                selectedAirportId={currentAirport?.id || null}
                onAirportChange={handleAirportChange}
                onAirportDeleted={() => {
                    setCurrentAirport(null);
                    setMapNodes([]);
                    setMapRoutes([]);
                }}
            />
            <DatasetManager
                datasets={datasetManager.datasets}
                currentDatasetId={datasetManager.currentDatasetId}
                onSelectDataset={datasetManager.handleSelectDataset}
                onCreateDataset={datasetManager.handleCreateDataset}
                onDeleteDataset={datasetManager.handleDeleteDataset}
                onRenameDataset={datasetManager.handleRenameDataset}
            />
            <button
                className="layout-header-button"
                onClick={handleExportJSON}
                disabled={!aircrafts.length && !employees.length && !hubs.length}
            >
                <span className="material-symbols-outlined">file_upload</span>
                Export JSON
            </button>
        </div>
    );
}

export default SharedHeaderActions;
