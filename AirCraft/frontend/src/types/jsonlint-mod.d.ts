// Type definitions for jsonlint-mod
declare module 'jsonlint-mod' {
  export function parse(jsonString: string): any;
  export function lint(jsonString: string): { error?: string; line?: number; column?: number };
}

