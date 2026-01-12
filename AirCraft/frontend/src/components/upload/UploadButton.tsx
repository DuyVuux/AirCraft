import React, { useRef, useState } from 'react';
import { parseFile, downloadTemplate, type ParseResult } from '@/services/csvParser';
import { deduplicateByKey } from '@/services/duplicateUtils';
import './UploadButton.css';

export interface UploadButtonProps {
    label: string;
    templateHeaders: string[];
    templateFilename: string;
    sampleRows?: string[][];
    onDataParsed: (data: ParseResult) => void;
    disabled?: boolean;
    duplicateKeyField?: string;
}

export default function UploadButton({
    label,
    templateHeaders,
    templateFilename,
    sampleRows = [],
    onDataParsed,
    disabled = false,
    duplicateKeyField,
}: UploadButtonProps) {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleUploadClick = () => {
        console.log('Upload button clicked, triggering file input');
        fileInputRef.current?.click();
    };

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setIsLoading(true);
        try {
            let result = await parseFile(file);

            if (duplicateKeyField && result.rows.length > 0) {
                const { uniqueRows, warnings } = deduplicateByKey(result.rows, duplicateKeyField);
                result = {
                    ...result,
                    rows: uniqueRows,
                    warnings: [...(result.warnings || []), ...warnings],
                };
            }

            onDataParsed(result);
        } catch (err) {
            console.error('Failed to parse file:', err);
            onDataParsed({ headers: [], rows: [], errors: [`Failed to parse file: ${err}`] });
        } finally {
            setIsLoading(false);
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    const handleDownloadTemplate = () => {
        downloadTemplate(templateFilename, templateHeaders, sampleRows);
    };

    return (
        <div className="upload-button-group">
            <input
                ref={fileInputRef}
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={handleFileChange}
                style={{ display: 'none' }}
                onClick={(e) => (e.target as HTMLInputElement).value = ''} // Allow re-uploading same file
            />
            <button
                type="button"
                className="upload-btn primary"
                onClick={handleUploadClick}
                disabled={disabled || isLoading}
            >
                <span className="material-symbols-outlined">
                    {isLoading ? 'sync' : 'upload_file'}
                </span>
                {isLoading ? 'Đang xử lý...' : label}
            </button>
            <button
                type="button"
                className="upload-btn secondary"
                onClick={handleDownloadTemplate}
                disabled={disabled}
                title="Tải template mẫu"
            >
                <span className="material-symbols-outlined">download</span>
                Template
            </button>
        </div>
    );
}
