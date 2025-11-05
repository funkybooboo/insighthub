import { describe, expect, test } from 'bun:test';
import { cn } from './utils';

describe('cn utility', () => {
    test('merges class names', () => {
        const result = cn('foo', 'bar');
        expect(result).toBe('foo bar');
    });

    test('handles conditional classes', () => {
        const isActive = false;
        const result = cn('foo', isActive && 'bar', 'baz');
        expect(result).toBe('foo baz');
    });

    test('merges tailwind classes correctly', () => {
        const result = cn('px-2 py-1', 'px-4');
        expect(result).toBe('py-1 px-4');
    });

    test('handles empty input', () => {
        const result = cn();
        expect(result).toBe('');
    });

    test('handles undefined and null', () => {
        const result = cn('foo', undefined, 'bar', null, 'baz');
        expect(result).toBe('foo bar baz');
    });
});
