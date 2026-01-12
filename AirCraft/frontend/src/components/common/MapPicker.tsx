import React, { useEffect, useState, useCallback, useRef } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents, useMap, GeoJSON } from 'react-leaflet';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Stack,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Autocomplete,
  CircularProgress,
} from '@mui/material';
import MyLocationIcon from '@mui/icons-material/MyLocation';
import SearchIcon from '@mui/icons-material/Search';
import FullscreenIcon from '@mui/icons-material/Fullscreen';
import FullscreenExitIcon from '@mui/icons-material/FullscreenExit';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { DEFAULT_GPS } from '@/utils/constants';
import { loadAircraftStandsPOI, loadHubPOI, type POIFeature } from '@/services/poiService';
import * as turf from '@turf/turf';

interface SearchResult {
  display_name: string;
  lat: string;
  lon: string;
  type: string;
  importance: number;
}

interface MapPickerProps {
  longitude: number;
  latitude: number;
  onLocationChange: (longitude: number, latitude: number) => void;
  height?: string;
  showPOI?: boolean;
  poiType?: 'aircraft' | 'hub';
  showHubs?: boolean;
  occupiedOsmIds?: string[];
  selectedLocationId?: string;
  onPOIClick?: (osmId: string, centroid: { longitude: number; latitude: number }) => void;
  hideTitle?: boolean;
  hideCoordinates?: boolean;
  hideWrapper?: boolean;
  customPOIFeatures?: POIFeature[];
}

interface MapClickHandlerProps {
  onMapClick: (lat: number, lng: number) => void;
}

