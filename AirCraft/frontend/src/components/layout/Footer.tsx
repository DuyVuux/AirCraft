import React from 'react';
import { Box, Typography } from '@mui/material';

const Footer: React.FC = () => {
  return (
    <Box
      component="footer"
      sx={{
        py: 2,
        px: 3,
        backgroundColor: '#1976d2',
        color: 'white',
        textAlign: 'center',
      }}
    >
      <Typography variant="body2">
        Aircraft Web - Data Input System v1.0.0
      </Typography>
    </Box>
  );
};

export default Footer;

