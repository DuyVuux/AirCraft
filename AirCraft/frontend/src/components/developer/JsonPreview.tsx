import React from 'react';
import { Box, Paper, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material';
import type { InputData } from '@/types/input';

interface JsonPreviewProps {
  data: InputData | null;
}

const JsonPreview: React.FC<JsonPreviewProps> = ({ data }) => {
  if (!data) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1" color="text.secondary">
          Chưa có dữ liệu để preview. Hãy upload hoặc paste JSON vào editor.
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Preview Data
      </Typography>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          Tracking ID: <strong>{data.trackingId}</strong>
        </Typography>
      </Paper>

      <TableContainer component={Paper} sx={{ mb: 2 }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell><strong>Loại</strong></TableCell>
              <TableCell align="right"><strong>Số lượng</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <TableRow>
              <TableCell>Aircrafts</TableCell>
              <TableCell align="right">{data.aircrafts.length}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell>Hubs</TableCell>
              <TableCell align="right">{data.hubs.length}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell>Employees</TableCell>
              <TableCell align="right">{data.employees.length}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell>Distance Matrix Entries</TableCell>
              <TableCell align="right">{data.matrixConfigs.distanceMatrix.length}</TableCell>
            </TableRow>
            <TableRow>
              <TableCell>Time Matrix Entries</TableCell>
              <TableCell align="right">{data.matrixConfigs.timeMatrix.length}</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </TableContainer>

      <Paper sx={{ p: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          JSON Data:
        </Typography>
        <Box
          component="pre"
          sx={{
            backgroundColor: '#f5f5f5',
            p: 2,
            borderRadius: 1,
            overflow: 'auto',
            maxHeight: 400,
            fontSize: '12px',
            fontFamily: 'monospace',
          }}
        >
          {JSON.stringify(data, null, 2)}
        </Box>
      </Paper>
    </Box>
  );
};

export default JsonPreview;

