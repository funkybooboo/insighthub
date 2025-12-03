-- Rollback: Remove CLI state table

-- Drop the trigger first
DROP TRIGGER IF EXISTS update_cli_state_updated_at ON cli_state;

-- Drop the table
DROP TABLE IF EXISTS cli_state;
