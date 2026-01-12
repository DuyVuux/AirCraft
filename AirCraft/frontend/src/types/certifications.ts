/**
 * Danh sách các chứng chỉ có sẵn trong hệ thống
 * Đọc từ file config/certifications.txt
 */
import certificationsRaw from '../../config/certifications.txt?raw';

export const AVAILABLE_CERTIFICATIONS = certificationsRaw
    .split('\n')
    .map((line: string) => line.trim())
    .filter((line: string) => line.length > 0);

export type Certification = string;
