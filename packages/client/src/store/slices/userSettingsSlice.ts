import { createSlice, createAsyncThunk, type PayloadAction } from '@reduxjs/toolkit';
import { type RootState } from '../index';
import apiService, { type DefaultRagConfig } from '../../services/api';

interface UserSettingsState {
    defaultRagConfig: DefaultRagConfig | null;
    isLoading: boolean;
    error: string | null;
}

const initialState: UserSettingsState = {
    defaultRagConfig: null,
    isLoading: false,
    error: null,
};

export const fetchDefaultRagConfig = createAsyncThunk<DefaultRagConfig | null, void>(
    'userSettings/fetchDefaultRagConfig',
    async (_, { rejectWithValue }) => {
        try {
            return await apiService.getDefaultRagConfig();
        } catch (error: unknown) {
            const err = error as { response?: { data?: { message?: string } }; message?: string };
            return rejectWithValue(
                err.response?.data?.message || err.message || 'An error occurred'
            );
        }
    }
);

export const updateDefaultRagConfig = createAsyncThunk<DefaultRagConfig, DefaultRagConfig>(
    'userSettings/updateDefaultRagConfig',
    async (ragConfig: DefaultRagConfig, { rejectWithValue }) => {
        try {
            return await apiService.saveDefaultRagConfig(ragConfig);
        } catch (error: unknown) {
            const err = error as { response?: { data?: { message?: string } }; message?: string };
            return rejectWithValue(
                err.response?.data?.message || err.message || 'An error occurred'
            );
        }
    }
);

const userSettingsSlice = createSlice({
    name: 'userSettings',
    initialState,
    reducers: {
        clearUserSettingsError: (state) => {
            state.error = null;
        },
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchDefaultRagConfig.pending, (state) => {
                state.isLoading = true;
                state.error = null;
            })
            .addCase(
                fetchDefaultRagConfig.fulfilled,
                (state, action: PayloadAction<DefaultRagConfig | null>) => {
                    state.defaultRagConfig = action.payload;
                    state.isLoading = false;
                }
            )
            .addCase(fetchDefaultRagConfig.rejected, (state, action) => {
                state.isLoading = false;
                state.error = action.payload as string;
            })
            .addCase(updateDefaultRagConfig.pending, (state) => {
                state.isLoading = true;
                state.error = null;
            })
            .addCase(
                updateDefaultRagConfig.fulfilled,
                (state, action: PayloadAction<DefaultRagConfig>) => {
                    state.defaultRagConfig = action.payload;
                    state.isLoading = false;
                }
            )
            .addCase(updateDefaultRagConfig.rejected, (state, action) => {
                state.isLoading = false;
                state.error = action.payload as string;
            });
    },
});

export const { clearUserSettingsError } = userSettingsSlice.actions;

export const selectDefaultRagConfig = (state: RootState) => state.userSettings.defaultRagConfig;
export const selectUserSettingsLoading = (state: RootState) => state.userSettings.isLoading;
export const selectUserSettingsError = (state: RootState) => state.userSettings.error;

export default userSettingsSlice.reducer;
