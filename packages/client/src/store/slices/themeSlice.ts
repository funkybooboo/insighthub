import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import apiService from '../../services/api';
import type { RootState } from '../index';

export type Theme = 'light' | 'dark';

interface ThemeState {
    theme: Theme;
}

const getInitialTheme = (): Theme => {
    try {
        const stored = localStorage.getItem('theme');
        if (stored === 'light' || stored === 'dark') {
            return stored;
        }
    } catch {
        // localStorage not available (e.g., in tests or SSR)
    }
    return 'dark';
};

const initialState: ThemeState = {
    theme: getInitialTheme(),
};

const themeSlice = createSlice({
    name: 'theme',
    initialState,
    reducers: {
        toggleTheme: (state) => {
            state.theme = state.theme === 'dark' ? 'light' : 'dark';
            try {
                localStorage.setItem('theme', state.theme);
            } catch {
                // localStorage not available (e.g., in tests or SSR)
            }
        },
        setTheme: (state, action: PayloadAction<Theme>) => {
            state.theme = action.payload;
            try {
                localStorage.setItem('theme', state.theme);
            } catch {
                // localStorage not available (e.g., in tests or SSR)
            }
        },
    },
});

export const { toggleTheme, setTheme } = themeSlice.actions;

export const toggleThemeAndSave = createAsyncThunk<void, void, { state: RootState }>(
    'theme/toggleAndSave',
    async (_, { dispatch, getState }) => {
        dispatch(toggleTheme());
        const newTheme = getState().theme.theme;
        try {
            await apiService.updatePreferences({ theme_preference: newTheme });
        } catch (error) {
            console.error('Failed to save theme preference:', error);
        }
    }
);

export default themeSlice.reducer;
