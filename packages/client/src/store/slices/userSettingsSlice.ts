import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { type RootState } from '../index';
import { api } from '../../services/api';
import { type RagConfig, type UpdateRagConfigRequest } from '../../types/workspace';

interface UserSettingsState {
    defaultRagConfig: RagConfig | null;
    isLoading: boolean;
    error: string | null;
}

const initialState: UserSettingsState = {
    defaultRagConfig: null,
    isLoading: false,
    error: null,
};

export const fetchDefaultRagConfig = createAsyncThunk(
    'userSettings/fetchDefaultRagConfig',
    async (_, { rejectWithValue }) => {
        try {
            const response = await api.get('/user/settings/rag');
            return response.data as RagConfig;
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.message || error.message);
        }
    },
);

export const updateDefaultRagConfig = createAsyncThunk(
    'userSettings/updateDefaultRagConfig',
    async (ragConfig: UpdateRagConfigRequest, { rejectWithValue }) => {
        try {
            const response = await api.put('/user/settings/rag', ragConfig);
            return response.data as RagConfig;
        } catch (error: any) {
            return rejectWithValue(error.response?.data?.message || error.message);
        }
    },
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
            .addCase(fetchDefaultRagConfig.fulfilled, (state, action: PayloadAction<RagConfig>) => {
                state.defaultRagConfig = action.payload;
                state.isLoading = false;
            })
            .addCase(fetchDefaultRagConfig.rejected, (state, action) => {
                state.isLoading = false;
                state.error = action.payload as string;
            })
            .addCase(updateDefaultRagConfig.pending, (state) => {
                state.isLoading = true;
                state.error = null;
            })
            .addCase(updateDefaultRagConfig.fulfilled, (state, action: PayloadAction<RagConfig>) => {
                state.defaultRagConfig = action.payload;
                state.isLoading = false;
            })
            .addCase(updateDefaultRagConfig.rejected, (state, action) => {
                state.isLoading = false;
                state.error = action.payload as string;
            });
    },
});

export const { clearUserSettingsError } = userSettingsSlice.actions;

export const selectDefaultRagConfig = (state: RootState) =>
    state.userSettings.defaultRagConfig;
export const selectUserSettingsLoading = (state: RootState) =>
    state.userSettings.isLoading;
export const selectUserSettingsError = (state: RootState) => state.userSettings.error;

export default userSettingsSlice.reducer;
