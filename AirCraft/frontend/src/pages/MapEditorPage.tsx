import Layout from '@/components/layout/Layout';
import MapEditorTab from '@/components/editor/MapEditorTab';
import { useGlobalData } from '@/contexts/GlobalDataContext';

function MapEditorPage() {
    const { mapNodes, mapEdges, mapTrips, setMapNodes, setMapEdges, setMapTrips, isLoading } = useGlobalData();

    const handleNodesChange = (nodes: typeof mapNodes) => {
        setMapNodes(nodes);
    };

    const handleEdgesChange = (edges: typeof mapEdges) => {
        setMapEdges(edges);
    };

    const handleTripsChange = (trips: typeof mapTrips) => {
        setMapTrips(trips);
    };

    return (
        <Layout title="Chỉnh sửa bản đồ" description="Thêm, sửa, xóa các điểm và tuyến đường trên bản đồ" showSharedHeader={true}>
            <div style={{ padding: '1rem', height: 'calc(100vh - 120px)' }}>
                {isLoading ? (
                    <div style={{ textAlign: 'center', padding: '2rem' }}>
                        <span className="material-symbols-outlined" style={{ animation: 'spin 1s linear infinite' }}>sync</span>
                        <p>Đang tải dữ liệu...</p>
                    </div>
                ) : (
                    <MapEditorTab
                        nodes={mapNodes}
                        edges={mapEdges}
                        trips={mapTrips}
                        onNodesChange={handleNodesChange}
                        onEdgesChange={handleEdgesChange}
                        onTripsChange={handleTripsChange}
                    />
                )}
            </div>

            <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
        </Layout>
    );
}

export default MapEditorPage;
