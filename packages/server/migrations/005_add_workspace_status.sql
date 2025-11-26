-- Add status column to workspaces table
-- Migration: 005_add_workspace_status.sql

ALTER TABLE workspaces ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'ready';

-- Update existing workspaces to have 'ready' status
UPDATE workspaces SET status = 'ready' WHERE status IS NULL;