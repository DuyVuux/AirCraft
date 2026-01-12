import React, { useState } from 'react';
import {
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Paper,
  Typography,
  Stack,
} from '@mui/material';
import type { DistanceMatrixEntry } from '@/types/matrix';
import { generateDistanceMatrix } from '@/utils/distanceCalculator';

interface DistanceMatrixEditorProps {
  onSave?: (entry: DistanceMatrixEntry) => void;
  onDelete?: (index: number) => void;
  onStartEdit?: () => void;
  initialData?: DistanceMatrixEntry | null;
  isEditing?: boolean;
  availableLocations?: string[];
  aircrafts?: Array<{ location: { locationId: string; locationType: string; longitude: number; latitude: number } }>;
  hubs?: Array<{ location: { locationId: string; locationType: string; longitude: number; latitude: number } }>;
}

const DistanceMatrixEditor: React.FC<DistanceMatrixEditorProps> = ({
  onSave,
  onDelete,
  onStartEdit,
  initialData,
  isEditing = false,
  availableLocations = [],
  aircrafts = [],
  hubs = [],
}) => {
  const [entry, setEntry] = useState<DistanceMatrixEntry>(
    initialData || {
      srcCode: '',
      destCode: '',
      travelTime: 0,
    }
  );

  // Determine if fields should be read-only
  const isReadOnly = !!(initialData && !isEditing);

  // Collect all locations from aircrafts and hubs
  const allLocations = React.useMemo(() => {
    const locations = new Set<string>();
    aircrafts.forEach((ac) => {
      const loc = ac.location?.locationId;
      if (loc) locations.add(loc);
    });
    hubs.forEach((hub) => {
      const loc = hub.location?.locationId;
      if (loc) locations.add(loc);
    });
    availableLocations.forEach((loc) => locations.add(loc));
    return Array.from(locations);
  }, [aircrafts, hubs, availableLocations]);

  const handleChange = (field: keyof DistanceMatrixEntry, value: any) => {
    setEntry((prev) => ({ ...prev, [field]: value }));
  };

  const handleSave = () => {
    const src = entry.srcCode || entry.source || '';
    const dest = entry.destCode || entry.destination || '';
    if (!src || !dest) {
      return;
    }
    onSave?.(entry);
    // Reset form after save
    if (!initialData) {
      setEntry({
        srcCode: '',
        destCode: '',
        travelTime: 0,
      });
    }
  };

  const handleDelete = () => {
    if (initialData && onDelete) {
      onDelete(0);
    }
  };

  const handleAutoGenerate = () => {
    // Collect locations with GPS coordinates
    const locationsWithGPS = allLocations.map((locId) => {
      // Try to find in aircrafts
      const aircraft = aircrafts.find((ac) => ac.location?.locationId === locId);
      if (aircraft && aircraft.location) {
        return {
          location: locId,
          longitude: aircraft.location.longitude || 0,
          latitude: aircraft.location.latitude || 0,
        };
      }

      // Try to find in hubs
      const hub = hubs.find((h) => h.location?.locationId === locId);
      if (hub && hub.location) {
        return {
          location: locId,
          longitude: hub.location.longitude || 0,
          latitude: hub.location.latitude || 0,
        };
      }

      return null;
    }).filter((loc): loc is { location: string; longitude: number; latitude: number } => loc !== null);

    if (locationsWithGPS.length < 2) {
      alert('Cần ít nhất 2 locations có GPS coordinates để auto-generate');
      return;
    }

    const matrix = generateDistanceMatrix(locationsWithGPS);
    // Call onSave for each entry
    // Convert km to seconds (assuming average speed 5 km/h = 1.39 m/s, so 1km ≈ 720 seconds)
    matrix.forEach((m) => {
      onSave?.({
        srcCode: m.source,
        destCode: m.destination,
        travelTime: Math.round(m.value * 720), // Convert km to seconds (rough estimate)
      });
    });
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        {initialData ? 'Edit Distance Matrix Entry' : 'Add New Distance Matrix Entry'}
      </Typography>

      {isReadOnly && (
        <Typography
          variant="body2"
          sx={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 0.5,
            mb: 1.5,
            px: 1,
            py: 0.25,
            bgcolor: 'rgba(59, 130, 246, 0.08)',
            border: '1px solid rgba(59, 130, 246, 0.2)',
            borderRadius: 1,
            color: 'primary.main',
            fontSize: '0.75rem',
          }}
        >
          🔒 Chế độ chỉ đọc — Nhấn "Update" để chỉnh sửa
        </Typography>
      )}

      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Source Location</InputLabel>
            <Select
              value={entry.srcCode || entry.source || ''}
              label="Source Location"
              onChange={(e) => {
                handleChange('srcCode', e.target.value);
                handleChange('source', e.target.value); // For backward compatibility
              }}
              disabled={isReadOnly}
            >
              {allLocations.map((loc) => (
                <MenuItem key={loc} value={loc}>
                  {loc}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Destination Location</InputLabel>
            <Select
              value={entry.destCode || entry.destination || ''}
              label="Destination Location"
              onChange={(e) => {
                handleChange('destCode', e.target.value);
                handleChange('destination', e.target.value); // For backward compatibility
              }}
              disabled={isReadOnly}
            >
              {allLocations.map((loc) => (
                <MenuItem key={loc} value={loc}>
                  {loc}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={2}>
          <TextField
            fullWidth
            label="Travel Time (seconds)"
            type="number"
            value={entry.travelTime || entry.value || 0}
            onChange={(e) => {
              const val = parseInt(e.target.value) || 0;
              handleChange('travelTime', val);
              handleChange('value', val); // For backward compatibility
            }}
            inputProps={{ min: 0 }}
            helperText={`${Math.round((entry.travelTime || entry.value || 0) / 60)} minutes`}
            required
            InputProps={{
              readOnly: isReadOnly,
            }}
          />
        </Grid>

        <Grid item xs={12} md={2}>
          <Button
            variant="outlined"
            fullWidth
            onClick={handleAutoGenerate}
            disabled={allLocations.length < 2 || isReadOnly}
            sx={{ height: '56px' }}
          >
            Auto Generate
          </Button>
        </Grid>

        <Grid item xs={12}>
          <Stack direction="row" spacing={2}>
            {isReadOnly ? (
              <>
                <Button variant="contained" color="primary" onClick={onStartEdit}>
                  Update
                </Button>
                {onDelete && (
                  <Button variant="outlined" color="error" onClick={handleDelete}>
                    Delete
                  </Button>
                )}
              </>
            ) : (
              <>
                <Button variant="contained" onClick={handleSave}>
                  {initialData ? 'Save Changes' : 'Add'} Entry
                </Button>
                {initialData && onDelete && (
                  <Button variant="outlined" color="error" onClick={handleDelete}>
                    Delete
                  </Button>
                )}
              </>
            )}
          </Stack>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default DistanceMatrixEditor;

