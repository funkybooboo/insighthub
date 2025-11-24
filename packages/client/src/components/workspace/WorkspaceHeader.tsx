import React from 'react';
import { FaChevronDown, FaFolderOpen } from 'react-icons/fa';
import { type Workspace } from '../../types/workspace';
import { LoadingSpinner } from '../shared';

interface WorkspaceHeaderProps {
    activeWorkspace?: Workspace;
    workspacesLoading: boolean;
    showWorkspaceDropdown: boolean;
    setShowWorkspaceDropdown: (show: boolean) => void;
}

const WorkspaceHeader: React.FC<WorkspaceHeaderProps> = ({
    activeWorkspace,
    workspacesLoading,
    showWorkspaceDropdown,
    setShowWorkspaceDropdown,
}) => {
    return (
        <div className="relative">
            <button
                onClick={() => setShowWorkspaceDropdown(!showWorkspaceDropdown)}
                className="w-full flex items-center justify-between px-3 py-2.5 bg-gray-50 dark:bg-gray-800 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700/70 transition-colors border border-gray-200/60 dark:border-gray-700/50"
                disabled={workspacesLoading}
            >
                <div className="flex items-center gap-2.5 min-w-0">
                    <FaFolderOpen className="text-blue-500 dark:text-blue-400 flex-shrink-0" />
                    <span className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                        {activeWorkspace?.name || 'Select Workspace'}
                    </span>
                </div>
                {workspacesLoading ? (
                    <LoadingSpinner size="sm" className="text-gray-500" />
                ) : (
                    <FaChevronDown
                        className={`w-3 h-3 text-gray-400 transition-transform flex-shrink-0 ${
                            showWorkspaceDropdown ? 'rotate-180' : ''
                        }`}
                    />
                )}
            </button>
        </div>
    );
};

export default WorkspaceHeader;
