import React, { useRef, useState } from 'react';
import { parseCSV } from '@/utils/csvParser';
import { parseExcel } from '@/utils/excelParser';
import './FileUpload.css';

interface FileUploadProps<T> {
  title: string;
  description: string;
  templateFileName: string;
  headers: string[];
  onUpload: (data: T[], errors: string[]) => void;
  acceptedFormats?: string[];
}

function FileUpload<T extends Record<string, any>>({
  title,
  description,
  templateFileName,
  headers,
  onUpload,
  acceptedFormats = ['.csv', '.xlsx', '.xls'],
}: FileUploadProps<T>) {
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setIsProcessing(true);
    setErrors([]);

    try {
      const fileExtension = file.name.split('.').pop()?.toLowerCase();
      let result;

      if (fileExtension === 'csv') {
        result = await parseCSV<T>(file, headers);
      } else if (fileExtension === 'xlsx' || fileExtension === 'xls') {
        result = await parseExcel<T>(file, headers);
      } else {
        setErrors(['Định dạng file không được hỗ trợ. Vui lòng sử dụng CSV hoặc Excel.']);
        setIsProcessing(false);
        return;
      }

      if (result.errors.length > 0) {
        setErrors(result.errors);
      }

      onUpload(result.data, result.errors);
    } catch (error) {
      setErrors([`Lỗi xử lý file: ${(error as Error).message}`]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFile(file);
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);

    const file = event.dataTransfer.files[0];
    if (file) {
      handleFile(file);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDownloadTemplate = () => {
    // Template files should be in public/templates/
    const link = document.createElement('a');
    link.href = `/templates/${templateFileName}`;
    link.download = templateFileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div>
      <div
        className={`file-upload-container ${isDragging ? 'dragging' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="file-upload-icon">
          <span className="material-symbols-outlined" style={{ fontSize: '3rem' }}>upload_file</span>
        </div>
        <h3 className="file-upload-title">{title}</h3>
        <p className="file-upload-description">{description}</p>
        <p className="file-upload-hint">Kéo thả file vào đây hoặc click để chọn file</p>
        <p className="file-upload-formats">Định dạng hỗ trợ: {acceptedFormats.join(', ')}</p>

        <input
          ref={fileInputRef}
          type="file"
          accept={acceptedFormats.join(',')}
          style={{ display: 'none' }}
          onChange={handleFileSelect}
        />

        <div className="file-upload-buttons">
          <button
            className="file-upload-button-primary"
            onClick={(e) => {
              e.stopPropagation();
              fileInputRef.current?.click();
            }}
            disabled={isProcessing}
            type="button"
          >
            {isProcessing ? (
              <span style={{ display: 'inline-block', width: '1rem', height: '1rem', border: '2px solid white', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></span>
            ) : (
              'CHỌN FILE'
            )}
          </button>
          <button
            className="file-upload-button-secondary"
            onClick={(e) => {
              e.stopPropagation();
              handleDownloadTemplate();
            }}
            type="button"
          >
            <span className="material-symbols-outlined">download</span>
            DOWNLOAD TEMPLATE
          </button>
        </div>
      </div>

      {errors.length > 0 && (
        <div className="file-upload-error">
          <div className="file-upload-error-title">Lỗi:</div>
          <ul className="file-upload-error-list">
            {errors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default FileUpload;

