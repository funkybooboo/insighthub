import { describe, it, expect } from 'vitest';
import {
    sanitizeString,
    validateWorkspaceName,
    validateDescription,
    validateEmail,
    validateUsername,
    validatePassword,
    validateNumber,
    validateChunkSize,
    validateChunkOverlap,
    validateTopK,
    sanitizeFilename,
    validateFileSize,
    validateFileType,
} from './validation';

describe('validation utilities', () => {
    describe('sanitizeString', () => {
        it('should trim whitespace', () => {
            expect(sanitizeString('  test  ')).toBe('test');
        });

        it('should limit length', () => {
            const longString = 'a'.repeat(2000);
            expect(sanitizeString(longString, 100)).toHaveLength(100);
        });

        it('should handle empty strings', () => {
            expect(sanitizeString('')).toBe('');
            expect(sanitizeString('   ')).toBe('');
        });
    });

    describe('validateWorkspaceName', () => {
        it('should accept valid workspace names', () => {
            expect(validateWorkspaceName('My Workspace').valid).toBe(true);
            expect(validateWorkspaceName('Test-123').valid).toBe(true);
            expect(validateWorkspaceName('Work_Space_1').valid).toBe(true);
        });

        it('should reject empty names', () => {
            const result = validateWorkspaceName('');
            expect(result.valid).toBe(false);
            expect(result.error).toBe('Workspace name is required');
        });

        it('should reject names that are too short', () => {
            const result = validateWorkspaceName('ab');
            expect(result.valid).toBe(false);
            expect(result.error).toContain('at least 3 characters');
        });

        it('should reject names that are too long', () => {
            const result = validateWorkspaceName('a'.repeat(101));
            expect(result.valid).toBe(false);
            expect(result.error).toContain('less than 100 characters');
        });

        it('should reject names with special characters', () => {
            const result = validateWorkspaceName('Test@Workspace!');
            expect(result.valid).toBe(false);
            expect(result.error).toContain('letters, numbers, spaces, hyphens, and underscores');
        });
    });

    describe('validateDescription', () => {
        it('should accept valid descriptions', () => {
            expect(validateDescription('A short description').valid).toBe(true);
            expect(validateDescription('').valid).toBe(true);
        });

        it('should reject descriptions that are too long', () => {
            const result = validateDescription('a'.repeat(501));
            expect(result.valid).toBe(false);
            expect(result.error).toContain('less than 500 characters');
        });
    });

    describe('validateEmail', () => {
        it('should accept valid emails', () => {
            expect(validateEmail('test@example.com').valid).toBe(true);
            expect(validateEmail('users.name+tag@example.co.uk').valid).toBe(true);
        });

        it('should reject empty emails', () => {
            const result = validateEmail('');
            expect(result.valid).toBe(false);
            expect(result.error).toBe('Email is required');
        });

        it('should reject invalid email formats', () => {
            expect(validateEmail('notanemail').valid).toBe(false);
            expect(validateEmail('test@').valid).toBe(false);
            expect(validateEmail('@example.com').valid).toBe(false);
            expect(validateEmail('test @example.com').valid).toBe(false);
        });
    });

    describe('validateUsername', () => {
        it('should accept valid usernames', () => {
            expect(validateUsername('testuser').valid).toBe(true);
            expect(validateUsername('test_user-123').valid).toBe(true);
        });

        it('should reject empty usernames', () => {
            const result = validateUsername('');
            expect(result.valid).toBe(false);
            expect(result.error).toBe('Username is required');
        });

        it('should reject usernames that are too short', () => {
            const result = validateUsername('ab');
            expect(result.valid).toBe(false);
            expect(result.error).toContain('at least 3 characters');
        });

        it('should reject usernames that are too long', () => {
            const result = validateUsername('a'.repeat(51));
            expect(result.valid).toBe(false);
            expect(result.error).toContain('less than 50 characters');
        });

        it('should reject usernames with special characters', () => {
            const result = validateUsername('test@users');
            expect(result.valid).toBe(false);
            expect(result.error).toContain('letters, numbers, hyphens, and underscores');
        });
    });

    describe('validatePassword', () => {
        it('should accept valid passwords', () => {
            expect(validatePassword('Password123').valid).toBe(true);
            expect(validatePassword('MyP@ssw0rd').valid).toBe(true);
        });

        it('should reject empty passwords', () => {
            const result = validatePassword('');
            expect(result.valid).toBe(false);
            expect(result.error).toBe('Password is required');
        });

        it('should reject passwords that are too short', () => {
            const result = validatePassword('Pass1');
            expect(result.valid).toBe(false);
            expect(result.error).toContain('at least 8 characters');
        });

        it('should reject passwords that are too long', () => {
            const result = validatePassword('A1' + 'a'.repeat(127));
            expect(result.valid).toBe(false);
            expect(result.error).toContain('less than 128 characters');
        });

        it('should reject passwords without uppercase letters', () => {
            const result = validatePassword('password123');
            expect(result.valid).toBe(false);
            expect(result.error).toContain('uppercase letter');
        });

        it('should reject passwords without lowercase letters', () => {
            const result = validatePassword('PASSWORD123');
            expect(result.valid).toBe(false);
            expect(result.error).toContain('lowercase letter');
        });

        it('should reject passwords without numbers', () => {
            const result = validatePassword('Password');
            expect(result.valid).toBe(false);
            expect(result.error).toContain('number');
        });
    });

    describe('validateNumber', () => {
        it('should accept valid numbers within range', () => {
            expect(validateNumber(5, 0, 10).valid).toBe(true);
            expect(validateNumber(0, 0, 10).valid).toBe(true);
            expect(validateNumber(10, 0, 10).valid).toBe(true);
        });

        it('should reject NaN', () => {
            const result = validateNumber(NaN, 0, 10);
            expect(result.valid).toBe(false);
            expect(result.error).toContain('must be a number');
        });

        it('should reject numbers below minimum', () => {
            const result = validateNumber(-1, 0, 10);
            expect(result.valid).toBe(false);
            expect(result.error).toContain('at least 0');
        });

        it('should reject numbers above maximum', () => {
            const result = validateNumber(11, 0, 10);
            expect(result.valid).toBe(false);
            expect(result.error).toContain('at most 10');
        });
    });

    describe('RAG configuration validation', () => {
        it('should validate chunk size', () => {
            expect(validateChunkSize(500).valid).toBe(true);
            expect(validateChunkSize(99).valid).toBe(false);
            expect(validateChunkSize(5001).valid).toBe(false);
        });

        it('should validate chunk overlap', () => {
            expect(validateChunkOverlap(200).valid).toBe(true);
            expect(validateChunkOverlap(-1).valid).toBe(false);
            expect(validateChunkOverlap(1001).valid).toBe(false);
        });

        it('should validate top K', () => {
            expect(validateTopK(5).valid).toBe(true);
            expect(validateTopK(0).valid).toBe(false);
            expect(validateTopK(21).valid).toBe(false);
        });
    });

    describe('sanitizeFilename', () => {
        it('should remove special characters', () => {
            expect(sanitizeFilename('test file!@#.pdf')).toBe('test_file___.pdf');
        });

        it('should preserve valid characters', () => {
            expect(sanitizeFilename('test-file_123.pdf')).toBe('test-file_123.pdf');
        });

        it('should limit length', () => {
            const longFilename = 'a'.repeat(300) + '.pdf';
            expect(sanitizeFilename(longFilename)).toHaveLength(255);
        });
    });

    describe('validateFileSize', () => {
        it('should accept valid file sizes', () => {
            expect(validateFileSize(1024).valid).toBe(true);
            expect(validateFileSize(5 * 1024 * 1024).valid).toBe(true);
        });

        it('should reject files with zero size', () => {
            const result = validateFileSize(0);
            expect(result.valid).toBe(false);
            expect(result.error).toContain('greater than 0');
        });

        it('should reject files that are too large', () => {
            const result = validateFileSize(11 * 1024 * 1024);
            expect(result.valid).toBe(false);
            expect(result.error).toContain('less than');
        });

        it('should accept custom max size', () => {
            expect(validateFileSize(50 * 1024, 100 * 1024).valid).toBe(true);
            expect(validateFileSize(150 * 1024, 100 * 1024).valid).toBe(false);
        });
    });

    describe('validateFileType', () => {
        it('should accept valid file types', () => {
            expect(validateFileType('document.pdf').valid).toBe(true);
            expect(validateFileType('notes.txt').valid).toBe(true);
            expect(validateFileType('readme.md').valid).toBe(true);
        });

        it('should reject invalid file types', () => {
            expect(validateFileType('image.jpg').valid).toBe(false);
            expect(validateFileType('archive.zip').valid).toBe(false);
        });

        it('should be case insensitive', () => {
            expect(validateFileType('DOCUMENT.PDF').valid).toBe(true);
        });

        it('should accept custom allowed types', () => {
            expect(validateFileType('image.jpg', ['.jpg', '.png']).valid).toBe(true);
            expect(validateFileType('document.pdf', ['.jpg', '.png']).valid).toBe(false);
        });
    });
});
