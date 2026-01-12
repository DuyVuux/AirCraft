import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './ProductPage.css';

// Dữ liệu cho hero banners - tất cả căn trái với màu chữ nổi bật
const heroBanners = [
  {
    image: '/image/hero_banner/Hero_1.png',
    title: 'Fill Ground Crew Shifts Faster and Reduce Costs',
    description: 'Manage crew schedules efficiently with our powerful ground crew shift management software.',
    textAlign: 'left',
    titleColor: '#ffffff', // White - nổi bật hơn
    descriptionColor: '#ffffff', // White - nổi bật hơn
    textPosition: 'left',
  },
  {
    image: '/image/hero_banner/Hero_2.png',
    title: 'Never Get Caught Short-Staffed Again',
    description: 'Cover shifts 87% faster! Centralize scheduling information and eliminate paper forms to boost efficiency.',
    textAlign: 'left',
    titleColor: '#ffffff', // White
    descriptionColor: '#ffffff', // White
    textPosition: 'left',
  },
  {
    image: '/image/hero_banner/Hero_3.png',
    title: 'Automate Scheduling Operations',
    description: 'Save valuable time and reduce administration costs by up to 40% with automated shift management.',
    textAlign: 'left',
    titleColor: '#ffffff', // White - nổi bật hơn
    descriptionColor: '#ffffff', // White - nổi bật hơn
    textPosition: 'left',
  },
  {
    image: '/image/hero_banner/Hero_4.png',
    title: 'Increase Employee Satisfaction',
    description: 'Enable convenient automated shift bidding, swapping, and PTO management for better retention.',
    textAlign: 'left',
    titleColor: '#ffffff', // White
    descriptionColor: '#ffffff', // White
    textPosition: 'left',
  },
];

