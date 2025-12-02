-- Add CLI state table for persisting selected workspace and session
-- Single-user system, only one row allowed

CREATE TABLE IF NOT EXISTS cli_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    current_workspace_id INTEGER REFERENCES workspaces(id) ON DELETE SET NULL,
    current_session_id INTEGER REFERENCES chat_sessions(id) ON DELETE SET NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Insert default state row
INSERT INTO cli_state (id) VALUES (1) ON CONFLICT DO NOTHING;

-- Add updated_at trigger
CREATE TRIGGER update_cli_state_updated_at
BEFORE UPDATE ON cli_state
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
