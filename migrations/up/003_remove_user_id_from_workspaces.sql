-- Remove user_id from workspace table (single-user system)
-- Drop the index first
DROP INDEX IF EXISTS ix_workspaces_user_id;

-- Drop the column
ALTER TABLE workspaces
DROP COLUMN user_id;
