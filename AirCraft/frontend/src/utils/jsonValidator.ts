export interface ValidationError {
  field: string;
  message: string;
}

/**
 * Trích xuất và validate các biến tương ứng từ JSON, không cần match chính xác schema
 */
export const validateInputData = (data: any): ValidationError[] => {
  const errors: ValidationError[] = [];

  // Kiểm tra trackingId (có thể có hoặc không)
  if (data.trackingId && typeof data.trackingId !== 'string') {
    errors.push({ field: 'trackingId', message: 'Tracking ID must be a string' });
  }

  // Trích xuất và validate aircrafts (hỗ trợ cả 2 format)
  if (!data.aircrafts || !Array.isArray(data.aircrafts)) {
    errors.push({ field: 'aircrafts', message: 'Aircrafts array is required' });
  } else if (data.aircrafts.length === 0) {
    errors.push({ field: 'aircrafts', message: 'At least one aircraft is required' });
  } else {
    const aircraftIds = new Set<string>();
    data.aircrafts.forEach((aircraft: any, index: number) => {
      // Kiểm tra aircraftId
      if (!aircraft.aircraftId) {
        errors.push({
          field: `aircrafts[${index}].aircraftId`,
          message: 'Aircraft ID is required',
        });
      } else {
        if (aircraftIds.has(aircraft.aircraftId)) {
          errors.push({
            field: `aircrafts[${index}].aircraftId`,
            message: 'Duplicate aircraft ID',
          });
        }
        aircraftIds.add(aircraft.aircraftId);
      }

      // Trích xuất time window từ format mới hoặc cũ
      let startTime: string | null = null;
      let endTime: string | null = null;

      if (aircraft.timeWindow) {
        // Format mới
        startTime = aircraft.timeWindow.start;
        endTime = aircraft.timeWindow.end;
      } else if (aircraft.schedule) {
        // Format cũ
        startTime = aircraft.schedule.arrivalTime;
        endTime = aircraft.schedule.departureTime;
      }

      if (!startTime || !endTime) {
        errors.push({
          field: `aircrafts[${index}]`,
          message: 'Time window or schedule is required',
        });
      } else {
        try {
          const start = new Date(startTime);
          const end = new Date(endTime);
          if (isNaN(start.getTime()) || isNaN(end.getTime())) {
            errors.push({
              field: `aircrafts[${index}]`,
              message: 'Invalid date format',
            });
          } else if (start >= end) {
            errors.push({
              field: `aircrafts[${index}]`,
              message: 'Start time must be before end time',
            });
          }
        } catch (e) {
          errors.push({
            field: `aircrafts[${index}]`,
            message: 'Invalid date format',
          });
        }
      }

      // Kiểm tra location (format mới với locationId/locationType hoặc format cũ)
      const location = aircraft.location;
      if (!location) {
        errors.push({
          field: `aircrafts[${index}]`,
          message: 'Location is required',
        });
      } else if (typeof location === 'object') {
        // Format mới: {locationId, locationType, longitude, latitude}
        if (!location.locationId) {
          errors.push({
            field: `aircrafts[${index}].location.locationId`,
            message: 'Location ID is required',
          });
        }
        if (!location.locationType) {
          errors.push({
            field: `aircrafts[${index}].location.locationType`,
            message: 'Location type is required',
          });
        }
        if (typeof location.longitude !== 'number' || typeof location.latitude !== 'number') {
          errors.push({
            field: `aircrafts[${index}].location`,
            message: 'Longitude and latitude must be numbers',
          });
        }
      }
    });
  }

  // Trích xuất và validate employees (hỗ trợ cả 2 format)
  if (!data.employees || !Array.isArray(data.employees)) {
    errors.push({ field: 'employees', message: 'Employees array is required' });
  } else if (data.employees.length === 0) {
    errors.push({ field: 'employees', message: 'At least one employee is required' });
  } else {
    const employeeIds = new Set<string>();
    data.employees.forEach((employee: any, index: number) => {
      if (!employee.employeeId) {
        errors.push({
          field: `employees[${index}].employeeId`,
          message: 'Employee ID is required',
        });
      } else {
        if (employeeIds.has(employee.employeeId)) {
          errors.push({
            field: `employees[${index}].employeeId`,
            message: 'Duplicate employee ID',
          });
        }
        employeeIds.add(employee.employeeId);
      }

      // Trích xuất working times từ format mới hoặc cũ
      let workingTimes: any[] = [];
      
      if (employee.workingTimes && Array.isArray(employee.workingTimes)) {
        // Format mới
        workingTimes = employee.workingTimes;
      } else if (employee.workSchedule) {
        // Format cũ - convert sang format mới
        if (employee.workSchedule.shiftStart && employee.workSchedule.shiftEnd) {
          workingTimes = [{
            start: employee.workSchedule.shiftStart,
            end: employee.workSchedule.shiftEnd,
          }];
        }
      }

      if (workingTimes.length === 0) {
        errors.push({
          field: `employees[${index}]`,
          message: 'Working times or work schedule is required',
        });
      } else {
        workingTimes.forEach((wt: any, wtIndex: number) => {
          if (wt && wt.start && wt.end) {
            try {
              const start = new Date(wt.start);
              const end = new Date(wt.end);
              if (isNaN(start.getTime()) || isNaN(end.getTime())) {
                errors.push({
                  field: `employees[${index}].workingTimes[${wtIndex}]`,
                  message: 'Invalid date format',
                });
              } else if (start >= end) {
                errors.push({
                  field: `employees[${index}].workingTimes[${wtIndex}]`,
                  message: 'Start time must be before end time',
                });
              }
            } catch (e) {
              // Skip invalid dates
            }
          }
        });
      }
    });
  }

  // Validate hubs (new format với location object)
  if (!data.hubs || !Array.isArray(data.hubs)) {
    errors.push({
      field: 'hubs',
      message: 'Hubs array is required',
    });
  } else if (data.hubs.length === 0) {
    errors.push({
      field: 'hubs',
      message: 'At least one hub is required',
    });
  } else {
    const hubIds = new Set<string>();
    data.hubs.forEach((hub: any, index: number) => {
      if (!hub.hubId) {
        errors.push({
          field: `hubs[${index}].hubId`,
          message: 'Hub ID is required',
        });
      } else {
        if (hubIds.has(hub.hubId)) {
          errors.push({
            field: `hubs[${index}].hubId`,
            message: 'Duplicate hub ID',
          });
        }
        hubIds.add(hub.hubId);
      }

      // Validate location object
      if (hub.location) {
        if (typeof hub.location === 'object') {
          if (!hub.location.locationId) {
            errors.push({
              field: `hubs[${index}].location.locationId`,
              message: 'Location ID is required',
            });
          }
          if (!hub.location.locationType) {
            errors.push({
              field: `hubs[${index}].location.locationType`,
              message: 'Location type is required',
            });
          }
          if (typeof hub.location.longitude !== 'number' || typeof hub.location.latitude !== 'number') {
            errors.push({
              field: `hubs[${index}].location`,
              message: 'Longitude and latitude must be numbers',
            });
          }
        }
      } else {
        errors.push({
          field: `hubs[${index}].location`,
          message: 'Location is required',
        });
      }
    });
  }

  // Validate matrixConfigs (new format với travelTime/timeProcess là seconds)
  if (!data.matrixConfigs) {
    errors.push({
      field: 'matrixConfigs',
      message: 'Matrix configs is required',
    });
  } else {
    // Validate distanceMatrix
    if (!data.matrixConfigs.distanceMatrix || data.matrixConfigs.distanceMatrix.length === 0) {
      errors.push({
        field: 'matrixConfigs.distanceMatrix',
        message: 'Distance matrix is required',
      });
    } else {
      data.matrixConfigs.distanceMatrix.forEach((entry: any, index: number) => {
        if (!entry.srcCode && !entry.source) {
          errors.push({
            field: `matrixConfigs.distanceMatrix[${index}]`,
            message: 'Source code is required',
          });
        }
        if (!entry.destCode && !entry.destination) {
          errors.push({
            field: `matrixConfigs.distanceMatrix[${index}]`,
            message: 'Destination code is required',
          });
        }
        if (entry.travelTime === undefined && entry.value === undefined) {
          errors.push({
            field: `matrixConfigs.distanceMatrix[${index}]`,
            message: 'Travel time or value is required',
          });
        } else if (entry.travelTime !== undefined && typeof entry.travelTime !== 'number') {
          errors.push({
            field: `matrixConfigs.distanceMatrix[${index}].travelTime`,
            message: 'Travel time must be a number (seconds)',
          });
        }
      });
    }

    // Validate timeMatrix
    if (!data.matrixConfigs.timeMatrix || data.matrixConfigs.timeMatrix.length === 0) {
      errors.push({
        field: 'matrixConfigs.timeMatrix',
        message: 'Time matrix is required',
      });
    } else {
      data.matrixConfigs.timeMatrix.forEach((entry: any, index: number) => {
        if (!entry.taskCode) {
          errors.push({
            field: `matrixConfigs.timeMatrix[${index}]`,
            message: 'Task code is required',
          });
        }
        if (!entry.role) {
          errors.push({
            field: `matrixConfigs.timeMatrix[${index}]`,
            message: 'Role is required',
          });
        }
        if (entry.level === undefined) {
          errors.push({
            field: `matrixConfigs.timeMatrix[${index}]`,
            message: 'Level is required',
          });
        }
        if (entry.timeProcess === undefined) {
          errors.push({
            field: `matrixConfigs.timeMatrix[${index}]`,
            message: 'Time process is required',
          });
        } else if (typeof entry.timeProcess !== 'number') {
          errors.push({
            field: `matrixConfigs.timeMatrix[${index}].timeProcess`,
            message: 'Time process must be a number (seconds)',
          });
        }
      });
    }
  }

  return errors;
};

export const validateJSON = (jsonString: string): { valid: boolean; errors: ValidationError[] } => {
  try {
    const data = JSON.parse(jsonString);
    const errors = validateInputData(data);
    return {
      valid: errors.length === 0,
      errors,
    };
  } catch (error) {
    return {
      valid: false,
      errors: [
        {
          field: 'json',
          message: `Invalid JSON: ${(error as Error).message}`,
        },
      ],
    };
  }
};
