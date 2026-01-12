import { Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Toolbar, Box, IconButton, Divider } from '@mui/material'
import { useNavigate, useLocation } from 'react-router-dom'
import EditIcon from '@mui/icons-material/Edit'
import PlayCircleIcon from '@mui/icons-material/PlayCircle'
import HistoryIcon from '@mui/icons-material/History'
import LightModeIcon from '@mui/icons-material/LightMode'
import DarkModeIcon from '@mui/icons-material/DarkMode'
import { useTheme } from '@/contexts/ThemeContext'

const drawerWidth = 240

const menuItems = [
  { text: 'Nhập dữ liệu', icon: <EditIcon />, path: '/' },
  { text: 'Scheduler', icon: <PlayCircleIcon />, path: '/scheduler' },
  { text: 'Lịch sử', icon: <HistoryIcon />, path: '/history' },
]

function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()
  const { theme, toggleTheme } = useTheme()

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          backgroundColor: 'var(--color-surface)',
          borderColor: 'var(--color-border)',
        },
      }}
    >
      <Toolbar />
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <List sx={{ flex: 1 }}>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                selected={location.pathname === item.path ||
                  (item.path === '/' && location.pathname === '/manual-input')}
                onClick={() => navigate(item.path)}
                sx={{
                  '&.Mui-selected': {
                    backgroundColor: 'var(--color-primary)',
                    color: 'white',
                    '&:hover': {
                      backgroundColor: 'var(--color-primary-dark)',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'white',
                    },
                  },
                  '&:hover': {
                    backgroundColor: 'var(--color-surface-hover)',
                  },
                }}
              >
                <ListItemIcon sx={{ color: 'var(--color-text-secondary)' }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  sx={{ color: 'var(--color-text-primary)' }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>

        <Divider sx={{ borderColor: 'var(--color-border)' }} />

        <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{
            fontSize: '0.75rem',
            color: 'var(--color-text-secondary)',
            textTransform: 'uppercase',
            letterSpacing: '0.05em'
          }}>
            {theme === 'light' ? 'Light Mode' : 'Dark Mode'}
          </span>
          <IconButton
            onClick={toggleTheme}
            size="small"
            sx={{
              color: 'var(--color-text-secondary)',
              '&:hover': {
                backgroundColor: 'var(--color-surface-hover)',
                color: 'var(--color-primary)'
              }
            }}
          >
            {theme === 'light' ? <DarkModeIcon /> : <LightModeIcon />}
          </IconButton>
        </Box>
      </Box>
    </Drawer>
  )
}

export default Sidebar
