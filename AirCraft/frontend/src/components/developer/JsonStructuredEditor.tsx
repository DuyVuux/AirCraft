import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  Grid,
  Stack,
  IconButton,
  Autocomplete,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import type { InputData } from '@/types/input';
import type { Aircraft, AircraftTypeId } from '@/types/aircraft';
import type { Employee } from '@/types/employee';
import type { Hub } from '@/types/hub';
import type { DistanceMatrixEntry, TimeMatrixEntry } from '@/types/matrix';
import { AIRCRAFT_TYPES } from '@/types/aircraft';
import { ROLES } from '@/types/employee';

interface JsonStructuredEditorProps {
  onDataChange?: (data: InputData | null) => void;
  initialData?: InputData | null;
}

const LOCATION_TYPES = ['GATE', 'HANGAR', 'APRON', 'HUB', 'REST_AREA'];
const TASK_CODES = [
  'TASK_TIRE_CHECK',
  'TASK_OIL_CHANGE',
  'TASK_ENGINE_INSPECT',
  'TASK_CLEANING',
  'TASK_LOADING',
  'TASK_UNLOADING',
  'TASK_REFUEL',
  'TASK_PUSHBACK',
];

const JsonStructuredEditor: React.FC<JsonStructuredEditorProps> = ({
  onDataChange,
  initialData,
}) => {
  const [data, setData] = useState<InputData>(
    initialData || {
      trackingId: `PLAN-${new Date().toISOString().split('T')[0]}-001`,
      aircrafts: [],
      hubs: [],
      employees: [],
      matrixConfigs: {
        distanceMatrix: [],
        timeMatrix: [],
      },
    }
  );

  useEffect(() => {
    if (initialData) {
      setData(initialData);
    }
  }, [initialData]);

  useEffect(() => {
    onDataChange?.(data);
  }, [data, onDataChange]);

  const handleTrackingIdChange = (value: string) => {
    setData((prev) => ({ ...prev, trackingId: value }));
  };

  // Aircraft handlers
  const handleAddAircraft = () => {
    const newAircraft: Aircraft = {
      aircraftId: '',
      aType: { id: 'A320', desc: 'Airbus A320' },
      location: {
        locationId: '',
        locationType: 'GATE',
        longitude: 105.8067,
        latitude: 21.2144,
      },
      timeWindow: {
        start: new Date().toISOString(),
        end: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(),
      },
      requiredTasks: [],
    };
    setData((prev) => ({
      ...prev,
      aircrafts: [...prev.aircrafts, newAircraft],
    }));
  };

  const handleAircraftChange = (index: number, field: string, value: any) => {
    setData((prev) => {
      const newAircrafts = [...prev.aircrafts];
      if (field.includes('.')) {
        const [parent, child] = field.split('.');
        newAircrafts[index] = {
          ...newAircrafts[index],
          [parent]: {
            ...(newAircrafts[index] as any)[parent],
            [child]: value,
          },
        };
      } else if (field === 'location') {
        newAircrafts[index] = {
          ...newAircrafts[index],
          location: value,
        };
      } else {
        (newAircrafts[index] as any)[field] = value;
      }
      return { ...prev, aircrafts: newAircrafts };
    });
  };

  const handleRemoveAircraft = (index: number) => {
    setData((prev) => ({
      ...prev,
      aircrafts: prev.aircrafts.filter((_, i) => i !== index),
    }));
  };

  const handleAddAircraftTask = (aircraftIndex: number) => {
    setData((prev) => {
      const newAircrafts = [...prev.aircrafts];
      newAircrafts[aircraftIndex] = {
        ...newAircrafts[aircraftIndex],
        requiredTasks: [
          ...newAircrafts[aircraftIndex].requiredTasks,
          { taskCode: '', minLevel: 1 },
        ],
      };
      return { ...prev, aircrafts: newAircrafts };
    });
  };

  const handleRemoveAircraftTask = (aircraftIndex: number, taskIndex: number) => {
    setData((prev) => {
      const newAircrafts = [...prev.aircrafts];
      newAircrafts[aircraftIndex] = {
        ...newAircrafts[aircraftIndex],
        requiredTasks: newAircrafts[aircraftIndex].requiredTasks.filter(
          (_, i) => i !== taskIndex
        ),
      };
      return { ...prev, aircrafts: newAircrafts };
    });
  };

  // Hub handlers
  const handleAddHub = () => {
    const newHub: Hub = {
      hubId: '',
      location: {
        locationId: '',
        locationType: 'HUB',
        longitude: 106.6650,
        latitude: 10.8200,
      },
    };
    setData((prev) => ({
      ...prev,
      hubs: [...prev.hubs, newHub],
    }));
  };

  const handleHubChange = (index: number, field: string, value: any) => {
    setData((prev) => {
      const newHubs = [...prev.hubs];
      if (field === 'location') {
        newHubs[index] = { ...newHubs[index], location: value };
      } else {
        (newHubs[index] as any)[field] = value;
      }
      return { ...prev, hubs: newHubs };
    });
  };

  const handleRemoveHub = (index: number) => {
    setData((prev) => ({
      ...prev,
      hubs: prev.hubs.filter((_, i) => i !== index),
    }));
  };

  // Employee handlers
  const handleAddEmployee = () => {
    const newEmployee: Employee = {
      employeeId: '',
      eType: { role: 'MECHANIC' },
      workingTimes: [
        {
          start: new Date().toISOString(),
          end: new Date(Date.now() + 10 * 60 * 60 * 1000).toISOString(),
        },
      ],
      breakDuration: 3600,
      fixedBreakTimes: [],
    };
    setData((prev) => ({
      ...prev,
      employees: [...prev.employees, newEmployee],
    }));
  };

  const handleEmployeeChange = (index: number, field: string, value: any) => {
    setData((prev) => {
      const newEmployees = [...prev.employees];
      if (field.includes('.')) {
        const [parent, child] = field.split('.');
        newEmployees[index] = {
          ...newEmployees[index],
          [parent]: {
            ...(newEmployees[index] as any)[parent],
            [child]: value,
          },
        };
      } else {
        (newEmployees[index] as any)[field] = value;
      }
      return { ...prev, employees: newEmployees };
    });
  };

  const handleRemoveEmployee = (index: number) => {
    setData((prev) => ({
      ...prev,
      employees: prev.employees.filter((_, i) => i !== index),
    }));
  };

  // Distance Matrix handlers
  const handleAddDistanceEntry = () => {
    const newEntry: DistanceMatrixEntry = {
      srcCode: '',
      destCode: '',
      travelTime: 0,
    };
    setData((prev) => ({
      ...prev,
      matrixConfigs: {
        ...prev.matrixConfigs,
        distanceMatrix: [...prev.matrixConfigs.distanceMatrix, newEntry],
      },
    }));
  };

  const handleDistanceEntryChange = (index: number, field: string, value: any) => {
    setData((prev) => {
      const newMatrix = [...prev.matrixConfigs.distanceMatrix];
      (newMatrix[index] as any)[field] = value;
      return {
        ...prev,
        matrixConfigs: {
          ...prev.matrixConfigs,
          distanceMatrix: newMatrix,
        },
      };
    });
  };

  const handleRemoveDistanceEntry = (index: number) => {
    setData((prev) => ({
      ...prev,
      matrixConfigs: {
        ...prev.matrixConfigs,
        distanceMatrix: prev.matrixConfigs.distanceMatrix.filter((_, i) => i !== index),
      },
    }));
  };

  // Time Matrix handlers
  const handleAddTimeEntry = () => {
    const newEntry: TimeMatrixEntry = {
      taskCode: '',
      role: 'MECHANIC',
      level: 1,
      timeProcess: 0,
    };
    setData((prev) => ({
      ...prev,
      matrixConfigs: {
        ...prev.matrixConfigs,
        timeMatrix: [...prev.matrixConfigs.timeMatrix, newEntry],
      },
    }));
  };

  const handleTimeEntryChange = (index: number, field: string, value: any) => {
    setData((prev) => {
      const newMatrix = [...prev.matrixConfigs.timeMatrix];
      (newMatrix[index] as any)[field] = value;
      return {
        ...prev,
        matrixConfigs: {
          ...prev.matrixConfigs,
          timeMatrix: newMatrix,
        },
      };
    });
  };

  const handleRemoveTimeEntry = (index: number) => {
    setData((prev) => ({
      ...prev,
      matrixConfigs: {
        ...prev.matrixConfigs,
        timeMatrix: prev.matrixConfigs.timeMatrix.filter((_, i) => i !== index),
      },
    }));
  };

  // Collect all location IDs for autocomplete
  const allLocationIds = useMemo(() => {
    const locations = new Set<string>();
    data.aircrafts.forEach((ac) => {
      if (ac.location.locationId) locations.add(ac.location.locationId);
    });
    data.hubs.forEach((hub) => {
      if (hub.location.locationId) locations.add(hub.location.locationId);
    });
    return Array.from(locations);
  }, [data.aircrafts, data.hubs]);

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Structured JSON Editor
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Chỉnh sửa dữ liệu theo cấu trúc với autocomplete suggestions
      </Typography>

      <Paper sx={{ p: 3, mb: 2 }}>
        <TextField
          fullWidth
          label="Tracking ID"
          value={data.trackingId}
          onChange={(e) => handleTrackingIdChange(e.target.value)}
          helperText="Format: PLAN-YYYY-MM-DD-XXX"
        />
      </Paper>

      {/* Aircrafts */}
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">
            Aircrafts ({data.aircrafts.length})
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Stack spacing={2}>
            {data.aircrafts.map((aircraft, index) => (
              <Paper key={index} sx={{ p: 2 }}>
                <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                  <Typography variant="subtitle1">Aircraft #{index + 1}</Typography>
                  <IconButton
                    color="error"
                    size="small"
                    onClick={() => handleRemoveAircraft(index)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Stack>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Aircraft ID"
                      value={aircraft.aircraftId}
                      onChange={(e) => handleAircraftChange(index, 'aircraftId', e.target.value)}
                      placeholder="VN-A320"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <Autocomplete
                      options={Object.keys(AIRCRAFT_TYPES)}
                      getOptionLabel={(option) => AIRCRAFT_TYPES[option as AircraftTypeId]}
                      value={aircraft.aType.id}
                      onChange={(_, newValue) => {
                        if (newValue) {
                          handleAircraftChange(index, 'aType', {
                            id: newValue,
                            desc: AIRCRAFT_TYPES[newValue as AircraftTypeId],
                          });
                        }
                      }}
                      renderInput={(params) => (
                        <TextField {...params} label="Aircraft Type" />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Autocomplete
                      freeSolo
                      options={allLocationIds}
                      value={aircraft.location.locationId}
                      onChange={(_, newValue) => {
                        handleAircraftChange(index, 'location', {
                          ...aircraft.location,
                          locationId: newValue || '',
                        });
                      }}
                      onInputChange={(_, newValue) => {
                        handleAircraftChange(index, 'location', {
                          ...aircraft.location,
                          locationId: newValue,
                        });
                      }}
                      renderInput={(params) => (
                        <TextField {...params} label="Location ID" placeholder="GATE-01" />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Autocomplete
                      options={LOCATION_TYPES}
                      value={aircraft.location.locationType}
                      onChange={(_, newValue) => {
                        if (newValue) {
                          handleAircraftChange(index, 'location', {
                            ...aircraft.location,
                            locationType: newValue,
                          });
                        }
                      }}
                      renderInput={(params) => (
                        <TextField {...params} label="Location Type" />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={2}>
                    <TextField
                      fullWidth
                      label="Longitude"
                      type="number"
                      value={aircraft.location.longitude}
                      onChange={(e) =>
                        handleAircraftChange(index, 'location', {
                          ...aircraft.location,
                          longitude: parseFloat(e.target.value) || 0,
                        })
                      }
                    />
                  </Grid>
                  <Grid item xs={12} md={2}>
                    <TextField
                      fullWidth
                      label="Latitude"
                      type="number"
                      value={aircraft.location.latitude}
                      onChange={(e) =>
                        handleAircraftChange(index, 'location', {
                          ...aircraft.location,
                          latitude: parseFloat(e.target.value) || 0,
                        })
                      }
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Time Window Start"
                      type="datetime-local"
                      value={aircraft.timeWindow.start.replace('Z', '').slice(0, 16)}
                      onChange={(e) =>
                        handleAircraftChange(index, 'timeWindow', {
                          ...aircraft.timeWindow,
                          start: new Date(e.target.value).toISOString(),
                        })
                      }
                      InputLabelProps={{ shrink: true }}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Time Window End"
                      type="datetime-local"
                      value={aircraft.timeWindow.end.replace('Z', '').slice(0, 16)}
                      onChange={(e) =>
                        handleAircraftChange(index, 'timeWindow', {
                          ...aircraft.timeWindow,
                          end: new Date(e.target.value).toISOString(),
                        })
                      }
                      InputLabelProps={{ shrink: true }}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Required Tasks
                    </Typography>
                    <Stack spacing={1}>
                      {aircraft.requiredTasks.map((task, taskIndex) => (
                        <Stack key={taskIndex} direction="row" spacing={1}>
                          <Autocomplete
                            freeSolo
                            options={TASK_CODES}
                            value={task.taskCode}
                            onChange={(_, newValue) => {
                              const newTasks = [...aircraft.requiredTasks];
                              newTasks[taskIndex] = {
                                ...newTasks[taskIndex],
                                taskCode: newValue || '',
                              };
                              handleAircraftChange(index, 'requiredTasks', newTasks);
                            }}
                            onInputChange={(_, newValue) => {
                              const newTasks = [...aircraft.requiredTasks];
                              newTasks[taskIndex] = {
                                ...newTasks[taskIndex],
                                taskCode: newValue,
                              };
                              handleAircraftChange(index, 'requiredTasks', newTasks);
                            }}
                            sx={{ flex: 1 }}
                            renderInput={(params) => (
                              <TextField {...params} placeholder="TASK_TIRE_CHECK" />
                            )}
                          />
                          <TextField
                            size="small"
                            label="Min Level"
                            type="number"
                            value={task.minLevel || 1}
                            onChange={(e) => {
                              const newTasks = [...aircraft.requiredTasks];
                              newTasks[taskIndex] = {
                                ...newTasks[taskIndex],
                                minLevel: parseInt(e.target.value) || 1,
                              };
                              handleAircraftChange(index, 'requiredTasks', newTasks);
                            }}
                            sx={{ width: 120 }}
                            inputProps={{ min: 1 }}
                          />
                          <IconButton
                            color="error"
                            onClick={() => handleRemoveAircraftTask(index, taskIndex)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Stack>
                      ))}
                      <Button
                        size="small"
                        startIcon={<AddIcon />}
                        onClick={() => handleAddAircraftTask(index)}
                      >
                        Add Task
                      </Button>
                    </Stack>
                  </Grid>
                </Grid>
              </Paper>
            ))}
            <Button variant="outlined" startIcon={<AddIcon />} onClick={handleAddAircraft}>
              Add Aircraft
            </Button>
          </Stack>
        </AccordionDetails>
      </Accordion>

      {/* Hubs */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">Hubs ({data.hubs.length})</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Stack spacing={2}>
            {data.hubs.map((hub, index) => (
              <Paper key={index} sx={{ p: 2 }}>
                <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                  <Typography variant="subtitle1">Hub #{index + 1}</Typography>
                  <IconButton
                    color="error"
                    size="small"
                    onClick={() => handleRemoveHub(index)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Stack>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Hub ID"
                      value={hub.hubId}
                      onChange={(e) => handleHubChange(index, 'hubId', e.target.value)}
                      placeholder="HUB_01"
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Autocomplete
                      freeSolo
                      options={allLocationIds}
                      value={hub.location.locationId}
                      onChange={(_, newValue) => {
                        handleHubChange(index, 'location', {
                          ...hub.location,
                          locationId: newValue || '',
                        });
                      }}
                      onInputChange={(_, newValue) => {
                        handleHubChange(index, 'location', {
                          ...hub.location,
                          locationId: newValue,
                        });
                      }}
                      renderInput={(params) => (
                        <TextField {...params} label="Location ID" placeholder="REST_AREA_A" />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Autocomplete
                      options={LOCATION_TYPES}
                      value={hub.location.locationType}
                      onChange={(_, newValue) => {
                        if (newValue) {
                          handleHubChange(index, 'location', {
                            ...hub.location,
                            locationType: newValue,
                          });
                        }
                      }}
                      renderInput={(params) => (
                        <TextField {...params} label="Location Type" />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="Longitude"
                      type="number"
                      value={hub.location.longitude}
                      onChange={(e) =>
                        handleHubChange(index, 'location', {
                          ...hub.location,
                          longitude: parseFloat(e.target.value) || 0,
                        })
                      }
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="Latitude"
                      type="number"
                      value={hub.location.latitude}
                      onChange={(e) =>
                        handleHubChange(index, 'location', {
                          ...hub.location,
                          latitude: parseFloat(e.target.value) || 0,
                        })
                      }
                    />
                  </Grid>
                </Grid>
              </Paper>
            ))}
            <Button variant="outlined" startIcon={<AddIcon />} onClick={handleAddHub}>
              Add Hub
            </Button>
          </Stack>
        </AccordionDetails>
      </Accordion>

      {/* Employees */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">Employees ({data.employees.length})</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Stack spacing={2}>
            {data.employees.map((employee, index) => (
              <Paper key={index} sx={{ p: 2 }}>
                <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                  <Typography variant="subtitle1">Employee #{index + 1}</Typography>
                  <IconButton
                    color="error"
                    size="small"
                    onClick={() => handleRemoveEmployee(index)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Stack>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Employee ID"
                      value={employee.employeeId}
                      onChange={(e) => handleEmployeeChange(index, 'employeeId', e.target.value)}
                      placeholder="EMP_001"
                    />
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Autocomplete
                      options={ROLES}
                      value={employee.eType.role}
                      onChange={(_, newValue) => {
                        if (newValue) {
                          handleEmployeeChange(index, 'eType', {
                            ...employee.eType,
                            role: newValue,
                          });
                        }
                      }}
                      renderInput={(params) => (
                        <TextField {...params} label="Role" />
                      )}
                    />
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Break Duration (seconds)"
                      type="number"
                      value={employee.breakDuration || 0}
                      onChange={(e) =>
                        handleEmployeeChange(index, 'breakDuration', parseInt(e.target.value) || 0)
                      }
                      helperText={`${Math.round((employee.breakDuration || 0) / 60)} minutes`}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Working Times
                    </Typography>
                    <Stack spacing={1}>
                      {employee.workingTimes.map((wt, wtIndex) => (
                        <Stack key={wtIndex} direction="row" spacing={1}>
                          <TextField
                            size="small"
                            label="Start"
                            type="datetime-local"
                            value={wt.start.replace('Z', '').slice(0, 16)}
                            onChange={(e) => {
                              const newWorkingTimes = [...employee.workingTimes];
                              newWorkingTimes[wtIndex] = {
                                ...newWorkingTimes[wtIndex],
                                start: new Date(e.target.value).toISOString(),
                              };
                              handleEmployeeChange(index, 'workingTimes', newWorkingTimes);
                            }}
                            InputLabelProps={{ shrink: true }}
                            sx={{ flex: 1 }}
                          />
                          <TextField
                            size="small"
                            label="End"
                            type="datetime-local"
                            value={wt.end.replace('Z', '').slice(0, 16)}
                            onChange={(e) => {
                              const newWorkingTimes = [...employee.workingTimes];
                              newWorkingTimes[wtIndex] = {
                                ...newWorkingTimes[wtIndex],
                                end: new Date(e.target.value).toISOString(),
                              };
                              handleEmployeeChange(index, 'workingTimes', newWorkingTimes);
                            }}
                            InputLabelProps={{ shrink: true }}
                            sx={{ flex: 1 }}
                          />
                          <IconButton
                            color="error"
                            size="small"
                            onClick={() => {
                              const newWorkingTimes = employee.workingTimes.filter(
                                (_, i) => i !== wtIndex
                              );
                              handleEmployeeChange(index, 'workingTimes', newWorkingTimes);
                            }}
                            disabled={employee.workingTimes.length === 1}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Stack>
                      ))}
                      <Button
                        size="small"
                        startIcon={<AddIcon />}
                        onClick={() => {
                          const newWorkingTimes = [
                            ...employee.workingTimes,
                            {
                              start: new Date().toISOString(),
                              end: new Date(Date.now() + 10 * 60 * 60 * 1000).toISOString(),
                            },
                          ];
                          handleEmployeeChange(index, 'workingTimes', newWorkingTimes);
                        }}
                      >
                        Add Working Time
                      </Button>
                    </Stack>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" gutterBottom>
                      Fixed Break Times
                    </Typography>
                    <Stack spacing={1}>
                      {(employee.fixedBreakTimes || []).map((bt, btIndex) => (
                        <Stack key={btIndex} direction="row" spacing={1}>
                          <TextField
                            size="small"
                            label="Start"
                            type="datetime-local"
                            value={bt.start.replace('Z', '').slice(0, 16)}
                            onChange={(e) => {
                              const newBreakTimes = [...(employee.fixedBreakTimes || [])];
                              newBreakTimes[btIndex] = {
                                ...newBreakTimes[btIndex],
                                start: new Date(e.target.value).toISOString(),
                              };
                              handleEmployeeChange(index, 'fixedBreakTimes', newBreakTimes);
                            }}
                            InputLabelProps={{ shrink: true }}
                            sx={{ flex: 1 }}
                          />
                          <TextField
                            size="small"
                            label="End"
                            type="datetime-local"
                            value={bt.end.replace('Z', '').slice(0, 16)}
                            onChange={(e) => {
                              const newBreakTimes = [...(employee.fixedBreakTimes || [])];
                              newBreakTimes[btIndex] = {
                                ...newBreakTimes[btIndex],
                                end: new Date(e.target.value).toISOString(),
                              };
                              handleEmployeeChange(index, 'fixedBreakTimes', newBreakTimes);
                            }}
                            InputLabelProps={{ shrink: true }}
                            sx={{ flex: 1 }}
                          />
                          <IconButton
                            color="error"
                            size="small"
                            onClick={() => {
                              const newBreakTimes = (employee.fixedBreakTimes || []).filter(
                                (_, i) => i !== btIndex
                              );
                              handleEmployeeChange(index, 'fixedBreakTimes', newBreakTimes);
                            }}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Stack>
                      ))}
                      <Button
                        size="small"
                        startIcon={<AddIcon />}
                        onClick={() => {
                          const newBreakTimes = [
                            ...(employee.fixedBreakTimes || []),
                            {
                              start: new Date().toISOString(),
                              end: new Date(Date.now() + 60 * 60 * 1000).toISOString(),
                            },
                          ];
                          handleEmployeeChange(index, 'fixedBreakTimes', newBreakTimes);
                        }}
                      >
                        Add Fixed Break Time
                      </Button>
                    </Stack>
                  </Grid>
                </Grid>
              </Paper>
            ))}
            <Button variant="outlined" startIcon={<AddIcon />} onClick={handleAddEmployee}>
              Add Employee
            </Button>
          </Stack>
        </AccordionDetails>
      </Accordion>

      {/* Distance Matrix */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">
            Distance Matrix ({data.matrixConfigs.distanceMatrix.length})
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Stack spacing={2}>
            {data.matrixConfigs.distanceMatrix.map((entry, index) => (
              <Paper key={index} sx={{ p: 2 }}>
                <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2">Entry #{index + 1}</Typography>
                  <IconButton
                    color="error"
                    size="small"
                    onClick={() => handleRemoveDistanceEntry(index)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Stack>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={4}>
                    <Autocomplete
                      freeSolo
                      options={allLocationIds}
                      value={entry.srcCode}
                      onChange={(_, newValue) => {
                        handleDistanceEntryChange(index, 'srcCode', newValue || '');
                      }}
                      onInputChange={(_, newValue) => {
                        handleDistanceEntryChange(index, 'srcCode', newValue);
                      }}
                      renderInput={(params) => (
                        <TextField {...params} label="Source Code" />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <Autocomplete
                      freeSolo
                      options={allLocationIds}
                      value={entry.destCode}
                      onChange={(_, newValue) => {
                        handleDistanceEntryChange(index, 'destCode', newValue || '');
                      }}
                      onInputChange={(_, newValue) => {
                        handleDistanceEntryChange(index, 'destCode', newValue);
                      }}
                      renderInput={(params) => (
                        <TextField {...params} label="Destination Code" />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="Travel Time (seconds)"
                      type="number"
                      value={entry.travelTime}
                      onChange={(e) =>
                        handleDistanceEntryChange(index, 'travelTime', parseInt(e.target.value) || 0)
                      }
                      helperText={`${Math.round(entry.travelTime / 60)} minutes`}
                    />
                  </Grid>
                </Grid>
              </Paper>
            ))}
            <Button variant="outlined" startIcon={<AddIcon />} onClick={handleAddDistanceEntry}>
              Add Distance Entry
            </Button>
          </Stack>
        </AccordionDetails>
      </Accordion>

      {/* Time Matrix */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6">
            Time Matrix ({data.matrixConfigs.timeMatrix.length})
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Stack spacing={2}>
            {data.matrixConfigs.timeMatrix.map((entry, index) => (
              <Paper key={index} sx={{ p: 2 }}>
                <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2">Entry #{index + 1}</Typography>
                  <IconButton
                    color="error"
                    size="small"
                    onClick={() => handleRemoveTimeEntry(index)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Stack>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={4}>
                    <Autocomplete
                      freeSolo
                      options={TASK_CODES}
                      value={entry.taskCode}
                      onChange={(_, newValue) => {
                        handleTimeEntryChange(index, 'taskCode', newValue || '');
                      }}
                      onInputChange={(_, newValue) => {
                        handleTimeEntryChange(index, 'taskCode', newValue);
                      }}
                      renderInput={(params) => (
                        <TextField {...params} label="Task Code" />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Autocomplete
                      options={ROLES}
                      value={entry.role}
                      onChange={(_, newValue) => {
                        if (newValue) {
                          handleTimeEntryChange(index, 'role', newValue);
                        }
                      }}
                      renderInput={(params) => (
                        <TextField {...params} label="Role" />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={2}>
                    <Autocomplete
                      options={[]} // Level removed from employee model
                      value={entry.level}
                      onChange={(_, newValue) => {
                        if (newValue !== null) {
                          handleTimeEntryChange(index, 'level', newValue);
                        }
                      }}
                      renderInput={(params) => (
                        <TextField {...params} label="Level" />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={3}>
                    <Autocomplete
                      freeSolo
                      options={data.aircrafts.map((ac) => ac.aircraftId)}
                      value={entry.aircraftId || ''}
                      onChange={(_, newValue) => {
                        handleTimeEntryChange(index, 'aircraftId', newValue || '');
                      }}
                      onInputChange={(_, newValue) => {
                        handleTimeEntryChange(index, 'aircraftId', newValue);
                      }}
                      renderInput={(params) => (
                        <TextField {...params} label="Aircraft ID (Optional)" />
                      )}
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Time Process (seconds)"
                      type="number"
                      value={entry.timeProcess}
                      onChange={(e) =>
                        handleTimeEntryChange(index, 'timeProcess', parseInt(e.target.value) || 0)
                      }
                      helperText={`${Math.round(entry.timeProcess / 60)} minutes`}
                    />
                  </Grid>
                </Grid>
              </Paper>
            ))}
            <Button variant="outlined" startIcon={<AddIcon />} onClick={handleAddTimeEntry}>
              Add Time Entry
            </Button>
          </Stack>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
};

export default JsonStructuredEditor;

