import React from 'react';
import { useNavigate } from 'react-router-dom';
import UploadIcon from '@mui/icons-material/Upload';
import EditIcon from '@mui/icons-material/Edit';
import CodeIcon from '@mui/icons-material/Code';
import './HomePage.css';

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  const features = [
    {
      title: 'Upload File',
      description: 'Upload CSV/Excel files để nhập dữ liệu nhanh chóng',
      icon: <UploadIcon />,
      path: '/upload',
      color: '#1976d2',
    },
    {
      title: 'Nhập tay',
      description: 'Nhập và chỉnh sửa dữ liệu trực tiếp trên web',
      icon: <EditIcon />,
      path: '/manual-input',
      color: '#4caf50',
    },
    {
      title: 'Developer Mode',
      description: 'Nhập JSON trực tiếp để test và phát triển',
      icon: <CodeIcon />,
      path: '/developer',
      color: '#ff9800',
    },
  ];

  return (
    <div className="home-page">
      <div className="home-container">
        {/* Welcome Section */}
        <section className="home-welcome">
          <h1 className="home-title">
            Chào mừng đến với Aircraft Web
          </h1>
          <p className="home-subtitle">
            Hệ thống nhập và quản lý dữ liệu cho Airport Ground Staff Scheduling
          </p>
        </section>

        {/* Features Cards Section */}
        <section className="home-features">
          <div className="home-features-grid">
            {features.map((feature) => (
              <div key={feature.title} className="home-feature-card">
                <div className="home-feature-icon" style={{ color: feature.color }}>
                  {feature.icon}
                </div>
                <h2 className="home-feature-title">{feature.title}</h2>
                <p className="home-feature-description">{feature.description}</p>
                <button
                  className="home-feature-button"
                  style={{ 
                    background: `linear-gradient(135deg, ${feature.color} 0%, ${getDarkerColor(feature.color)} 100%)`,
                  }}
                  onClick={() => navigate(feature.path)}
                >
                  Bắt đầu
                </button>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};

// Helper function to get darker shade of color
const getDarkerColor = (color: string): string => {
  const colorMap: { [key: string]: string } = {
    '#1976d2': '#1565c0',
    '#4caf50': '#388e3c',
    '#ff9800': '#f57c00',
  };
  return colorMap[color] || color;
};

export default HomePage;
