import React from 'react';
import { AppBar, Toolbar, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const Header: React.FC = () => {
  const navigate = useNavigate();

  return (
    <AppBar 
      position="static"
      sx={{ 
        overflow: 'visible',
        '& .MuiToolbar-root': {
          overflow: 'visible',
        }
      }}
    >
      <Toolbar 
        sx={{ 
          minHeight: '64px !important', 
          paddingX: { xs: 1, sm: 2, md: 3 },
          overflow: 'visible',
          width: '100%',
        }}
      >
        <Typography
          variant="h6"
          component="div"
          sx={{ 
            flexGrow: 1, 
            cursor: 'pointer',
            whiteSpace: 'nowrap',
            overflow: 'visible !important',
            textOverflow: 'clip',
            minWidth: 0,
            fontSize: { xs: '0.875rem', sm: '1.125rem', md: '1.25rem' },
            fontWeight: 700,
            display: 'block',
            width: 'auto',
            maxWidth: '100%',
            marginLeft: '10cm',
          }}
          onClick={() => navigate('/home')}
        >
          Aircraft Web - Data Input System
        </Typography>
      </Toolbar>
    </AppBar>
  );
};

export default Header;

