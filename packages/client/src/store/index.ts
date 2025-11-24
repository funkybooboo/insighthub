import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import chatReducer from './slices/chatSlice';
import statusReducer from './slices/statusSlice';
import themeReducer from './slices/themeSlice';
import workspaceReducer from './slices/workspaceSlice';
import userSettingsReducer from './slices/userSettingsSlice'; // Import the new reducer

export const store = configureStore({
    reducer: {
        auth: authReducer,
        chat: chatReducer,
        theme: themeReducer,
        workspace: workspaceReducer,
        status: statusReducer,
        userSettings: userSettingsReducer, // Add the new reducer here
    },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
