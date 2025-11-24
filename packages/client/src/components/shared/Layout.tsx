import React, { type ReactNode } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { selectUser } from '../../store/slices/authSlice';

interface LayoutProps {
    workspaceColumn: ReactNode;
    chatSessionColumn: ReactNode;
    chatColumn: ReactNode;
    documentColumn: ReactNode;
    headerContent?: ReactNode;
}

const Layout: React.FC<LayoutProps> = ({
    workspaceColumn,
    chatSessionColumn,
    chatColumn,
    documentColumn,
    headerContent,
}) => {
    const navigate = useNavigate();
    const { logout } = useAuth();
    const user = useSelector(selectUser);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="flex h-screen bg-gray-100 dark:bg-gray-950 text-gray-900 dark:text-gray-100">
            {/* Left Columns Container */}
            <div className="flex h-full">
                {/* Workspace Column (Left 1) */}
                <aside className="w-64 bg-white dark:bg-gray-900 border-r border-gray-200/80 dark:border-gray-800 flex flex-col">
                    {workspaceColumn}
                </aside>

                {/* Chat Session Column (Left 2) */}
                <aside className="w-64 bg-white dark:bg-gray-900 border-r border-gray-200/80 dark:border-gray-800 flex flex-col">
                    {chatSessionColumn}
                </aside>
            </div>

            {/* Main Content Area */}
            <main className="flex-1 flex flex-col overflow-hidden">
                <header className="flex-shrink-0 h-14 flex items-center justify-between px-6 bg-white dark:bg-gray-900 border-b border-gray-200/80 dark:border-gray-800">
                    <div className="flex-1">{headerContent}</div>
                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => navigate('/settings')}
                            className="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400"
                        >
                            Settings
                        </button>
                        <button
                            onClick={handleLogout}
                            className="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-red-600 dark:hover:text-red-400"
                        >
                            Logout
                        </button>
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                            {user?.username}
                        </span>
                    </div>
                </header>
                <div className="flex-1 flex overflow-hidden">
                    {/* Chat Column (Middle) */}
                    <section className="flex-1 flex flex-col overflow-hidden">{chatColumn}</section>

                    {/* Document Column (Right) */}
                    <section className="w-96 bg-white dark:bg-gray-900 border-l border-gray-200/80 dark:border-gray-800 flex flex-col">
                        {documentColumn}
                    </section>
                </div>
            </main>
        </div>
    );
};

export default Layout;
