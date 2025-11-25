/**
 * Workspace types for multi-workspace document and chat management
 * Re-exports shared types with client-specific extensions
 */

export {
    BaseRagConfig,
    VectorRagConfig,
    GraphRagConfig,
    RagConfig,
    CreateRagConfigRequest,
    UpdateRagConfigRequest,
    Workspace,
    CreateWorkspaceRequest,
    UpdateWorkspaceRequest,
} from '@insighthub/shared-typescript';

// Client-specific extensions
export interface WorkspaceState {
    workspaces: Workspace[];
    activeWorkspaceId: number | null;
    isLoading: boolean;
    error: string | null;
}
