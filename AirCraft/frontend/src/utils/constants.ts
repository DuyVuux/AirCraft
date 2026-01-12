// Color scheme
export const COLORS = {
  primary: '#1976d2',
  success: '#4caf50',
  warning: '#ff9800',
  error: '#f44336',
  background: '#ffffff',
  backgroundLight: '#f5f5f5',
} as const;

// Spacing
export const SPACING = {
  small: 8,
  medium: 16,
  large: 24,
  xLarge: 32,
} as const;

// Date formats
export const DATE_FORMATS = {
  iso: "yyyy-MM-dd'T'HH:mm:ss'Z'",
  dateTime: 'yyyy-MM-dd HH:mm',
  time: 'HH:mm',
} as const;

// Validation
export const VALIDATION = {
  longitude: {
    min: -180,
    max: 180,
  },
  latitude: {
    min: -90,
    max: 90,
  },
  level: {
    min: 1,
  },
} as const;

// Location patterns
export const LOCATION_PATTERNS = {
  gate: /^GATE-\d+$/,
  hangar: /^HANGAR-\d+$/,
  apron: /^APRON-\d+$/,
  restArea: /^REST_AREA_[A-Z]$/,
} as const;

// Default GPS coordinates (Noi Bai Airport - Sân Bay Nội Bài)
export const DEFAULT_GPS = {
  longitude: 105.8067,
  latitude: 21.2144,
} as const;

