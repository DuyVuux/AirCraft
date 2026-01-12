import React, { useState } from 'react';
import type { Hub } from '@/types/hub';
import type { Location } from '@/types/aircraft';
import { DEFAULT_GPS } from '@/utils/constants';
import MapPicker from '@/components/common/MapPicker';
import './Editor.css';

interface HubEditorProps {
  onSave?: (hub: Hub) => void;
  onDelete?: (hubId: string) => void;
  onStartEdit?: () => void;
  initialData?: Hub | null;
  isEditing?: boolean;
}

const HubEditor: React.FC<HubEditorProps> = ({
  onSave,
  onDelete,
  onStartEdit,
  initialData,
  isEditing = false,
}) => {
  const [hub, setHub] = useState<Hub>(
    initialData || {
      hubId: '',
      location: {
        locationId: '',
        locationType: 'HUB',
        longitude: DEFAULT_GPS.longitude,
        latitude: DEFAULT_GPS.latitude,
      },
    }
  );
  const [showMap, setShowMap] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Determine if fields should be read-only
  const isReadOnly = !!(initialData && !isEditing);

  // Validation function
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!hub.hubId.trim()) {
      newErrors.hubId = 'Hub ID là bắt buộc';
    }

    if (!hub.location.locationId.trim()) {
      newErrors.locationId = 'Location ID (OSM @Id) là bắt buộc';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Check if form is valid
  const isFormValid = (): boolean => {
    return (
      hub.hubId.trim() !== '' &&
      hub.location.locationId.trim() !== ''
    );
  };

  const handleChange = (field: keyof Hub, value: any) => {
    setHub((prev) => ({ ...prev, [field]: value }));
  };

  const handleLocationChange = (field: keyof Location, value: any) => {
    setHub((prev) => ({
      ...prev,
      location: {
        ...prev.location,
        [field]: value,
      },
    }));
  };

  const handleSave = () => {
    if (!validateForm()) {
      return;
    }
    onSave?.(hub);
  };

  const handleDelete = () => {
    if (window.confirm('Bạn có chắc chắn muốn xóa hub này không?')) {
      if (hub.hubId && onDelete) {
        onDelete(hub.hubId);
      }
    }
  };

  return (
    <>
      {isReadOnly && (
        <div className="editor-readonly-banner">
          <span className="material-symbols-outlined">lock</span>
          Chế độ chỉ đọc — Nhấn "Update" để chỉnh sửa
        </div>
      )}

      {/* Thông tin Hub */}
      <div className="editor-card">
        <h3 className="editor-card-title">Add New Hub</h3>
        <p className="editor-card-description">Thông tin Hub</p>
        <div className="editor-form-grid">
          <div className="editor-form-group">
            <label className="editor-form-label" htmlFor="hub-id">
              Hub ID *
            </label>
            <input
              className="editor-form-input"
              id="hub-id"
              type="text"
              value={hub.hubId}
              onChange={(e) => {
                handleChange('hubId', e.target.value);
                if (errors.hubId) {
                  setErrors((prev) => ({ ...prev, hubId: '' }));
                }
              }}
              placeholder="HUB_VAECO_1"
              required
              readOnly={isReadOnly}
              style={errors.hubId ? { borderColor: 'var(--color-danger)' } : {}}
            />
            {errors.hubId && (
              <p className="editor-form-helper text-danger" style={{ marginTop: '0.25rem' }}>
                {errors.hubId}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Thông tin vị trí */}
      <div className="editor-card">
        <h3 className="editor-card-title">Thông tin vị trí</h3>
        <div className="editor-form-group" style={{ marginBottom: '1rem' }}>
          <label className="editor-form-label" htmlFor="location-id">
            Location ID (OSM @Id) *
          </label>
          <input
            className="editor-form-input"
            id="location-id"
            type="text"
            value={hub.location.locationId}
            onChange={(e) => {
              handleLocationChange('locationId', e.target.value);
              if (errors.locationId) {
                setErrors((prev) => ({ ...prev, locationId: '' }));
              }
            }}
            placeholder="Location ID (OSM @Id)"
            required
            readOnly
            style={errors.locationId ? { borderColor: 'var(--color-danger)' } : {}}
          />
          {errors.locationId ? (
            <p className="editor-form-helper text-danger" style={{ marginTop: '0.25rem' }}>
              {errors.locationId}
            </p>
          ) : (
            <p className="editor-form-helper">Chọn vùng POI trên bản đồ để tự động điền OSM @Id và centroid</p>
          )}
        </div>
        <button
          className="editor-form-button-map"
          onClick={() => setShowMap(!showMap)}
          type="button"
        >
          <span className="material-symbols-outlined">map</span>
          {showMap ? 'HIDE MAP' : 'SHOW MAP'}
        </button>
        {showMap && (
          <div>
            <label className="editor-form-label">Chọn vị trí trên bản đồ</label>
            <p className="editor-form-helper" style={{ marginBottom: '0.5rem' }}>
              Click trên bản đồ để chọn vị trí, hoặc tìm kiếm địa điểm
            </p>
            <div className="editor-map-container">
              <MapPicker
                longitude={hub.location.longitude}
                latitude={hub.location.latitude}
                onLocationChange={(lon, lat) => {
                  handleLocationChange('longitude', lon);
                  handleLocationChange('latitude', lat);
                }}
                showPOI={true}
                poiType="hub"
                onPOIClick={async (osmId, centroid) => {
                  handleLocationChange('locationId', osmId);
                  handleLocationChange('longitude', centroid.longitude);
                  handleLocationChange('latitude', centroid.latitude);
                  handleLocationChange('locationType', 'HUB');
                }}
                height="32rem"
                hideTitle={true}
                hideCoordinates={true}
                hideWrapper={true}
              />
            </div>
            <div className="editor-form-grid" style={{ marginTop: '1rem' }}>
              <div className="editor-form-group">
                <label className="editor-form-label" htmlFor="latitude">
                  Latitude
                </label>
                <input
                  className="editor-form-input"
                  id="latitude"
                  type="text"
                  value={hub.location.latitude.toFixed(6)}
                  onChange={(e) => handleLocationChange('latitude', parseFloat(e.target.value) || 0)}
                  readOnly={isReadOnly}
                />
              </div>
              <div className="editor-form-group">
                <label className="editor-form-label" htmlFor="longitude">
                  Longitude
                </label>
                <input
                  className="editor-form-input"
                  id="longitude"
                  type="text"
                  value={hub.location.longitude.toFixed(6)}
                  onChange={(e) => handleLocationChange('longitude', parseFloat(e.target.value) || 0)}
                  readOnly={isReadOnly}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div style={{ marginTop: '2rem' }}>
        {isReadOnly ? (
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              className="editor-form-button-primary"
              onClick={onStartEdit}
            >
              Update
            </button>
            {onDelete && (
              <button
                className="editor-form-button-secondary text-danger"
                onClick={handleDelete}
                style={{ borderColor: 'var(--color-danger)' }}
              >
                Delete
              </button>
            )}
          </div>
        ) : (
          <button
            className="editor-form-button-primary"
            onClick={handleSave}
            disabled={!isFormValid()}
            style={{
              opacity: !isFormValid() ? 0.5 : 1,
              cursor: !isFormValid() ? 'not-allowed' : 'pointer',
            }}
          >
            {initialData ? 'SAVE CHANGES' : 'ADD HUB'}
          </button>
        )}
      </div>
    </>
  );
};

export default HubEditor;
