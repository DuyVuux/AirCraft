import TaskTab, { tabConfig as taskConfig } from './TaskTab';
import EmployeeTab, { tabConfig as employeeConfig } from './EmployeeTab';
// import HubTab, { tabConfig as hubConfig } from './HubTab'; // Disabled: Hubs are fixed per airport
import AircraftTab, { tabConfig as aircraftConfig } from './AircraftTab';
// import TimeMatrixTab, { tabConfig as timeMatrixConfig } from './TimeMatrixTab'; // Disabled: Will be handled in Tasks tab
// import MapTab, { tabConfig as mapConfig } from './MapTab'; // Moved to sidebar as separate page
// import SchedulerTab, { tabConfig as schedulerConfig } from './SchedulerTab'; // Moved to sidebar as separate page

export const TAB_REGISTRY = [
    { ...taskConfig, Component: TaskTab },
    { ...employeeConfig, Component: EmployeeTab },
    // { ...hubConfig, Component: HubTab }, // Disabled
    { ...aircraftConfig, Component: AircraftTab },
    // { ...timeMatrixConfig, Component: TimeMatrixTab }, // Disabled
    // { ...schedulerConfig, Component: SchedulerTab }, // Moved to sidebar
    // { ...mapConfig, Component: MapTab }, // Moved to sidebar
].sort((a, b) => a.order - b.order);

export type { TabProps, TabConfig } from './types';
