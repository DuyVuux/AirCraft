import { Aircraft } from './aircraft';
import { Employee } from './employee';
import { Hub } from './hub';
import { MatrixConfigs } from './matrix';

export interface InputData {
  trackingId: string;
  aircrafts: Aircraft[];
  hubs: Hub[];
  employees: Employee[];
  matrixConfigs: MatrixConfigs;
}

