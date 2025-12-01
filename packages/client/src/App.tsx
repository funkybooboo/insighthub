import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { useEffect, useState } from 'react';
import LoginForm from './components/auth/LoginForm';
import SignupForm from './components/auth/SignupForm';
import ProtectedRoute from './components/auth/ProtectedRoute';
import ChatBot from './components/chat/ChatBot';
import WorkspaceColumn from './components/workspace/WorkspaceColumn';
import ChatSessionList from './components/chat/ChatSessionList';
import DocumentManager from './components/upload/DocumentManager';
import Layout from './components/shared/Layout';
import SettingsPage from './pages/SettingsPage';
import WorkspacesPage from './pages/WorkspacesPage';
import WorkspaceDetailPage from './pages/WorkspaceDetailPage';
import { setTheme } from './store/slices/themeSlice';
import { useStatusUpdates } from './hooks/useStatusUpdates';
import type { RootState } from './store';
import { selectActiveWorkspaceId } from './store/slices/workspaceSlice';

function AppContent() {
    const dispatch = useDispatch();
    const { isAuthenticated, user } = useSelector((state: RootState) => state.auth);
    const { theme } = useSelector((state: RootState) => state.theme);
    const activeWorkspaceId = useSelector(selectActiveWorkspaceId);
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);

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
    }, [user?.theme_preference, dispatch]);

    const layout = (chatColumn: React.ReactNode) => (
        <Layout
            workspaceColumn={<WorkspaceColumn />}
            chatSessionColumn={<ChatSessionList />}
            chatColumn={chatColumn}
            documentColumn={
                activeWorkspaceId ? (
                    <DocumentManager workspaceId={activeWorkspaceId} />
                ) : (
                    <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                        Select a workspace to manage documents
                    </div>
                )
            }
            openSettings={() => setIsSettingsOpen(true)}
        />
    );

    return (
        <>
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
                        path="/workspaces"
                        element={<ProtectedRoute>{layout(<WorkspacesPage />)}</ProtectedRoute>}
                    />
                    <Route
                        path="/workspaces/:workspaceId"
                        element={<ProtectedRoute>{layout(<WorkspaceDetailPage />)}</ProtectedRoute>}
                    />
                    <Route
                        path="/"
                        element={<ProtectedRoute>{layout(<ChatBot />)}</ProtectedRoute>}
                    />
                </Routes>
            </BrowserRouter>
            {isAuthenticated && (
                <SettingsPage isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
            )}
        </>
    );
}

function App() {
    return <AppContent />;
}

export default App;
