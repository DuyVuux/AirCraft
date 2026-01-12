import React, { useState, useRef } from 'react';
import { validateJSON } from '@/utils/jsonValidator';
import type { InputData } from '@/types/input';
import './JsonEditor.css';

interface JsonEditorProps {
  onDataChange?: (data: InputData | null) => void;
  initialData?: InputData | null;
}

const JsonEditor: React.FC<JsonEditorProps> = ({ onDataChange, initialData }) => {
  const [jsonText, setJsonText] = useState<string>(
    initialData ? JSON.stringify(initialData, null, 2) : ''
  );
  const [errors, setErrors] = useState<string[]>([]);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [isValid, setIsValid] = useState<boolean>(false);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleTextChange = (value: string) => {
    setJsonText(value);
    setErrors([]);
    setWarnings([]);
    setIsValid(false);
  };

  const handleValidate = () => {
    if (!jsonText.trim()) {
      setErrors(['JSON không được để trống']);
      setWarnings([]);
      setIsValid(false);
      return;
    }

    try {
      const parsed = JSON.parse(jsonText);
      const result = validateJSON(jsonText);
      setIsValid(result.valid);
      
      if (result.valid) {
        // JSON hợp lệ - chỉ hiển thị success message
        setErrors([]);
        setWarnings(['✅ JSON hợp lệ - đã trích xuất được các biến tương ứng.']);
        onDataChange?.(parsed as InputData);
      } else {
        // JSON có lỗi - hiển thị error messages
        const errorMessages = result.errors.map((e) => `${e.field}: ${e.message}`);
        setErrors(errorMessages);
        setWarnings(['⚠️ Một số trường có thể thiếu hoặc không đúng format, nhưng validator sẽ cố gắng trích xuất các biến tương ứng.']);
        
        // Vẫn cố gắng trích xuất dữ liệu nếu có thể
        if (parsed.aircrafts || parsed.employees || parsed.hubs || parsed.facilities) {
          onDataChange?.(parsed as InputData);
        } else {
          onDataChange?.(null);
        }
      }
    } catch (error) {
      setErrors([`Parse error: ${(error as Error).message}`]);
      setWarnings([]);
      setIsValid(false);
      onDataChange?.(null);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.json')) {
      setErrors(['File phải có định dạng .json']);
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        setJsonText(content);
        setErrors([]);
        setWarnings([]);
        setIsValid(false);
        // Auto validate after upload
        setTimeout(() => {
          try {
            const parsed = JSON.parse(content);
            const result = validateJSON(content);
            setIsValid(result.valid);
            
            if (result.valid) {
              setErrors([]);
              setWarnings(['✅ JSON hợp lệ - đã trích xuất được các biến.']);
              onDataChange?.(parsed as InputData);
            } else {
              const errorMessages = result.errors.map((e) => `${e.field}: ${e.message}`);
              setErrors(errorMessages);
              setWarnings(['⚠️ Một số trường có thể thiếu hoặc không đúng format, nhưng validator sẽ cố gắng trích xuất các biến tương ứng.']);
              if (parsed.aircrafts || parsed.employees || parsed.hubs) {
                onDataChange?.(parsed as InputData);
              }
            }
          } catch (e) {
            setErrors([`Lỗi parse: ${(e as Error).message}`]);
            setWarnings([]);
          }
        }, 100);
      } catch (error) {
        setErrors([`Lỗi đọc file: ${(error as Error).message}`]);
      }
    };
    reader.onerror = () => {
      setErrors(['Lỗi khi đọc file']);
      setWarnings([]);
    };
    reader.readAsText(file);
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
    const file = event.dataTransfer.files[0];
    if (!file) return;

    if (!file.name.endsWith('.json')) {
      setErrors(['File phải có định dạng .json']);
      setWarnings([]);
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        setJsonText(content);
        setErrors([]);
        setWarnings([]);
        setIsValid(false);
        // Auto validate after drop
        setTimeout(() => {
          try {
            const parsed = JSON.parse(content);
            const result = validateJSON(content);
            setIsValid(result.valid);
            
            if (result.valid) {
              setErrors([]);
              setWarnings(['✅ JSON hợp lệ - đã trích xuất được các biến.']);
              onDataChange?.(parsed as InputData);
            } else {
              const errorMessages = result.errors.map((e) => `${e.field}: ${e.message}`);
              setErrors(errorMessages);
              setWarnings(['⚠️ Một số trường có thể thiếu hoặc không đúng format, nhưng validator sẽ cố gắng trích xuất các biến tương ứng.']);
              if (parsed.aircrafts || parsed.employees || parsed.hubs) {
                onDataChange?.(parsed as InputData);
              }
            }
          } catch (e) {
            setErrors([`Lỗi parse: ${(e as Error).message}`]);
            setWarnings([]);
          }
        }, 100);
      } catch (error) {
        setErrors([`Lỗi đọc file: ${(error as Error).message}`]);
      }
    };
    reader.readAsText(file);
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(jsonText);
  };

  const handleDownload = () => {
    if (!jsonText.trim()) return;

    const blob = new Blob([jsonText], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'input_data.json';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleClear = () => {
    setJsonText('');
    setErrors([]);
    setWarnings([]);
    setIsValid(false);
    onDataChange?.(null);
  };

  const handleLoadSample = () => {
    const sample: InputData = {
      trackingId: 'PLAN-2024-12-05-001',
      aircrafts: [
        {
          aircraftId: 'VN-A320',
          aType: { id: 'A320', desc: 'Airbus A320' },
          location: {
            locationId: 'GATE-01',
            locationType: 'GATE',
            longitude: 105.8067,
            latitude: 21.2144,
          },
          timeWindow: {
            start: '2024-12-05T08:00:00Z',
            end: '2024-12-05T12:00:00Z',
          },
          requiredTasks: [{ taskCode: 'TASK_TIRE_CHECK' }],
        },
      ],
      hubs: [
        {
          hubId: 'HUB_01',
          location: {
            locationId: 'REST_AREA_A',
            locationType: 'HUB',
            longitude: 106.6650,
            latitude: 10.8200,
          },
        },
      ],
      employees: [
        {
          employeeId: 'EMP_001',
          eType: { role: 'MECHANIC', level: 1 },
          workingTimes: [
            {
              start: '2024-12-05T07:00:00Z',
              end: '2024-12-05T17:00:00Z',
            },
          ],
          breakTimes: [{ start: '12:00', end: '13:00' }],
        },
      ],
      matrixConfigs: {
        distanceMatrix: [
          { srcCode: 'GATE-01', destCode: 'REST_AREA_A', travelTime: 600 },
        ],
        timeMatrix: [
          {
            taskCode: 'TASK_TIRE_CHECK',
            role: 'MECHANIC',
            level: 1,
            timeProcess: 1800,
          },
        ],
      },
    };
    const sampleText = JSON.stringify(sample, null, 2);
    setJsonText(sampleText);
    setErrors([]);
    setWarnings([]);
    setIsValid(true);
    onDataChange?.(sample);
  };

  return (
    <div>
      <div
        className={`json-editor-container ${isDragging ? 'dragging' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <div className="json-editor-header">
          <h3 className="json-editor-title">JSON Editor</h3>
          <div className="json-editor-actions">
            <input
              ref={fileInputRef}
              type="file"
              accept=".json"
              style={{ display: 'none' }}
              onChange={handleFileUpload}
            />
            <button
              className="json-editor-button json-editor-button-primary"
              onClick={() => fileInputRef.current?.click()}
              type="button"
            >
              <span className="material-symbols-outlined">upload_file</span>
              UPLOAD FILE
            </button>
            <button
              className="json-editor-button"
              onClick={handleLoadSample}
              type="button"
            >
              LOAD SAMPLE
            </button>
            <button
              className="json-editor-icon-button"
              onClick={handleCopy}
              disabled={!jsonText.trim()}
              type="button"
              title="Copy to clipboard"
            >
              <span className="material-symbols-outlined">content_copy</span>
            </button>
            <button
              className="json-editor-icon-button"
              onClick={handleDownload}
              disabled={!jsonText.trim()}
              type="button"
              title="Download JSON"
            >
              <span className="material-symbols-outlined">download</span>
            </button>
            <button
              className="json-editor-icon-button"
              onClick={handleClear}
              disabled={!jsonText.trim()}
              type="button"
              title="Clear"
            >
              <span className="material-symbols-outlined">close</span>
            </button>
          </div>
        </div>

        <p className="json-editor-hint">
          Kéo thả file JSON vào đây hoặc click "Upload File" để chọn file
        </p>

        <textarea
          className="json-editor-textarea"
          value={jsonText}
          onChange={(e) => handleTextChange(e.target.value)}
          placeholder="Paste JSON vào đây hoặc upload file..."
          rows={20}
        />
      </div>

      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '1rem' }}>
        <button
          className="json-editor-validate-button"
          onClick={handleValidate}
          type="button"
        >
          VALIDATE JSON
        </button>
        {isValid && (
          <div className="json-editor-alert json-editor-alert-success">
            ✅ JSON hợp lệ!
          </div>
        )}
      </div>

      {warnings.length > 0 && (
        <div className={`json-editor-alert ${isValid ? 'json-editor-alert-success' : 'json-editor-alert-warning'}`}>
          <ul>
            {warnings.map((warning, index) => (
              <li key={index}>{warning}</li>
            ))}
          </ul>
        </div>
      )}

      {errors.length > 0 && (
        <div className="json-editor-alert json-editor-alert-error">
          <div style={{ fontWeight: 600, marginBottom: '0.5rem' }}>Lỗi validation:</div>
          <ul>
            {errors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default JsonEditor;

