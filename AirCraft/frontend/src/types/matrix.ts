export interface DistanceMatrixEntry {
  source?: string; // For backward compatibility
  destination?: string; // For backward compatibility
  srcCode: string; // Source location code
  destCode: string; // Destination location code
  value?: number; // km (old format, for backward compatibility)
  travelTime: number; // Travel time in seconds (new format)
}

export interface TimeMatrixLevel {
  levelId: number;
  timeProcess: number; // minutes
}

export interface TimeMatrixRole {
  role: string;
  levels: TimeMatrixLevel[];
}

export interface TimeMatrixEntry {
  taskCode: string;
  roles?: TimeMatrixRole[]; // Old format (nested) - for backward compatibility
  role: string; // Role name (new format)
  level: number; // Level (1, 2, 3) (new format)
  aircraftId?: string; // Optional: specific aircraft ID
  timeProcess: number; // Time process in seconds (new format) or minutes (old format for backward compatibility)
}

export interface MatrixConfigs {
  distanceMatrix: DistanceMatrixEntry[];
  timeMatrix: TimeMatrixEntry[];
}

