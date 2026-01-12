import * as XLSX from 'xlsx';

export interface ParsedRow {
    [key: string]: string;
}

export interface ParseResult {
    headers: string[];
    rows: ParsedRow[];
    errors: string[];
    warnings?: string[];
}

function detectDelimiter(content: string): string {
    const firstLine = content.split('\n')[0] || '';
    const semicolonCount = (firstLine.match(/;/g) || []).length;
    const commaCount = (firstLine.match(/,/g) || []).length;
    return semicolonCount > commaCount ? ';' : ',';
}

function parseCSVLine(line: string, delimiter: string): string[] {
    const result: string[] = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        if (char === '"') {
            if (inQuotes && line[i + 1] === '"') {
                current += '"';
                i++;
            } else {
                inQuotes = !inQuotes;
            }
        } else if (char === delimiter && !inQuotes) {
            result.push(current.trim());
            current = '';
        } else {
            current += char;
        }
    }
    result.push(current.trim());
    return result;
}

export function parseCSV(content: string): ParseResult {
    const errors: string[] = [];
    const lines = content.split('\n').filter(line => line.trim());

    if (lines.length === 0) {
        return { headers: [], rows: [], errors: ['File is empty'] };
    }

    const delimiter = detectDelimiter(content);
    const headers = parseCSVLine(lines[0], delimiter);
    const rows: ParsedRow[] = [];

    for (let i = 1; i < lines.length; i++) {
        const values = parseCSVLine(lines[i], delimiter);
        if (values.length !== headers.length) {
            errors.push(`Row ${i + 1}: Expected ${headers.length} columns, got ${values.length}`);
            continue;
        }
        const row: ParsedRow = {};
        headers.forEach((header, idx) => {
            row[header] = values[idx];
        });
        rows.push(row);
    }

    return { headers, rows, errors };
}

export async function parseXLSX(file: File): Promise<ParseResult> {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = new Uint8Array(e.target?.result as ArrayBuffer);
                const workbook = XLSX.read(data, { type: 'array' });
                const sheetName = workbook.SheetNames[0];
                const sheet = workbook.Sheets[sheetName];
                const jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 }) as unknown[][];

                if (jsonData.length === 0) {
                    resolve({ headers: [], rows: [], errors: ['File is empty'] });
                    return;
                }

                const headers = (jsonData[0] as unknown[]).map(h => String(h || '').trim());
                const rows: ParsedRow[] = [];

                for (let i = 1; i < jsonData.length; i++) {
                    const rowData = jsonData[i] as unknown[];
                    if (!rowData || rowData.every(cell => !cell)) continue;

                    const row: ParsedRow = {};
                    headers.forEach((header, idx) => {
                        row[header] = String(rowData[idx] || '').trim();
                    });
                    rows.push(row);
                }

                resolve({ headers, rows, errors: [] });
            } catch (err) {
                resolve({ headers: [], rows: [], errors: [`Failed to parse XLSX: ${err}`] });
            }
        };
        reader.readAsArrayBuffer(file);
    });
}

export async function parseFile(file: File): Promise<ParseResult> {
    const fileName = file.name.toLowerCase();

    if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
        return parseXLSX(file);
    }

    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const content = e.target?.result as string;
            resolve(parseCSV(content));
        };
        reader.readAsText(file, 'UTF-8');
    });
}

export function generateCSVTemplate(headers: string[], sampleRows: string[][] = []): string {
    const lines = [headers.join(',')];
    sampleRows.forEach(row => {
        lines.push(row.map(cell => cell.includes(',') ? `"${cell}"` : cell).join(','));
    });
    return lines.join('\n');
}

export function downloadTemplate(filename: string, headers: string[], sampleRows: string[][] = []) {
    const content = generateCSVTemplate(headers, sampleRows);
    const blob = new Blob(['\ufeff' + content], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}
