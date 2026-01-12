import type { ParsedRow } from './csvParser';

export interface DeduplicateResult {
    uniqueRows: ParsedRow[];
    warnings: string[];
}

export function deduplicateByKey(
    rows: ParsedRow[],
    keyField: string
): DeduplicateResult {
    const warnings: string[] = [];
    const rowMap = new Map<string, { row: ParsedRow; firstIndex: number; count: number }>();

    rows.forEach((row, index) => {
        const key = row[keyField]?.trim();
        if (!key) return;

        const existing = rowMap.get(key);
        if (existing) {
            existing.row = row;
            existing.count++;
        } else {
            rowMap.set(key, { row, firstIndex: index + 2, count: 1 });
        }
    });

    rowMap.forEach((info, key) => {
        if (info.count > 1) {
            warnings.push(`⚠️ Mã "${key}" xuất hiện ${info.count} lần - giữ bản ghi cuối cùng`);
        }
    });

    const uniqueRows = Array.from(rowMap.values()).map(info => info.row);
    return { uniqueRows, warnings };
}
