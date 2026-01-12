import { format, parseISO, isValid } from 'date-fns';

export const formatISO = (date: Date | string): string => {
  const d = typeof date === 'string' ? parseISO(date) : date;
  if (!isValid(d)) {
    throw new Error('Invalid date');
  }
  return format(d, "yyyy-MM-dd'T'HH:mm:ss'Z'");
};

export const formatTime = (date: Date | string): string => {
  const d = typeof date === 'string' ? parseISO(date) : date;
  if (!isValid(d)) {
    throw new Error('Invalid date');
  }
  return format(d, 'HH:mm');
};

export const formatDateTime = (date: Date | string): string => {
  const d = typeof date === 'string' ? parseISO(date) : date;
  if (!isValid(d)) {
    throw new Error('Invalid date');
  }
  return format(d, 'yyyy-MM-dd HH:mm');
};

export const parseISOString = (isoString: string): Date => {
  const date = parseISO(isoString);
  if (!isValid(date)) {
    throw new Error('Invalid ISO string');
  }
  return date;
};

export const parseTimeString = (timeString: string): Date => {
  const [hours, minutes] = timeString.split(':').map(Number);
  const date = new Date();
  date.setHours(hours, minutes, 0, 0);
  return date;
};

