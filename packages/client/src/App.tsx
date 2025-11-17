import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { useEffect } from 'react';
import LoginForm from './components/auth/LoginForm';
import SignupForm from './components/auth/SignupForm';
import ProtectedRoute from './components/auth/ProtectedRoute';
import ChatBot from './components/chat/ChatBot';
import ChatSidebar from './components/chat/ChatSidebar';
import UserMenu from './components/auth/UserMenu';
import type { RootState } from './store';

function MainApp() {
    return (
        <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-950">
            <UserMenu />
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
    const { isAuthenticated } = useSelector((state: RootState) => state.auth);
    const { theme } = useSelector((state: RootState) => state.theme);

    useEffect(() => {
        if (theme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }, [theme]);

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
