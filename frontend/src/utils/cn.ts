import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Enterprise-grade utility for merging Tailwind classes with proper collision handling.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
