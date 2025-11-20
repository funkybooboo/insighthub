/**
 * Input validation and sanitization utilities
 */

/**
 * Validates and sanitizes a string input
 */
export function sanitizeString(input: string, maxLength: number = 1000): string {
    return input.trim().slice(0, maxLength);
}

/**
 * Validates workspace name
 */
export function validateWorkspaceName(name: string): { valid: boolean; error?: string } {
    if (name.trim().length === 0) {
        return { valid: false, error: 'Workspace name is required' };
    }

    if (name.trim().length < 3) {
        return { valid: false, error: 'Workspace name must be at least 3 characters' };
    }

    if (name.length > 100) {
        return { valid: false, error: 'Workspace name must be less than 100 characters' };
    }

    const validNamePattern = /^[a-zA-Z0-9\s\-_]+$/;
    if (!validNamePattern.test(name.trim())) {
        return {
            valid: false,
            error: 'Workspace name can only contain letters, numbers, spaces, hyphens, and underscores',
        };
    }

    return { valid: true };
}

/**
 * Validates workspace description
 */
export function validateDescription(description: string): { valid: boolean; error?: string } {
    if (description.length > 500) {
        return { valid: false, error: 'Description must be less than 500 characters' };
    }

    return { valid: true };
}

/**
 * Validates email format
 */
export function validateEmail(email: string): { valid: boolean; error?: string } {
    const sanitized = sanitizeString(email, 255);

    if (sanitized.length === 0) {
        return { valid: false, error: 'Email is required' };
    }

    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(sanitized)) {
        return { valid: false, error: 'Invalid email format' };
    }

    return { valid: true };
}

/**
 * Validates username format
 */
export function validateUsername(username: string): { valid: boolean; error?: string } {
    if (username.trim().length === 0) {
        return { valid: false, error: 'Username is required' };
    }

    if (username.trim().length < 3) {
        return { valid: false, error: 'Username must be at least 3 characters' };
    }

    if (username.length > 50) {
        return { valid: false, error: 'Username must be less than 50 characters' };
    }

    const validUsernamePattern = /^[a-zA-Z0-9_-]+$/;
    if (!validUsernamePattern.test(username.trim())) {
        return {
            valid: false,
            error: 'Username can only contain letters, numbers, hyphens, and underscores',
        };
    }

    return { valid: true };
}

/**
 * Validates password strength
 */
export function validatePassword(password: string): { valid: boolean; error?: string } {
    if (password.length === 0) {
        return { valid: false, error: 'Password is required' };
    }

    if (password.length < 8) {
        return { valid: false, error: 'Password must be at least 8 characters' };
    }

    if (password.length > 128) {
        return { valid: false, error: 'Password must be less than 128 characters' };
    }

    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);

    if (!hasUpperCase || !hasLowerCase || !hasNumber) {
        return {
            valid: false,
            error: 'Password must contain at least one uppercase letter, one lowercase letter, and one number',
        };
    }

    return { valid: true };
}

/**
 * Validates numeric input within a range
 */
export function validateNumber(
    value: number,
    min: number,
    max: number,
    fieldName: string = 'Value'
): { valid: boolean; error?: string } {
    if (isNaN(value)) {
        return { valid: false, error: `${fieldName} must be a number` };
    }

    if (value < min) {
        return { valid: false, error: `${fieldName} must be at least ${min}` };
    }

    if (value > max) {
        return { valid: false, error: `${fieldName} must be at most ${max}` };
    }

    return { valid: true };
}

/**
 * Validates RAG configuration chunk size
 */
export function validateChunkSize(chunkSize: number): { valid: boolean; error?: string } {
    return validateNumber(chunkSize, 100, 5000, 'Chunk size');
}

/**
 * Validates RAG configuration chunk overlap
 */
export function validateChunkOverlap(chunkOverlap: number): { valid: boolean; error?: string } {
    return validateNumber(chunkOverlap, 0, 1000, 'Chunk overlap');
}

/**
 * Validates RAG configuration top K
 */
export function validateTopK(topK: number): { valid: boolean; error?: string } {
    return validateNumber(topK, 1, 20, 'Top K');
}

/**
 * Sanitizes filename for safe display
 */
export function sanitizeFilename(filename: string): string {
    return filename.replace(/[^a-zA-Z0-9.\-_]/g, '_').slice(0, 255);
}

/**
 * Validates file size (in bytes)
 */
export function validateFileSize(
    size: number,
    maxSize: number = 10 * 1024 * 1024
): { valid: boolean; error?: string } {
    if (size <= 0) {
        return { valid: false, error: 'File size must be greater than 0' };
    }

    if (size > maxSize) {
        const maxSizeMB = (maxSize / (1024 * 1024)).toFixed(2);
        return { valid: false, error: `File size must be less than ${maxSizeMB} MB` };
    }

    return { valid: true };
}

/**
 * Validates file type
 */
export function validateFileType(
    filename: string,
    allowedTypes: string[] = ['.pdf', '.txt', '.md']
): { valid: boolean; error?: string } {
    const extension = filename.toLowerCase().slice(filename.lastIndexOf('.'));

    if (!allowedTypes.includes(extension)) {
        return {
            valid: false,
            error: `File type must be one of: ${allowedTypes.join(', ')}`,
        };
    }

    return { valid: true };
}
