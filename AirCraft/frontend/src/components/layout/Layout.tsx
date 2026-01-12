import { ReactNode, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useTheme } from '@/contexts/ThemeContext'
import SharedHeaderActions from '@/components/common/SharedHeaderActions'
import './Layout.css'

interface LayoutProps {
  children: ReactNode
  title?: string
  description?: string
  headerActions?: ReactNode
  showSharedHeader?: boolean
}

function Layout({
  children,
  title = 'Aircraft Scheduler',
  description = '',
  headerActions,
  showSharedHeader = true
}: LayoutProps) {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const location = useLocation()
  const { theme, toggleTheme } = useTheme()

  const menuItems = [
    { text: 'Nhập dữ liệu', icon: 'edit', path: '/' },
    { text: 'Scheduler', icon: 'schedule', path: '/scheduler' },
    { text: 'Lịch sử', icon: 'history', path: '/history' },
    { text: 'Chỉnh sửa bản đồ', icon: 'map', path: '/map-editor' },
  ]

  return (
    <div className="layout-container">
      <aside className={`layout-sidebar ${isCollapsed ? 'collapsed' : ''}`}>
        <div className="layout-sidebar-header" style={{ display: 'flex', alignItems: 'center', justifyContent: isCollapsed ? 'center' : 'space-between' }}>
          {!isCollapsed && <h1 className="layout-sidebar-title">✈️ Aircraft</h1>}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--color-text-secondary)',
              cursor: 'pointer',
              padding: '0.25rem',
              display: 'flex'
            }}
          >
            <span className="material-symbols-outlined">{isCollapsed ? 'menu_open' : 'menu'}</span>
          </button>
        </div>
        <nav className="layout-sidebar-nav">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`layout-sidebar-link ${location.pathname === item.path ||
                (item.path === '/' && location.pathname === '/manual-input')
                ? 'active'
                : ''
                }`}
              title={isCollapsed ? item.text : ''}
            >
              <span className="material-symbols-outlined">{item.icon}</span>
              <span className="layout-sidebar-link-text">{item.text}</span>
            </Link>
          ))}
        </nav>
        <div className="layout-sidebar-footer">
          <button className="theme-toggle" onClick={toggleTheme} title={isCollapsed ? 'Toggle Theme' : ''}>
            <span className="material-symbols-outlined">
              {theme === 'light' ? 'dark_mode' : 'light_mode'}
            </span>
            <span>{theme === 'light' ? 'Dark Mode' : 'Light Mode'}</span>
          </button>
        </div>
      </aside>

      <div className="layout-main">
        <header className="layout-header">
          <div className="layout-header-content">
            <h2 className="layout-header-title">{title}</h2>
            {description && <p className="layout-header-description">{description}</p>}
          </div>
          <div className="layout-header-actions">
            {showSharedHeader && <SharedHeaderActions />}
            {headerActions}
          </div>
        </header>

        <main className="layout-content">
          {children}
        </main>
      </div>
    </div>
  )
}

export default Layout

