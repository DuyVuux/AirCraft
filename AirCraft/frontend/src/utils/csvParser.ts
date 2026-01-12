import Papa from 'papaparse';

export interface ParseResult<T> {
  data: T[];
  errors: string[];
}

export const parseCSV = async <T>(
  file: File,
  headers: string[]
): Promise<ParseResult<T>> => {
  return new Promise((resolve) => {
    Papa.parse<T>(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        const errors: string[] = [];

        // Validate headers
        if (results.meta.fields) {
          const missingHeaders = headers.filter(
            (h) => !results.meta.fields!.includes(h)
          );
          if (missingHeaders.length > 0) {
            errors.push(`Missing headers: ${missingHeaders.join(', ')}`);
          }
        }

        // Validate data
        if (results.errors.length > 0) {
          errors.push(
            ...results.errors.map((e) => `Row ${e.row}: ${e.message}`)
          );
        }

        resolve({
          data: results.data,
          errors,
        });
      },
      error: (error) => {
        resolve({
          data: [],
          errors: [error.message],
        });
      },
    });
  });
};

export const exportToCSV = <T extends Record<string, any>>(
  data: T[],
  filename: string
): void => {
  const csv = Papa.unparse(data);
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

