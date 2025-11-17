import { createSlice } from '@reduxjs/toolkit';

export type Theme = 'light' | 'dark';

interface ThemeState {
    theme: Theme;
}

const getInitialTheme = (): Theme => {
    const stored = localStorage.getItem('theme');
    if (stored === 'light' || stored === 'dark') {
        return stored;
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
            localStorage.setItem('theme', state.theme);
        },
        setTheme: (state, action: { payload: Theme }) => {
            state.theme = action.payload;
            localStorage.setItem('theme', state.theme);
        },
    },
});

export const { toggleTheme, setTheme } = themeSlice.actions;
export default themeSlice.reducer;