const MapClickHandler: React.FC<MapClickHandlerProps> = ({ onMapClick }) => {
  useMapEvents({
    click: (e) => {
      onMapClick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
};

interface MapCenterUpdaterProps {
  latitude: number;
  longitude: number;
}

const MapCenterUpdater: React.FC<MapCenterUpdaterProps> = ({ latitude, longitude }) => {
  const map = useMap();

  useEffect(() => {
    if (map && (latitude || longitude)) {
      // Update center without resetting zoom
      map.setView([latitude || DEFAULT_GPS.latitude, longitude || DEFAULT_GPS.longitude], map.getZoom(), {
        animate: true,
        duration: 0.5,
      });
    }
  }, [map, latitude, longitude]);

  return null;
};

interface ZoomControlHandlerProps {
  onZoomChange?: (zoom: number) => void;
}

const ZoomControlHandler: React.FC<ZoomControlHandlerProps> = ({ onZoomChange }) => {
  const map = useMap();

  useEffect(() => {
    if (map && map.scrollWheelZoom) {
      // Disable default scroll wheel zoom
      map.scrollWheelZoom.disable();

      // Track zoom changes
      const handleZoomEnd = () => {
        if (onZoomChange) {
          onZoomChange(map.getZoom());
        }
      };

      map.on('zoomend', handleZoomEnd);

      // Add custom smooth zoom handler
      const handleWheel = (e: WheelEvent) => {
        e.preventDefault();
        e.stopPropagation();

        const delta = e.deltaY;
        const currentZoom = map.getZoom();
        // Zoom nhanh gấp 5 lần
        const zoomStep = delta > 0 ? -2.25 : 2.25; // Tăng từ 0.45 lên 2.25 (gấp 5 lần)
        const newZoom = currentZoom + zoomStep;

        // Giới hạn zoom level
        const minZoom = map.getMinZoom();
        const maxZoom = map.getMaxZoom();
        const clampedZoom = Math.max(minZoom, Math.min(maxZoom, newZoom));

        map.setZoom(clampedZoom, { animate: true, duration: 0.2 });
      };

      const mapContainer = map.getContainer();
      mapContainer.addEventListener('wheel', handleWheel, { passive: false });

      return () => {
        mapContainer.removeEventListener('wheel', handleWheel);
        map.off('zoomend', handleZoomEnd);
        map.scrollWheelZoom.enable();
      };
    }
  }, [map, onZoomChange]);

  return null;
};

// POI Polygons Component
interface POIPolygonsProps {
  poiFeatures: POIFeature[]; // Selectable Features (Stands)
  hubFeatures?: POIFeature[]; // Background Features (Hubs)
  selectedOsmId: string | null;
  occupiedOsmIds?: string[];
  onPOIClick?: (osmId: string, centroid: { longitude: number; latitude: number }) => void;
}

const POIPolygons: React.FC<POIPolygonsProps> = ({ poiFeatures, selectedOsmId, occupiedOsmIds = [], onPOIClick }) => {
  const [highlightedLayer, setHighlightedLayer] = useState<L.Layer | null>(null);

  // Default style for POI polygons - available stands (blue)
  const defaultStyle = {
    color: '#10b981',
    fillColor: '#10b981',
    fillOpacity: 0.5,
    weight: 2,
  };

  // Occupied style for stands with aircraft (red)
  const occupiedStyle = {
    color: '#ef4444',
    fillColor: '#ef4444',
    fillOpacity: 0.6,
    weight: 2,
  };

  // Highlighted style for selected POI (yellow - current aircraft position)
  const highlightedStyle = {
    color: '#facc15',
    fillColor: '#facc15',
    fillOpacity: 0.8,
    weight: 3,
  };

  // Convert Point to square polygon
  // Create a square centered at the point with ~1200m side length
  const convertPointToPolygon = (feature: POIFeature): GeoJSON.Feature => {
    if (feature.geometry.type === 'Point') {
      const coords = feature.geometry.coordinates;
      if (Array.isArray(coords) && coords.length === 2 && typeof coords[0] === 'number') {
        const [lon, lat] = coords as [number, number];

        // Create a square polygon centered at the point
        // Side length: ~0.012 km = ~1200m (gấp 2 lần 600m)
        // Half side: ~0.006 km = ~600m
        const halfSide = 0.006; // ~600m in degrees (approximately)

        // Calculate square corners (approximate, works well for small areas)
        // 1 degree latitude ≈ 111 km, so 0.003 km ≈ 0.000027 degrees
        const latOffset = halfSide / 111; // ~0.000027 degrees
        const lonOffset = halfSide / (111 * Math.cos(lat * Math.PI / 180)); // Adjust for longitude

        // Create square polygon coordinates [lon, lat]
        const squareCoordinates: number[][][] = [[
          [lon - lonOffset, lat - latOffset], // Bottom-left
          [lon + lonOffset, lat - latOffset], // Bottom-right
          [lon + lonOffset, lat + latOffset], // Top-right
          [lon - lonOffset, lat + latOffset], // Top-left
          [lon - lonOffset, lat - latOffset], // Close the polygon
        ]];

        return {
          ...feature,
          geometry: {
            type: 'Polygon',
            coordinates: squareCoordinates,
          },
        } as GeoJSON.Feature;
      }
    }
    // If already Polygon or MultiPolygon, use directly without conversion
    return feature as GeoJSON.Feature;
  };

  // Calculate centroid for any geometry type
  const calculateCentroid = (feature: POIFeature): { longitude: number; latitude: number } => {
    if (feature.geometry.type === 'Point') {
      const coords = feature.geometry.coordinates;
      if (Array.isArray(coords) && coords.length === 2 && typeof coords[0] === 'number') {
        const [lon, lat] = coords as [number, number];
        return { longitude: lon, latitude: lat };
      }
    }

    // For Polygon/MultiPolygon, use turf centroid
    const geoJsonFeature = feature as GeoJSON.Feature;
    const centroid = turf.centroid(geoJsonFeature);
    const [lon, lat] = centroid.geometry.coordinates as [number, number];
    return { longitude: lon, latitude: lat };
  };

  const handleFeatureClick = (feature: POIFeature, layer: L.Layer) => {
    // Reset previous highlight
    if (highlightedLayer && highlightedLayer !== layer) {
      const prevPath = highlightedLayer as L.Path;
      if (prevPath && prevPath.setStyle) {
        prevPath.setStyle(defaultStyle);
      }
    }

    // Highlight clicked polygon
    const pathLayer = layer as L.Path;
    if (pathLayer && pathLayer.setStyle) {
      pathLayer.setStyle(highlightedStyle);
    }
    setHighlightedLayer(layer);

    // Calculate centroid
    const centroid = calculateCentroid(feature);
    const osmId = feature.properties.locationId; // This is OSM @id

    // Call callback with OSM @id and centroid
    if (onPOIClick) {
      onPOIClick(osmId, centroid);
    }
  };

  return (
    <>
      {poiFeatures.map((feature) => {
        const convertedFeature = convertPointToPolygon(feature);
        const osmId = feature.properties.locationId;
        const isSelected = selectedOsmId === osmId;
        const isOccupied = occupiedOsmIds.includes(osmId);

        const getStyle = () => {
          if (isSelected) return highlightedStyle;
          if (isOccupied) return occupiedStyle;
          return defaultStyle;
        };

        const baseStyle = isOccupied ? occupiedStyle : defaultStyle;

        return (
          <GeoJSON
            key={osmId}
            data={convertedFeature as GeoJSON.Feature}
            style={getStyle()}
            eventHandlers={{
              click: (e) => {
                const layer = e.target;
                handleFeatureClick(feature, layer);
              },
              mouseover: (e) => {
                const pathLayer = e.target as L.Path;
                if (pathLayer && pathLayer.setStyle && !isSelected) {
                  pathLayer.setStyle({
                    ...baseStyle,
                    fillOpacity: 0.7,
                    weight: 2.5,
                  });
                }
              },
              mouseout: (e) => {
                const pathLayer = e.target as L.Path;
                if (pathLayer && pathLayer !== highlightedLayer && pathLayer.setStyle) {
                  pathLayer.setStyle(getStyle());
                }
              },
            }}
          />
        );
      })}
    </>
  );
};

const MapPicker: React.FC<MapPickerProps> = ({
  longitude,
  latitude,
  onLocationChange,
  height = '400px',
  showPOI = false,
  poiType = 'aircraft',
  showHubs = false,
  occupiedOsmIds = [],
  selectedLocationId,
  onPOIClick,
  hideTitle = false,
  hideCoordinates = false,
  hideWrapper = false,
  customPOIFeatures,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
  const [currentZoom, setCurrentZoom] = useState(18);
  const [poiFeatures, setPoiFeatures] = useState<POIFeature[]>([]);
  const [hubFeatures, setHubFeatures] = useState<POIFeature[]>([]);
  const [selectedOsmId, setSelectedOsmId] = useState<string | null>(null);
  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (customPOIFeatures && customPOIFeatures.length > 0) {
      setPoiFeatures(customPOIFeatures);
      return;
    }

    if (showPOI) {
      const loadPrimary = poiType === 'hub' ? loadHubPOI() : loadAircraftStandsPOI();
      loadPrimary
        .then((data) => {
          setPoiFeatures(data.features);
        })
        .catch((error) => {
          console.error(`Error loading ${poiType} POI data:`, error);
        });

      if (showHubs && poiType !== 'hub') {
        loadHubPOI()
          .then((data) => {
            setHubFeatures(data.features);
          })
          .catch((error) => {
            console.error(`Error loading Hub background data:`, error);
          });
      }
    }
  }, [showPOI, poiType, showHubs, customPOIFeatures]);

  // Fix default marker icon issue
  useEffect(() => {
    delete (L.Icon.Default.prototype as any)._getIconUrl;
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
      iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
    });
  }, []);

  // Cleanup debounce timeout on unmount
  useEffect(() => {
    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, []);

  const handleMapClick = (lat: number, lng: number) => {
    onLocationChange(lng, lat);
  };

  const fetchSuggestions = useCallback(async (query: string) => {
    if (!query.trim() || query.length < 2) {
      setSearchResults([]);
      return;
    }

    setIsLoadingSuggestions(true);
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5&addressdetails=1&extratags=1`,
        {
          headers: {
            'User-Agent': 'Aircraft-Web-App',
          },
        }
      );

      const data = await response.json();
      if (data && Array.isArray(data)) {
        // Sort by importance (higher is better)
        const sorted = data.sort((a, b) => (b.importance || 0) - (a.importance || 0));
        setSearchResults(sorted);
      } else {
        setSearchResults([]);
      }
    } catch (error) {
      console.error('Search suggestions error:', error);
      setSearchResults([]);
    } finally {
      setIsLoadingSuggestions(false);
    }
  }, []);

  const handleSearchInputChange = (value: string) => {
    setSearchQuery(value);

    // Clear previous timeout
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }

    // Debounce: wait 300ms after user stops typing
    debounceTimeoutRef.current = setTimeout(() => {
      fetchSuggestions(value);
    }, 300);
  };

  const handleSearch = async (selectedResult?: SearchResult) => {
    const query = selectedResult ? selectedResult.display_name : searchQuery;
    if (!query.trim()) return;

    setIsSearching(true);
    try {
      let result: SearchResult;

      if (selectedResult) {
        result = selectedResult;
      } else {
        const response = await fetch(
          `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`,
          {
            headers: {
              'User-Agent': 'Aircraft-Web-App',
            },
          }
        );

        const data = await response.json();
        if (data && data.length > 0) {
          result = data[0];
        } else {
          return;
        }
      }

      const lat = parseFloat(result.lat);
      const lon = parseFloat(result.lon);
      onLocationChange(lon, lat);
      setSearchQuery(result.display_name);
      setSearchResults([]);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const handleUseCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          onLocationChange(position.coords.longitude, position.coords.latitude);
        },
        (error) => {
          console.error('Geolocation error:', error);
        }
      );
    }
  };

  const renderMapControls = (showFullscreenButton: boolean = true) => (
    <Stack direction="row" spacing={1} sx={{ mb: 2 }} alignItems="flex-start">
      <Autocomplete
        freeSolo
        options={searchResults}
        getOptionLabel={(option) =>
          typeof option === 'string' ? option : option.display_name
        }
        value={searchQuery}
        onInputChange={(_, newValue) => handleSearchInputChange(newValue)}
        onChange={(_, newValue) => {
          if (newValue && typeof newValue !== 'string') {
            handleSearch(newValue);
          }
        }}
        loading={isLoadingSuggestions}
        filterOptions={(x) => x} // Disable default filtering, we use API results
        renderInput={(params) => (
          <TextField
            {...params}
            size="small"
            placeholder="Tìm kiếm địa điểm (ví dụ: Noi Bai Airport)"
            onKeyPress={(e) => {
              if (e.key === 'Enter' && searchQuery.trim()) {
                handleSearch();
              }
            }}
            InputProps={{
              ...params.InputProps,
              endAdornment: (
                <>
                  {isLoadingSuggestions ? <CircularProgress color="inherit" size={20} /> : null}
                  {params.InputProps.endAdornment}
                </>
              ),
            }}
            sx={{ flex: 1 }}
          />
        )}
        renderOption={(props, option) => (
          <Box
            component="li"
            {...props}
            sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, py: 1.5 }}
          >
            <LocationOnIcon sx={{ color: 'text.secondary', mt: 0.5 }} fontSize="small" />
            <Box sx={{ flex: 1 }}>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                {option.display_name.split(',')[0]}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {option.display_name}
              </Typography>
            </Box>
          </Box>
        )}
        sx={{ flex: 1 }}
        noOptionsText="Không tìm thấy địa điểm"
        loadingText="Đang tìm kiếm..."
      />
      <Button
        variant="outlined"
        startIcon={<SearchIcon />}
        onClick={() => handleSearch()}
        disabled={isSearching || !searchQuery.trim()}
        sx={{ minWidth: 100 }}
      >
        Tìm
      </Button>
      <IconButton
        color="primary"
        onClick={handleUseCurrentLocation}
        title="Sử dụng vị trí hiện tại"
      >
        <MyLocationIcon />
      </IconButton>
      {showFullscreenButton && (
        <IconButton
          color="primary"
          onClick={() => setIsFullscreen(true)}
          title="Mở bản đồ toàn màn hình"
        >
          <FullscreenIcon />
        </IconButton>
      )}
    </Stack>
  );

  const renderMap = (mapHeight: string) => {
    // Only re-mount map when fullscreen state changes, not when location changes
    const mapKey = `map-${isFullscreen}`;

    // Convert rem to px if needed, or use directly
    const heightValue = mapHeight.includes('rem')
      ? `${parseFloat(mapHeight) * 16}px`
      : mapHeight;

    return (
      <Box
        sx={{
          height: heightValue,
          width: '100%',
          borderRadius: 1,
          overflow: 'hidden',
          border: '1px solid',
          borderColor: 'divider',
          position: 'relative',
          minHeight: '256px', // Ensure minimum height
        }}
      >
        <MapContainer
          center={[latitude || DEFAULT_GPS.latitude, longitude || DEFAULT_GPS.longitude]}
          zoom={currentZoom}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom={true}
          zoomSnap={0.25}
          key={mapKey}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <Marker position={[latitude || DEFAULT_GPS.latitude, longitude || DEFAULT_GPS.longitude]} />
          {showPOI && poiFeatures.length > 0 && (
            <POIPolygons
              poiFeatures={poiFeatures}
              hubFeatures={hubFeatures}
              selectedOsmId={selectedLocationId || selectedOsmId}
              occupiedOsmIds={occupiedOsmIds}
              onPOIClick={(osmId, centroid) => {
                // Update map center to centroid
                onLocationChange(centroid.longitude, centroid.latitude);
                setSelectedOsmId(osmId);
                // Call parent callback
                if (onPOIClick) {
                  onPOIClick(osmId, centroid);
                }
              }}
            />
          )}
          <MapClickHandler onMapClick={handleMapClick} />
          <ZoomControlHandler onZoomChange={setCurrentZoom} />
          <MapCenterUpdater latitude={latitude || DEFAULT_GPS.latitude} longitude={longitude || DEFAULT_GPS.longitude} />
        </MapContainer>
      </Box>
    );
  };

  const renderCoordinates = () => (
    <Stack direction="row" spacing={2} sx={{ mt: 2 }}>
      <TextField
        size="small"
        label="Longitude"
        type="number"
        value={longitude.toFixed(6)}
        onChange={(e) => {
          const val = parseFloat(e.target.value);
          if (!isNaN(val)) {
            onLocationChange(val, latitude);
          }
        }}
        inputProps={{ step: '0.000001' }}
        sx={{ flex: 1 }}
      />
      <TextField
        size="small"
        label="Latitude"
        type="number"
        value={latitude.toFixed(6)}
        onChange={(e) => {
          const val = parseFloat(e.target.value);
          if (!isNaN(val)) {
            onLocationChange(longitude, val);
          }
        }}
        inputProps={{ step: '0.000001' }}
        sx={{ flex: 1 }}
      />
    </Stack>
  );

  const mapContent = (
    <>
      {!hideTitle && (
        <>
          <Typography variant="subtitle2" gutterBottom>
            Chọn vị trí trên bản đồ
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
            Click trên bản đồ để chọn vị trí, hoặc tìm kiếm địa điểm
          </Typography>
        </>
      )}

      {renderMapControls(true)}
      {renderMap(height)}
      {!hideCoordinates && renderCoordinates()}
    </>
  );

  return (
    <>
      {hideWrapper ? (
        <div style={{ width: '100%', height: '100%' }}>{mapContent}</div>
      ) : (
        <Paper sx={{ p: 2, mt: 2 }}>
          {mapContent}
        </Paper>
      )}

      <Dialog
        open={isFullscreen}
        onClose={() => setIsFullscreen(false)}
        maxWidth={false}
        fullWidth
        PaperProps={{
          sx: {
            width: '95vw',
            height: '95vh',
            maxWidth: 'none',
            maxHeight: 'none',
            m: 2,
          },
        }}
      >
        <DialogTitle>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Typography variant="h6">Chọn vị trí trên bản đồ</Typography>
            <IconButton
              onClick={() => setIsFullscreen(false)}
              title="Đóng bản đồ toàn màn hình"
            >
              <FullscreenExitIcon />
            </IconButton>
          </Stack>
        </DialogTitle>
        <DialogContent sx={{ p: 2, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {renderMapControls(false)}
          {renderMap('calc(95vh - 250px)')}
          {renderCoordinates()}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setIsFullscreen(false)} variant="contained">
            Xác nhận
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default MapPicker;
