#!/bin/bash

# Database migration script for InsightHub
# Usage: ./migrate.sh [up|down] [migration_number]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Load environment variables from .env file
if [ -f "${PROJECT_ROOT}/.env" ]; then
    export $(grep -v '^#' "${PROJECT_ROOT}/.env" | grep -v '^[[:space:]]*$' | xargs)
fi

# Default values
MIGRATION_DIR="${SCRIPT_DIR}"
DATABASE_URL="${DATABASE_URL:-postgresql://insighthub:insighthub_dev@localhost:5432/insighthub}"

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
Database Migration Script for InsightHub

USAGE:
    ./migrate.sh [COMMAND] [MIGRATION_NUMBER]

COMMANDS:
    up [migration]      Apply database migrations
                        - Without migration number: applies all migrations in /up folder
                        - With migration number: applies specific migration (e.g., 001)

    down [migration]    Rollback database migrations
                        - Without migration number: rolls back all migrations in reverse order
                        - With migration number: rolls back specific migration (e.g., 006)

    status              Show migration status (not yet implemented)

    --help, -h          Show this help message

EXAMPLES:
    ./migrate.sh up                    Apply all pending migrations in numerical order
    ./migrate.sh up 001                Apply migration 001_*.sql only
    ./migrate.sh down                  Rollback all migrations in reverse order
    ./migrate.sh down 006              Rollback migration 006_*.sql only

MIGRATION FILES:
    Migrations are automatically discovered from the /up and /down directories.
    Files must follow the naming pattern: NNN_description.sql

    Example:
        migrations/up/001_initial_schema.sql
        migrations/up/002_add_users_table.sql
        migrations/down/001_initial_schema.sql
        migrations/down/002_add_users_table.sql

CONFIGURATION:
    Database connection is read from the .env file in the project root.

    Required variable:
        DATABASE_URL    PostgreSQL connection string
                        Format: postgresql://user:password@host:port/database
                        Example: postgresql://insighthub:insighthub_dev@localhost:5432/insighthub

    The script works with any PostgreSQL instance (Docker, localhost, remote)
    as long as the DATABASE_URL is correctly configured.

NOTES:
    - Migrations in /up are applied in ascending numerical order (001, 002, 003...)
    - Migrations in /down are applied in descending numerical order (006, 005, 004...)
    - The script requires psql (PostgreSQL client) to be installed
    - All migrations are executed with set -e (exit on first error)

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
        --help|-h)
            print_usage
            exit 0
            ;;
        *)
            MIGRATION="$1"
            shift
            ;;
    esac
done

# Default command - show help if no command provided
if [ -z "$COMMAND" ]; then
    print_usage
    exit 0
fi

# Execute SQL file
execute_sql() {
    local sql_file="$1"

    if [ ! -f "$sql_file" ]; then
        print_error "Migration file not found: $sql_file"
        exit 1
    fi

    print_info "Executing: $(basename $sql_file)"

    # Use psql with DATABASE_URL
    if ! command -v psql &> /dev/null; then
        print_error "psql not found. Install PostgreSQL client."
        exit 1
    fi

    psql "$DATABASE_URL" < "$sql_file"

    if [ $? -eq 0 ]; then
        print_success "✓ Migration executed successfully!"
    else
        print_error "Migration failed!"
        exit 1
    fi
}

# Get all migration files in numerical order
get_migration_files() {
    local direction="$1"
    local dir="${MIGRATION_DIR}/${direction}"

    if [ ! -d "$dir" ]; then
        print_error "Migration directory not found: $dir"
        exit 1
    fi

    # Find all .sql files and sort them numerically
    find "$dir" -maxdepth 1 -name "*.sql" -type f | sort
}

# Get all migration files in reverse numerical order
get_migration_files_reverse() {
    local direction="$1"
    local dir="${MIGRATION_DIR}/${direction}"

    if [ ! -d "$dir" ]; then
        print_error "Migration directory not found: $dir"
        exit 1
    fi

    # Find all .sql files and sort them in reverse numerical order
    find "$dir" -maxdepth 1 -name "*.sql" -type f | sort -r
}

# Apply migrations
migrate_up() {
    if [ -n "$MIGRATION" ]; then
        # Apply specific migration
        # Look for files starting with the migration number
        local migration_file=$(find "${MIGRATION_DIR}/up" -maxdepth 1 -name "${MIGRATION}*.sql" -type f | head -n 1)

        if [ -z "$migration_file" ]; then
            print_error "Migration file not found matching: $MIGRATION"
            exit 1
        fi

        print_info "Applying migration: $(basename $migration_file)"
        execute_sql "$migration_file"
    else
        # Apply all migrations in order
        print_info "Applying all migrations..."

        local migration_files=$(get_migration_files "up")

        if [ -z "$migration_files" ]; then
            print_info "No migration files found in ${MIGRATION_DIR}/up"
            exit 0
        fi

        while IFS= read -r migration_file; do
            execute_sql "$migration_file"
        done <<< "$migration_files"

        print_success "All migrations applied successfully!"
    fi
}

# Rollback migrations
migrate_down() {
    if [ -n "$MIGRATION" ]; then
        # Rollback specific migration
        # Look for files starting with the migration number
        local migration_file=$(find "${MIGRATION_DIR}/down" -maxdepth 1 -name "${MIGRATION}*.sql" -type f | head -n 1)

        if [ -z "$migration_file" ]; then
            print_error "Migration file not found matching: $MIGRATION"
            exit 1
        fi

        print_info "Rolling back migration: $(basename $migration_file)"
        execute_sql "$migration_file"
    else
        # Rollback all migrations in reverse order
        print_info "Rolling back all migrations..."

        local migration_files=$(get_migration_files_reverse "down")

        if [ -z "$migration_files" ]; then
            print_info "No migration files found in ${MIGRATION_DIR}/down"
            exit 0
        fi

        while IFS= read -r migration_file; do
            execute_sql "$migration_file"
        done <<< "$migration_files"

        print_success "All migrations rolled back successfully!"
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
