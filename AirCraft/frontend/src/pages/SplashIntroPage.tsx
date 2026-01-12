import { useNavigate } from 'react-router-dom';
import './SplashIntroPage.css';

// Chỉ sử dụng 1 ảnh cố định
const BACKGROUND_IMAGE = '/image/workforce_splash_intro/Flight (2).png';

const SplashIntroPage: React.FC = () => {
  const navigate = useNavigate();

  const handleEnterSite = () => {
    navigate('/product');
  };

  return (
    <div className="splash-intro-container">
      {/* Background image cố định */}
      <div
        className="slideshow-background"
        style={{
          backgroundImage: `url("${BACKGROUND_IMAGE}")`,
        }}
      >
        {/* Overlay để làm tối background */}
        <div className="slideshow-overlay" />
      </div>

      {/* Content */}
      <div className="splash-content">
        <h1 className="splash-heading">
          Modern Workforce Scheduling for Aviation & Operations
        </h1>
        <p className="splash-tagline">Smart. Automated. Reliable.</p>
        <button
          className="splash-button"
          onClick={handleEnterSite}
          type="button"
        >
          Enter Site
        </button>
      </div>
    </div>
  );
};

export default SplashIntroPage;

