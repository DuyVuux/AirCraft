import * as XLSX from 'xlsx';

export interface ParseResult<T> {
  data: T[];
  errors: string[];
}

export const parseExcel = async <T>(
  file: File,
  headers: string[]
): Promise<ParseResult<T>> => {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = e.target?.result;
        const workbook = XLSX.read(data, { type: 'binary' });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const jsonData = XLSX.utils.sheet_to_json<T>(worksheet);

        const errors: string[] = [];

        // Validate headers
        if (jsonData.length > 0) {
          const firstRow = jsonData[0] as Record<string, any>;
          const missingHeaders = headers.filter(
            (h) => !Object.keys(firstRow).includes(h)
          );
          if (missingHeaders.length > 0) {
            errors.push(`Missing headers: ${missingHeaders.join(', ')}`);
          }
        }

        resolve({
          data: jsonData,
          errors,
        });
      } catch (error) {
        resolve({
          data: [],
          errors: [(error as Error).message],
        });
      }
    };
    reader.onerror = () => {
      resolve({
        data: [],
        errors: ['Failed to read file'],
      });
    };
    reader.readAsBinaryString(file);
  });
};

export const exportToExcel = <T extends Record<string, any>>(
  data: T[],
  filename: string,
  sheetName = 'Sheet1'
): void => {
  const worksheet = XLSX.utils.json_to_sheet(data);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, sheetName);
  XLSX.writeFile(workbook, filename);
};

