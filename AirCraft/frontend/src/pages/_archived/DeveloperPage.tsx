import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '@/components/layout/Layout';
import JsonEditor from '@/components/developer/JsonEditor';
import JsonMonacoEditor from '@/components/developer/JsonMonacoEditor';
import JsonPreview from '@/components/developer/JsonPreview';
import type { InputData } from '@/types/input';
import { useDataContext } from '@/contexts/DataContext';
import './DeveloperPage.css';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`developer-tabpanel-${index}`}
      aria-labelledby={`developer-tab-${index}`}
      {...other}
    >
      {value === index && <div className="developer-tabpanel">{children}</div>}
    </div>
  );
}

const DeveloperPage: React.FC = () => {
  const [jsonData, setJsonData] = useState<InputData | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const { setImportedData } = useDataContext();
  const navigate = useNavigate();

  const handleDataChange = (data: InputData | null) => {
    setJsonData(data);
    if (data) {
      // Save to context when data is valid
      setImportedData(data);
    }
  };

  const handleGoToManualInput = () => {
    if (jsonData) {
      navigate('/manual-input');
    }
  };

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const tabs = [
    { label: 'JSON EDITOR (SIMPLE)', id: 'simple' },
    { label: 'JSON EDITOR (MONACO)', id: 'monaco' },
    { label: 'PREVIEW', id: 'preview' },
  ];

  return (
    <Layout
      title="Developer Mode"
      description="Upload file JSON, chỉnh sửa theo cấu trúc, hoặc paste JSON trực tiếp để validate và preview dữ liệu"
    >
      <div className="developer-page">
        <div className="developer-tabs">
          {tabs.map((tab, index) => (
            <button
              key={tab.id}
              className={`developer-tab ${tabValue === index ? 'active' : ''}`}
              onClick={() => handleTabChange(null as any, index)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <TabPanel value={tabValue} index={0}>
          <div className="developer-editor-card">
            <JsonEditor onDataChange={handleDataChange} initialData={jsonData} />
          </div>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <div className="developer-editor-card">
            <JsonMonacoEditor onDataChange={handleDataChange} initialData={jsonData} />
          </div>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <div className="developer-editor-card">
            <JsonPreview data={jsonData} />
            {jsonData && (
              <div>
                <div className="developer-success-alert">
                  Dữ liệu JSON đã được validate và lưu. Nhấn nút bên dưới để chuyển đến Nhập tay.
                </div>
                <button
                  className="developer-action-button"
                  onClick={handleGoToManualInput}
                >
                  Chuyển đến Nhập tay để tiếp tục
                </button>
              </div>
            )}
          </div>
        </TabPanel>
      </div>
    </Layout>
  );
};

export default DeveloperPage;
