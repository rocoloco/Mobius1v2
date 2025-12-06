#!/bin/bash
# Supabase Setup Script for Mobius
# This script helps set up Supabase for production deployment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if Supabase CLI is installed
check_supabase_cli() {
    if command -v supabase &> /dev/null; then
        print_success "Supabase CLI is installed"
        return 0
    else
        print_warning "Supabase CLI is not installed"
        return 1
    fi
}

# Install Supabase CLI
install_supabase_cli() {
    print_info "Installing Supabase CLI..."
    
    if command -v npm &> /dev/null; then
        npm install -g supabase
        print_success "Supabase CLI installed via npm"
    elif command -v brew &> /dev/null; then
        brew install supabase/tap/supabase
        print_success "Supabase CLI installed via Homebrew"
    else
        print_error "Neither npm nor Homebrew found"
        print_info "Install manually: https://supabase.com/docs/guides/cli"
        exit 1
    fi
}

# Link to Supabase project
link_project() {
    print_info "Linking to Supabase project..."
    
    read -p "Enter your Supabase project ref (from project URL): " PROJECT_REF
    
    supabase link --project-ref "$PROJECT_REF"
    
    print_success "Linked to project: $PROJECT_REF"
}

# Run migrations
run_migrations() {
    print_info "Running database migrations..."
    
    if [ -d "supabase/migrations" ]; then
        supabase db push
        print_success "Migrations applied successfully"
    else
        print_error "Migrations directory not found"
        exit 1
    fi
}

# Create storage buckets
create_buckets() {
    print_info "Storage buckets should be created manually in Supabase dashboard"
    print_info "Go to: Storage → Create bucket"
    print_info ""
    print_info "Create the following buckets:"
    print_info "  1. brands (50MB max, public)"
    print_info "  2. assets (10MB max, public)"
    print_info ""
    
    read -p "Press Enter when buckets are created..."
}

# Get connection details
get_connection_details() {
    print_header "Connection Details"
    
    print_info "Get these from your Supabase dashboard:"
    print_info ""
    print_info "1. Pooler URL (Settings → Database → Connection Pooling)"
    print_info "   Format: postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres"
    print_info ""
    print_info "2. Project URL (Settings → API)"
    print_info "   Format: https://[ref].supabase.co"
    print_info ""
    print_info "3. Anon/Public Key (Settings → API)"
    print_info ""
    
    read -p "Press Enter to continue..."
}

# Verify setup
verify_setup() {
    print_info "Verifying Supabase setup..."
    
    # Check if migrations were applied
    print_info "Checking database tables..."
    
    # This would require database connection, so we'll just provide instructions
    print_info "Verify in Supabase dashboard:"
    print_info "  1. Database → Tables should show: brands, assets, jobs, templates, feedback, etc."
    print_info "  2. Storage → Buckets should show: brands, assets"
    print_info ""
    
    read -p "Are all tables and buckets created? (y/N): " VERIFIED
    
    if [ "$VERIFIED" = "y" ] || [ "$VERIFIED" = "Y" ]; then
        print_success "Supabase setup verified"
        return 0
    else
        print_warning "Please verify setup manually"
        return 1
    fi
}

# Main workflow
main() {
    print_header "Mobius Supabase Setup"
    
    # Step 1: Check/Install Supabase CLI
    print_header "Step 1: Supabase CLI"
    
    if ! check_supabase_cli; then
        read -p "Install Supabase CLI now? (Y/n): " INSTALL
        if [ "$INSTALL" != "n" ] && [ "$INSTALL" != "N" ]; then
            install_supabase_cli
        else
            print_info "Please install Supabase CLI manually"
            exit 0
        fi
    fi
    
    # Step 2: Link project
    print_header "Step 2: Link to Supabase Project"
    
    print_info "Make sure you have:"
    print_info "  1. Created a Supabase project at https://supabase.com"
    print_info "  2. Have your project ref ready (from project URL)"
    print_info ""
    
    read -p "Ready to link? (Y/n): " READY
    if [ "$READY" != "n" ] && [ "$READY" != "N" ]; then
        link_project
    else
        print_info "Link manually with: supabase link --project-ref YOUR_REF"
        exit 0
    fi
    
    # Step 3: Run migrations
    print_header "Step 3: Run Database Migrations"
    
    read -p "Run migrations now? (Y/n): " RUN_MIGRATIONS
    if [ "$RUN_MIGRATIONS" != "n" ] && [ "$RUN_MIGRATIONS" != "N" ]; then
        run_migrations
    else
        print_info "Run migrations manually with: supabase db push"
    fi
    
    # Step 4: Create storage buckets
    print_header "Step 4: Create Storage Buckets"
    create_buckets
    
    # Step 5: Get connection details
    get_connection_details
    
    # Step 6: Verify
    print_header "Step 5: Verification"
    verify_setup
    
    # Success
    print_header "Setup Complete"
    print_success "Supabase is configured and ready"
    
    print_info "\nNext steps:"
    print_info "  1. Save your connection details securely"
    print_info "  2. Set up Modal secrets with Supabase credentials"
    print_info "  3. Deploy to Modal: python scripts/deploy.py"
    
    echo -e "\n${GREEN}🚀 Ready to deploy!${NC}\n"
}

# Run main
main
