-- Rollback: Add user_id back to workspaces table

-- Add the user_id column (assuming it was an INTEGER)
ALTER TABLE workspaces
ADD COLUMN user_id INTEGER;

-- Create the index
CREATE INDEX IF NOT EXISTS ix_workspaces_user_id ON workspaces(user_id);
