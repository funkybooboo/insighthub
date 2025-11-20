import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import userEvent from '@testing-library/user-event';
import WorkspaceSelector from './WorkspaceSelector';
import workspaceReducer from '../../store/slices/workspaceSlice';
import { apiService } from '../../services/api';
import type { Workspace } from '../../types/workspace';

vi.mock('../../services/api', () => ({
    apiService: {
        listWorkspaces: vi.fn(),
        createWorkspace: vi.fn(),
    },
}));

const mockWorkspaces: Workspace[] = [
    {
        id: 1,
        name: 'Research Papers',
        description: 'Academic research papers',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        document_count: 5,
        session_count: 2,
    },
    {
        id: 2,
        name: 'Personal Notes',
        description: 'My personal notes',
        created_at: '2025-01-02T00:00:00Z',
        updated_at: '2025-01-02T00:00:00Z',
        document_count: 3,
        session_count: 1,
    },
];

function createTestStore(preloadedState = {}) {
    return configureStore({
        reducer: {
            workspace: workspaceReducer,
        },
        preloadedState,
    });
}

function renderWithStore(component: React.ReactElement, store = createTestStore()) {
    return {
        ...render(<Provider store={store}>{component}</Provider>),
        store,
    };
}

describe('WorkspaceSelector', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        localStorage.clear();
    });

    it('should render and load workspaces on mount', async () => {
        vi.mocked(apiService.listWorkspaces).mockResolvedValue(mockWorkspaces);

        renderWithStore(<WorkspaceSelector />);

        await waitFor(() => {
            expect(apiService.listWorkspaces).toHaveBeenCalledTimes(1);
        });

        expect(screen.getByRole('combobox')).toBeInTheDocument();
        expect(screen.getByText('Research Papers')).toBeInTheDocument();
        expect(screen.getByText('Personal Notes')).toBeInTheDocument();
    });

    it('should display "No workspaces" when workspaces list is empty', async () => {
        vi.mocked(apiService.listWorkspaces).mockResolvedValue([]);

        renderWithStore(<WorkspaceSelector />);

        await waitFor(() => {
            expect(apiService.listWorkspaces).toHaveBeenCalled();
        });

        expect(screen.getByText('No workspaces')).toBeInTheDocument();
    });

    it('should change active workspace when selecting a different one', async () => {
        vi.mocked(apiService.listWorkspaces).mockResolvedValue(mockWorkspaces);

        const { store } = renderWithStore(<WorkspaceSelector />);

        await waitFor(() => {
            expect(screen.getByText('Research Papers')).toBeInTheDocument();
        });

        const select = screen.getByRole('combobox');
        await userEvent.selectOptions(select, '2');

        expect(store.getState().workspace.activeWorkspaceId).toBe(2);
        expect(localStorage.getItem('activeWorkspaceId')).toBe('2');
    });

    it('should open create workspace modal when clicking plus button', async () => {
        vi.mocked(apiService.listWorkspaces).mockResolvedValue(mockWorkspaces);

        renderWithStore(<WorkspaceSelector />);

        await waitFor(() => {
            expect(screen.getByText('Research Papers')).toBeInTheDocument();
        });

        const createButton = screen.getByTitle('Create new workspace');
        await userEvent.click(createButton);

        expect(screen.getByText('Create New Workspace')).toBeInTheDocument();
        expect(screen.getByPlaceholderText('e.g., Research Papers')).toBeInTheDocument();
    });

    it('should create a new workspace', async () => {
        const newWorkspace: Workspace = {
            id: 3,
            name: 'New Workspace',
            description: 'Test description',
            created_at: '2025-01-03T00:00:00Z',
            updated_at: '2025-01-03T00:00:00Z',
        };

        vi.mocked(apiService.listWorkspaces).mockResolvedValue(mockWorkspaces);
        vi.mocked(apiService.createWorkspace).mockResolvedValue(newWorkspace);

        const { store } = renderWithStore(<WorkspaceSelector />);

        await waitFor(() => {
            expect(screen.getByText('Research Papers')).toBeInTheDocument();
        });

        const createButton = screen.getByTitle('Create new workspace');
        await userEvent.click(createButton);

        const nameInput = screen.getByPlaceholderText('e.g., Research Papers');
        const descriptionInput = screen.getByPlaceholderText('What is this workspace for?');

        await userEvent.type(nameInput, 'New Workspace');
        await userEvent.type(descriptionInput, 'Test description');

        const submitButton = screen.getByRole('button', { name: 'Create' });
        await userEvent.click(submitButton);

        await waitFor(() => {
            expect(apiService.createWorkspace).toHaveBeenCalledWith({
                name: 'New Workspace',
                description: 'Test description',
            });
        });

        expect(store.getState().workspace.workspaces).toHaveLength(3);
        expect(store.getState().workspace.workspaces[2]).toEqual(newWorkspace);
    });

    it('should not submit form with empty workspace name', async () => {
        vi.mocked(apiService.listWorkspaces).mockResolvedValue(mockWorkspaces);

        renderWithStore(<WorkspaceSelector />);

        await waitFor(() => {
            expect(screen.getByText('Research Papers')).toBeInTheDocument();
        });

        const createButton = screen.getByTitle('Create new workspace');
        await userEvent.click(createButton);

        const submitButton = screen.getByRole('button', { name: 'Create' });
        expect(submitButton).toBeDisabled();
    });

    it('should close modal on cancel', async () => {
        vi.mocked(apiService.listWorkspaces).mockResolvedValue(mockWorkspaces);

        renderWithStore(<WorkspaceSelector />);

        await waitFor(() => {
            expect(screen.getByText('Research Papers')).toBeInTheDocument();
        });

        const createButton = screen.getByTitle('Create new workspace');
        await userEvent.click(createButton);

        expect(screen.getByText('Create New Workspace')).toBeInTheDocument();

        const cancelButton = screen.getByRole('button', { name: /cancel/i });
        await userEvent.click(cancelButton);

        await waitFor(() => {
            expect(screen.queryByText('Create New Workspace')).not.toBeInTheDocument();
        });
    });

    it('should set first workspace as active if none is set', async () => {
        vi.mocked(apiService.listWorkspaces).mockResolvedValue(mockWorkspaces);

        const { store } = renderWithStore(<WorkspaceSelector />);

        await waitFor(() => {
            expect(apiService.listWorkspaces).toHaveBeenCalled();
        });

        expect(store.getState().workspace.activeWorkspaceId).toBe(1);
    });

    it('should disable select when loading', async () => {
        vi.mocked(apiService.listWorkspaces).mockImplementation(
            () => new Promise((resolve) => setTimeout(() => resolve(mockWorkspaces), 100))
        );

        renderWithStore(<WorkspaceSelector />);

        const select = screen.getByRole('combobox');
        expect(select).toBeDisabled();
    });

    it('should handle API error gracefully', async () => {
        const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
        vi.mocked(apiService.listWorkspaces).mockRejectedValue(
            new Error('Failed to load workspaces')
        );

        const { store } = renderWithStore(<WorkspaceSelector />);

        await waitFor(() => {
            expect(store.getState().workspace.error).toBe('Failed to load workspaces');
        });

        consoleError.mockRestore();
    });
});
