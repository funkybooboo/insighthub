#!/bin/bash

# Database migration script for InsightHub
# Usage: ./migrate.sh [up|down] [migration_number] [--docker]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Default values
MIGRATION_DIR="${SCRIPT_DIR}"
USE_DOCKER=false
DB_USER="${POSTGRES_USER:-insighthub}"
DB_NAME="${POSTGRES_DB:-insighthub}"
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
print_error() {
    echo -e "${RED}Error: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_info() {
    echo -e "${YELLOW}$1${NC}"
}

print_usage() {
    cat << EOF
Usage: ./migrate.sh [COMMAND] [OPTIONS]

Commands:
  up [migration]     Apply migration (default: all pending migrations)
  down [migration]   Rollback migration (default: latest migration)
  status             Show migration status (not implemented)

Options:
  --docker           Use Docker container for PostgreSQL
  --help             Show this help message

Examples:
  ./migrate.sh up                              # Apply all migrations locally
  ./migrate.sh up 001_initial_schema.sql       # Apply specific migration locally
  ./migrate.sh down                            # Rollback all migrations locally
  ./migrate.sh down 006_add_cli_state_table.sql  # Rollback specific migration locally
  ./migrate.sh up --docker                     # Apply migrations in Docker
  ./migrate.sh down --docker                   # Rollback migrations in Docker

Environment Variables:
  POSTGRES_USER      PostgreSQL user (default: insighthub)
  POSTGRES_DB        PostgreSQL database (default: insighthub)
  POSTGRES_HOST      PostgreSQL host (default: localhost)
  POSTGRES_PORT      PostgreSQL port (default: 5432)

EOF
}

# Parse arguments
COMMAND=""
MIGRATION=""

while [[ $# -gt 0 ]]; do
    case $1 in
        up|down|status)
            COMMAND="$1"
            shift
            ;;
        --docker)
            USE_DOCKER=true
            shift
            ;;
        --help|-h)
            print_usage
            exit 0
            ;;
        [0-9]*)
            MIGRATION="$1"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            print_usage
            exit 1
            ;;
    esac
done

# Default command
if [ -z "$COMMAND" ]; then
    COMMAND="up"
fi

# Execute SQL file
execute_sql() {
    local sql_file="$1"

    if [ ! -f "$sql_file" ]; then
        print_error "Migration file not found: $sql_file"
        exit 1
    fi

    print_info "Executing: $sql_file"

    if [ "$USE_DOCKER" = true ]; then
        # Use Docker container
        docker compose -f "${PROJECT_ROOT}/docker-compose.yml" exec -T postgres \
            psql -U "$DB_USER" -d "$DB_NAME" < "$sql_file"
    else
        # Use local psql
        if ! command -v psql &> /dev/null; then
            print_error "psql not found. Install PostgreSQL client or use --docker flag."
            exit 1
        fi

        PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" < "$sql_file"
    fi

    if [ $? -eq 0 ]; then
        print_success "Migration executed successfully!"
    else
        print_error "Migration failed!"
        exit 1
    fi
}

# Apply migrations
migrate_up() {
    if [ -n "$MIGRATION" ]; then
        # Apply specific migration
        local migration_file="${MIGRATION_DIR}/up/${MIGRATION}"
        if [ ! -f "$migration_file" ]; then
            migration_file="${MIGRATION_DIR}/up/${MIGRATION}.sql"
        fi

        if [ ! -f "$migration_file" ]; then
            print_error "Migration file not found: $MIGRATION"
            exit 1
        fi

        print_info "Applying migration: $MIGRATION"
        execute_sql "$migration_file"
    else
        # Apply all migrations in order
        print_info "Applying all migrations..."

        local migration_files=(
            "${MIGRATION_DIR}/up/001_initial_schema.sql"
            "${MIGRATION_DIR}/up/002_add_rag_type_to_default_config.sql"
            "${MIGRATION_DIR}/up/003_remove_user_id_from_workspaces.sql"
            "${MIGRATION_DIR}/up/004_add_chunk_count_to_documents.sql"
            "${MIGRATION_DIR}/up/005_fix_chat_sessions_schema.sql"
            "${MIGRATION_DIR}/up/006_add_cli_state_table.sql"
        )

        for migration_file in "${migration_files[@]}"; do
            if [ -f "$migration_file" ]; then
                execute_sql "$migration_file"
            else
                print_error "Migration file not found: $migration_file"
                exit 1
            fi
        done
    fi
}

# Rollback migrations
migrate_down() {
    if [ -n "$MIGRATION" ]; then
        # Rollback specific migration
        local migration_file="${MIGRATION_DIR}/down/${MIGRATION}"
        if [ ! -f "$migration_file" ]; then
            migration_file="${MIGRATION_DIR}/down/${MIGRATION}.sql"
        fi

        if [ ! -f "$migration_file" ]; then
            print_error "Migration file not found: $MIGRATION"
            exit 1
        fi

        print_info "Rolling back migration: $MIGRATION"
        execute_sql "$migration_file"
    else
        # Rollback all migrations in reverse order
        print_info "Rolling back all migrations..."

        local migration_files=(
            "${MIGRATION_DIR}/down/006_add_cli_state_table.sql"
            "${MIGRATION_DIR}/down/005_fix_chat_sessions_schema.sql"
            "${MIGRATION_DIR}/down/004_add_chunk_count_to_documents.sql"
            "${MIGRATION_DIR}/down/003_remove_user_id_from_workspaces.sql"
            "${MIGRATION_DIR}/down/002_add_rag_type_to_default_config.sql"
            "${MIGRATION_DIR}/down/001_initial_schema.sql"
        )

        for migration_file in "${migration_files[@]}"; do
            if [ -f "$migration_file" ]; then
                execute_sql "$migration_file"
            else
                print_error "Migration file not found: $migration_file"
                exit 1
            fi
        done
    fi
}

# Show migration status
migration_status() {
    print_info "Migration status check not implemented yet."
    print_info "Check the database manually to see which tables exist."
}

# Main execution
case $COMMAND in
    up)
        migrate_up
        ;;
    down)
        migrate_down
        ;;
    status)
        migration_status
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        print_usage
        exit 1
        ;;
esac
