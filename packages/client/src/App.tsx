import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { useEffect } from 'react';
import LoginForm from './components/auth/LoginForm';
import SignupForm from './components/auth/SignupForm';
import ProtectedRoute from './components/auth/ProtectedRoute';
import ChatBot from './components/chat/ChatBot';
import ChatSidebar from './components/chat/ChatSidebar';
import UserMenu from './components/auth/UserMenu';
import WorkspaceSelector from './components/workspace/WorkspaceSelector';
import WorkspaceSettings from './components/workspace/WorkspaceSettings';
import { SettingsPage } from './components/settings';
import WorkspacesPage from './pages/WorkspacesPage';
import WorkspaceDetailPage from './pages/WorkspaceDetailPage';
import { setTheme } from './store/slices/themeSlice';
import { useStatusUpdates } from './hooks/useStatusUpdates';
import type { RootState } from './store';

function MainApp() {
    return (
        <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-950">
            <div className="flex items-center justify-between border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
                <WorkspaceSelector />
                <div className="flex items-center gap-2 px-4">
                    <WorkspaceSettings />
                    <UserMenu />
                </div>
            </div>
            <div className="flex-1 flex overflow-hidden">
                <ChatSidebar />
                <main className="flex-1 flex flex-col overflow-hidden bg-white dark:bg-gray-900">
                    <ChatBot />
                </main>
            </div>
        </div>
    );
}

function App() {
    const dispatch = useDispatch();
    const { isAuthenticated, user } = useSelector((state: RootState) => state.auth);
    const { theme } = useSelector((state: RootState) => state.theme);

    // Subscribe to real-time status updates when authenticated
    useStatusUpdates();

    useEffect(() => {
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }, [theme]);

    useEffect(() => {
        if (user?.theme_preference) {
            dispatch(setTheme(user.theme_preference as 'light' | 'dark'));
        }
        // Only sync from user on login/user data change, not on theme toggle
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [user?.theme_preference, dispatch]);

    return (
        <BrowserRouter>
            <Routes>
                <Route
                    path="/login"
                    element={isAuthenticated ? <Navigate to="/" replace /> : <LoginForm />}
                />
                <Route
                    path="/signup"
                    element={isAuthenticated ? <Navigate to="/" replace /> : <SignupForm />}
                />
                <Route
                    path="/settings"
                    element={
                        <ProtectedRoute>
                            <SettingsPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/workspaces"
                    element={
                        <ProtectedRoute>
                            <WorkspacesPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/workspaces/:workspaceId"
                    element={
                        <ProtectedRoute>
                            <WorkspaceDetailPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/"
                    element={
                        <ProtectedRoute>
                            <MainApp />
                        </ProtectedRoute>
                    }
                />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
