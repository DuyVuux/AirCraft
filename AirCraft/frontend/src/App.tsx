import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ThemeProvider as MuiThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import ManualInputPage from './pages/ManualInputPage'
import HistoryPage from './pages/HistoryPage'
// import DeveloperPage from './pages/DeveloperPage' // Disabled
import SchedulerPage from './pages/SchedulerPage'
import MapEditorPage from './pages/MapEditorPage'
import { DataProvider } from './contexts/DataContext'
import { GlobalDataProvider } from './contexts/GlobalDataContext'
import { HistoryProvider } from './contexts/HistoryContext'
import { ThemeProvider, useTheme } from './contexts/ThemeContext'
import { NotificationProvider } from './contexts/NotificationContext'
import NotificationContainer from './components/common/NotificationContainer'
import './styles/theme.css'

function AppContent() {
  const { theme } = useTheme()

  const muiTheme = createTheme({
    palette: {
      mode: theme,
      primary: {
        main: '#0EA5E9',
      },
      success: {
        main: '#10B981',
      },
      warning: {
        main: '#F59E0B',
      },
      error: {
        main: '#EF4444',
      },
      background: {
        default: theme === 'light' ? '#F8FAFC' : '#0F172A',
        paper: theme === 'light' ? '#FFFFFF' : '#1E293B',
      },
    },
  })

  return (
    <MuiThemeProvider theme={muiTheme}>
      <CssBaseline />
      <NotificationProvider>
        <DataProvider>
          <GlobalDataProvider>
            <HistoryProvider>
              <BrowserRouter>
                <Routes>
                  <Route path="/" element={<ManualInputPage />} />
                  <Route path="/manual-input" element={<ManualInputPage />} />
                  <Route path="/history" element={<HistoryPage />} />
                  <Route path="/scheduler" element={<SchedulerPage />} />
                  <Route path="/map-editor" element={<MapEditorPage />} />
                  {/* <Route path="/developer" element={<DeveloperPage />} /> */}
                </Routes>
                <NotificationContainer />
              </BrowserRouter>
            </HistoryProvider>
          </GlobalDataProvider>
        </DataProvider>
      </NotificationProvider>
    </MuiThemeProvider>
  )
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  )
}

export default App