const ProductPage: React.FC = () => {
  const navigate = useNavigate();
  const [currentSlide, setCurrentSlide] = useState(0);

  const handleManageCrewSchedules = () => {
    navigate('/home');
  };

  // Tự động chuyển slide mỗi 5 giây
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % heroBanners.length);
    }, 5000);

    return () => clearInterval(interval);
  }, []); // Chỉ chạy một lần khi component mount

  // Điều hướng slide
  const goToSlide = (index: number) => {
    setCurrentSlide(index);
  };

  const goToPrevious = () => {
    setCurrentSlide((prev) => (prev - 1 + heroBanners.length) % heroBanners.length);
  };

  const goToNext = () => {
    setCurrentSlide((prev) => (prev + 1) % heroBanners.length);
  };

  // Ảnh cho 4 khung tròn
  const productImages = [
    '/image/product_page/Pic1.png',
    '/image/product_page/Pic2.jpg',
    '/image/product_page/Píc3.jpg',
    '/image/product_page/Pic4.jpg',
  ];

  return (
    <div className="product-page">
      {/* Header */}
      <header className="product-header">
        <div className="product-container">
          <nav className="product-nav">
            <div className="product-logo">
              <span className="material-symbols-outlined product-logo-icon">flight_takeoff</span>
              <span className="product-logo-text">AeroSchedule</span>
            </div>
            <div className="product-nav-links">
              <a href="#features" className="product-nav-link">Features</a>
              <a href="#benefits" className="product-nav-link">Benefits</a>
              <a href="#integrations" className="product-nav-link">Integrations</a>
              <a href="#pricing" className="product-nav-link">Pricing</a>
            </div>
            <div className="product-nav-actions">
              <a href="#login" className="product-nav-link product-nav-link-hidden">Log In</a>
              <button className="product-btn-primary product-btn-demo">Request a Demo</button>
            </div>
          </nav>
        </div>
      </header>

      {/* Hero Section - Slideshow */}
      <main className="product-main">
        <div className="product-hero-slideshow">
          {heroBanners.map((banner, index) => (
            <div
              key={index}
              className={`product-hero-slide ${index === currentSlide ? 'active' : ''}`}
            >
              <div className="product-hero-background">
                <img 
                  alt={banner.title}
                  className="product-hero-image"
                  src={banner.image}
                />
                <div className="product-hero-overlay"></div>
                <div className="product-hero-gradient"></div>
              </div>
              <div className="product-hero-content">
                <div className="product-container">
                  <div className={`product-hero-grid product-hero-grid-${banner.textPosition}`}>
                    <div className={`product-hero-text product-hero-text-${banner.textPosition}`}>
                      <h1 
                        className="product-hero-title"
                        style={{ 
                          color: banner.titleColor,
                          textAlign: banner.textAlign as 'left' | 'center' | 'right'
                        }}
                      >
                        {banner.title}
                      </h1>
                      <p 
                        className="product-hero-description"
                        style={{ 
                          color: banner.descriptionColor,
                          textAlign: banner.textAlign as 'left' | 'center' | 'right'
                        }}
                      >
                        {banner.description}
                      </p>
                      <div 
                        className={`product-hero-actions product-hero-actions-${banner.textPosition}`}
                        style={{ 
                          justifyContent: banner.textAlign === 'center' ? 'center' : 
                          banner.textAlign === 'right' ? 'flex-end' : 'flex-start'
                        }}
                      >
                        <button 
                          className="product-btn-primary product-btn-large"
                          onClick={handleManageCrewSchedules}
                        >
                          Manage Crew Schedules <span className="material-symbols-outlined">arrow_forward</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {/* Navigation Buttons */}
          <button 
            className="product-hero-nav product-hero-nav-prev"
            onClick={goToPrevious}
            aria-label="Previous slide"
          >
            <span className="material-symbols-outlined">chevron_left</span>
          </button>
          <button 
            className="product-hero-nav product-hero-nav-next"
            onClick={goToNext}
            aria-label="Next slide"
          >
            <span className="material-symbols-outlined">chevron_right</span>
          </button>

          {/* Dots Indicator */}
          <div className="product-hero-dots">
            {heroBanners.map((_, index) => (
              <button
                key={index}
                className={`product-hero-dot ${index === currentSlide ? 'active' : ''}`}
                onClick={() => goToSlide(index)}
                aria-label={`Go to slide ${index + 1}`}
              />
            ))}
          </div>
        </div>
      </main>

      {/* Features Section */}
      <section className="product-section product-section-centered" id="features">
        <div className="product-container">
          <div className="product-section-content-centered">
            <h2 className="product-section-title product-section-title-center">Never Get Caught Short-Staffed Again</h2>
            <p className="product-section-description product-section-description-center">
              Cover shifts 87% faster! AeroSchedule ground crew shift management software allows you to centralize scheduling information. It also eliminates the need for paper forms and processes, freeing your front-line workforce to focus on their primary goal of delivering an exceptional customer experience. It also gives employees agency in their own scheduling process, boosting job satisfaction and retention.
            </p>
          </div>
        </div>
      </section>

      <section className="product-section product-section-alt">
        <div className="product-container">
          <div className="product-section-grid product-section-grid-reverse">
            <div className="product-section-text">
              <h2 className="product-section-title">Automating Scheduling Operations Saves on Administrative Costs</h2>
              <p className="product-section-description">
                By automating and centralizing scheduling operations, you can instantly create shift bids, process shift swaps, assign overtime, and electronically approve or deny requests without paper, spreadsheets, or fax machines. As a result, you save valuable time and reduce administration costs by up to 40%.
              </p>
            </div>
            <div className="product-section-visual">
              <div className="product-circle product-circle-outer">
                <img 
                  src={productImages[1]} 
                  alt="Automating Scheduling Operations"
                  className="product-circle-image"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="product-section">
        <div className="product-container">
          <div className="product-section-grid">
            <div className="product-section-text">
              <h2 className="product-section-title">Raise Efficiency and Passenger Satisfaction</h2>
              <p className="product-section-description">
                In addition to delivering operational efficiency gains and reducing turnover, our crew management software can save airlines thousands of dollars by reducing canceled flights due to inferior scheduling. It can also help avoid paycheck overpayments because of shifts being incorrectly logged.
              </p>
            </div>
            <div className="product-section-visual">
              <div className="product-circle product-circle-outer">
                <img 
                  src={productImages[2]} 
                  alt="Raise Efficiency and Passenger Satisfaction"
                  className="product-circle-image"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="product-section product-section-alt">
        <div className="product-container">
          <div className="product-section-grid product-section-grid-reverse">
            <div className="product-section-text">
              <h2 className="product-section-title">Increase Employee Retention and Satisfaction</h2>
              <p className="product-section-description">
                AeroSchedule increases employee satisfaction and retention by enabling convenient automated shift and vacation bidding, swapping, and PTO management. The crew management software is intuitive and user-friendly for both supervisors and employees. AeroSchedule adheres to company and union policies, helping you to avoid grievances and any slowdown in service.
              </p>
            </div>
            <div className="product-section-visual">
              <div className="product-circle product-circle-outer">
                <img 
                  src={productImages[3]} 
                  alt="Increase Employee Retention and Satisfaction"
                  className="product-circle-image"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features List Section */}
      <section className="product-section">
        <div className="product-container">
          <div className="product-section-header">
            <h2 className="product-section-title product-section-title-center">
              Features That Allow You to Do More, More Efficiently
            </h2>
          </div>
          <div className="product-features-grid">
            <ul className="product-features-list">
              <li className="product-feature-item">
                <span className="material-symbols-outlined product-feature-icon">check_circle</span>
                Automate shift and vacation bidding.
              </li>
              <li className="product-feature-item">
                <span className="material-symbols-outlined product-feature-icon">check_circle</span>
                Built-in tracking makes for dependable metrics and reports.
              </li>
              <li className="product-feature-item">
                <span className="material-symbols-outlined product-feature-icon">check_circle</span>
                Flexible software to accommodates changing rules and union requirements.
              </li>
              <li className="product-feature-item">
                <span className="material-symbols-outlined product-feature-icon">check_circle</span>
                Works on employee self-service model.
              </li>
            </ul>
            <ul className="product-features-list">
              <li className="product-feature-item">
                <span className="material-symbols-outlined product-feature-icon">check_circle</span>
                All scheduling information is centrally located in one place.
              </li>
              <li className="product-feature-item">
                <span className="material-symbols-outlined product-feature-icon">check_circle</span>
                Rules are configurable for each work group or by individual.
              </li>
              <li className="product-feature-item">
                <span className="material-symbols-outlined product-feature-icon">check_circle</span>
                Trace attendance incidents and work history to reduce grievance payouts.
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* Configuration Section */}
      <section className="product-section product-section-alt">
        <div className="product-container">
          <div className="product-section-header">
            <h2 className="product-section-title product-section-title-center">
              Configured to the Way Your Ground Crews Work
            </h2>
          </div>
          <div className="product-config-grid">
            <div className="product-config-item">
              <div className="product-config-icon-wrapper">
                <div className="product-config-icon-bg">
                  <span className="material-symbols-outlined product-config-icon">checklist</span>
                </div>
              </div>
              <h3 className="product-config-title">Adheres to Labor Union Rules</h3>
              <p className="product-config-description">
                AeroSchedule is configurable to your specific labor union rules.
              </p>
            </div>
            <div className="product-config-item">
              <div className="product-config-icon-wrapper">
                <div className="product-config-icon-bg">
                  <span className="material-symbols-outlined product-config-icon">sync</span>
                </div>
              </div>
              <h3 className="product-config-title">Plays Well With Your System</h3>
              <p className="product-config-description">
                Powerful integration capabilities maximize existing investments and use of any Time & Attendance or Human Resources Information Systems.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Knowledge Section */}
      <section className="product-section">
        <div className="product-container">
          <div className="product-section-header">
            <h2 className="product-section-title product-section-title-center">Knowledge is Power</h2>
            <p className="product-section-subtitle">
              Learn how AeroSchedule can help your organization solve complex problems.
            </p>
          </div>
          <div className="product-knowledge-grid">
            <div className="product-knowledge-card">
              <div className="product-knowledge-card-image"></div>
              <h3 className="product-knowledge-card-title">How to Conduct Your Manpower Planning</h3>
              <a href="#" className="product-knowledge-card-link">
                Discover Efficiencies <span className="material-symbols-outlined">arrow_forward</span>
              </a>
            </div>
            <div className="product-knowledge-card">
              <div className="product-knowledge-card-image"></div>
              <h3 className="product-knowledge-card-title">Powerful integrations through the AeroSchedule API</h3>
              <a href="#" className="product-knowledge-card-link">
                Learn about the API <span className="material-symbols-outlined">arrow_forward</span>
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="product-footer">
        <div className="product-container">
          <div className="product-footer-grid">
            <div className="product-footer-brand">
              <div className="product-logo">
                <span className="material-symbols-outlined product-logo-icon">flight_takeoff</span>
                <span className="product-logo-text">AeroSchedule</span>
              </div>
              <p className="product-footer-description">Optimizing aviation workforces worldwide.</p>
            </div>
            <div className="product-footer-column">
              <h5 className="product-footer-heading">Products</h5>
              <ul className="product-footer-list">
                <li><a href="#" className="product-footer-link">AeroSchedule</a></li>
                <li><a href="#" className="product-footer-link">ShiftBidding</a></li>
                <li><a href="#" className="product-footer-link">Time & Attendance</a></li>
                <li><a href="#" className="product-footer-link">Integrations</a></li>
              </ul>
            </div>
            <div className="product-footer-column">
              <h5 className="product-footer-heading">Company</h5>
              <ul className="product-footer-list">
                <li><a href="#" className="product-footer-link">About Us</a></li>
                <li><a href="#" className="product-footer-link">Contact Us</a></li>
                <li><a href="#" className="product-footer-link">News</a></li>
                <li><a href="#" className="product-footer-link">Blog</a></li>
              </ul>
            </div>
            <div className="product-footer-column">
              <h5 className="product-footer-heading">Industries</h5>
              <ul className="product-footer-list">
                <li><a href="#" className="product-footer-link">Airlines</a></li>
                <li><a href="#" className="product-footer-link">Ground Handling</a></li>
                <li><a href="#" className="product-footer-link">Airports</a></li>
              </ul>
            </div>
            <div className="product-footer-column">
              <h5 className="product-footer-heading">Support</h5>
              <ul className="product-footer-list">
                <li><a href="#" className="product-footer-link">Contact Support</a></li>
                <li><a href="#" className="product-footer-link">Knowledge Base</a></li>
                <li><a href="#" className="product-footer-link">Accessibility</a></li>
              </ul>
            </div>
          </div>
          <div className="product-footer-bottom">
            <p>© 2024 AeroSchedule Inc. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default ProductPage;

