import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import chatReducer from './slices/chatSlice';
import statusReducer from './slices/statusSlice';
import themeReducer from './slices/themeSlice';
import workspaceReducer from './slices/workspaceSlice';

export const store = configureStore({
    reducer: {
        auth: authReducer,
        chat: chatReducer,
        theme: themeReducer,
        workspace: workspaceReducer,
        status: statusReducer,
    },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
