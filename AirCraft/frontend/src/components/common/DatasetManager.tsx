import React, { useState } from 'react';
import type { DatasetMeta } from '@/types/dataset';
import './DatasetManager.css';

interface DatasetManagerProps {
    datasets: DatasetMeta[];
    currentDatasetId: string | null;
    onSelectDataset: (id: string) => void;
    onCreateDataset: (name: string) => void;
    onDeleteDataset: (id: string) => void;
    onRenameDataset: (id: string, name: string) => void;
}

type DialogType = 'create' | 'rename' | 'delete' | null;

function DatasetManager({
    datasets,
    currentDatasetId,
    onSelectDataset,
    onCreateDataset,
    onDeleteDataset,
    onRenameDataset,
}: DatasetManagerProps) {
    const [dialogType, setDialogType] = useState<DialogType>(null);
    const [inputValue, setInputValue] = useState('');

    const currentDataset = datasets.find(d => d.id === currentDatasetId);

    const handleOpenCreate = () => {
        setInputValue('');
        setDialogType('create');
    };

    const handleOpenRename = () => {
        setInputValue(currentDataset?.name || '');
        setDialogType('rename');
    };

    const handleOpenDelete = () => {
        setDialogType('delete');
    };

    const handleCloseDialog = () => {
        setDialogType(null);
        setInputValue('');
    };

    const handleConfirmCreate = () => {
        if (inputValue.trim()) {
            onCreateDataset(inputValue.trim());
            handleCloseDialog();
        }
    };

    const handleConfirmRename = () => {
        if (inputValue.trim() && currentDatasetId) {
            onRenameDataset(currentDatasetId, inputValue.trim());
            handleCloseDialog();
        }
    };

    const handleConfirmDelete = () => {
        if (currentDatasetId) {
            onDeleteDataset(currentDatasetId);
            handleCloseDialog();
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            if (dialogType === 'create') handleConfirmCreate();
            if (dialogType === 'rename') handleConfirmRename();
        }
        if (e.key === 'Escape') {
            handleCloseDialog();
        }
    };

    return (
        <>
            <div className="dataset-manager">
                <div className="dataset-select-wrapper">
                    <select
                        className="dataset-select"
                        value={currentDatasetId || ''}
                        onChange={(e) => onSelectDataset(e.target.value)}
                    >
                        {datasets.map((ds) => (
                            <option key={ds.id} value={ds.id}>
                                {ds.name}
                            </option>
                        ))}
                    </select>
                    <span className="material-symbols-outlined dataset-select-icon">expand_more</span>
                </div>

                <button
                    className="dataset-btn primary"
                    onClick={handleOpenCreate}
                    title="Tạo bộ dữ liệu mới"
                >
                    <span className="material-symbols-outlined">add</span>
                </button>

                <button
                    className="dataset-btn"
                    onClick={handleOpenRename}
                    title="Đổi tên"
                    disabled={!currentDatasetId}
                >
                    <span className="material-symbols-outlined">edit</span>
                </button>

                <button
                    className="dataset-btn danger"
                    onClick={handleOpenDelete}
                    title="Xóa bộ dữ liệu"
                    disabled={!currentDatasetId || datasets.length <= 1}
                >
                    <span className="material-symbols-outlined">delete</span>
                </button>
            </div>

            {dialogType && (
                <div className="dataset-dialog-overlay" onClick={handleCloseDialog}>
                    <div className="dataset-dialog" onClick={(e) => e.stopPropagation()}>
                        {dialogType === 'create' && (
                            <>
                                <h3 className="dataset-dialog-title">Tạo bộ dữ liệu mới</h3>
                                <input
                                    className="dataset-dialog-input"
                                    type="text"
                                    placeholder="Nhập tên bộ dữ liệu..."
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    autoFocus
                                />
                                <div className="dataset-dialog-actions">
                                    <button className="dataset-dialog-btn cancel" onClick={handleCloseDialog}>
                                        Hủy
                                    </button>
                                    <button
                                        className="dataset-dialog-btn confirm"
                                        onClick={handleConfirmCreate}
                                        disabled={!inputValue.trim()}
                                    >
                                        Tạo
                                    </button>
                                </div>
                            </>
                        )}

                        {dialogType === 'rename' && (
                            <>
                                <h3 className="dataset-dialog-title">Đổi tên bộ dữ liệu</h3>
                                <input
                                    className="dataset-dialog-input"
                                    type="text"
                                    placeholder="Nhập tên mới..."
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    autoFocus
                                />
                                <div className="dataset-dialog-actions">
                                    <button className="dataset-dialog-btn cancel" onClick={handleCloseDialog}>
                                        Hủy
                                    </button>
                                    <button
                                        className="dataset-dialog-btn confirm"
                                        onClick={handleConfirmRename}
                                        disabled={!inputValue.trim()}
                                    >
                                        Lưu
                                    </button>
                                </div>
                            </>
                        )}

                        {dialogType === 'delete' && (
                            <>
                                <h3 className="dataset-dialog-title">Xóa bộ dữ liệu</h3>
                                <p className="dataset-dialog-message">
                                    Bạn có chắc chắn muốn xóa bộ dữ liệu "<strong>{currentDataset?.name}</strong>"?
                                    <br />
                                    Hành động này không thể hoàn tác.
                                </p>
                                <div className="dataset-dialog-actions">
                                    <button className="dataset-dialog-btn cancel" onClick={handleCloseDialog}>
                                        Hủy
                                    </button>
                                    <button className="dataset-dialog-btn danger" onClick={handleConfirmDelete}>
                                        Xóa
                                    </button>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            )}
        </>
    );
}

export default DatasetManager;
