#!/bin/bash

# HTML Text Formatter Pro - Production Deployment Script
# Comprehensive deployment with health checks and rollback capability

set -e

# Configuration
APP_NAME="html-formatter-pro"
DOCKER_IMAGE="ghcr.io/your-org/html-formatter-pro"
ENVIRONMENT="${ENVIRONMENT:-production}"
VERSION="${VERSION:-latest}"
HEALTH_CHECK_TIMEOUT=60
ROLLBACK_ENABLED="${ROLLBACK_ENABLED:-true}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Error handling
handle_error() {
    log_error "Deployment failed at line $1"
    if [ "$ROLLBACK_ENABLED" = "true" ]; then
        log_warning "Initiating rollback..."
        rollback_deployment
    fi
    exit 1
}

trap 'handle_error $LINENO' ERR

# Helper functions
check_dependencies() {
    log_info "Checking deployment dependencies..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    # Check curl for health checks
    if ! command -v curl &> /dev/null; then
        log_error "curl is not installed or not in PATH"
        exit 1
    fi
    
    log_success "All dependencies are available"
}

backup_current_deployment() {
    log_info "Creating backup of current deployment..."
    
    if docker ps --format "table {{.Names}}" | grep -q "$APP_NAME"; then
        # Create backup of current container
        BACKUP_NAME="${APP_NAME}-backup-$(date +%Y%m%d-%H%M%S)"
        docker commit "$APP_NAME" "$BACKUP_NAME" || true
        
        # Save current environment variables
        docker inspect "$APP_NAME" --format='{{range .Config.Env}}{{println .}}{{end}}' > .env.backup || true
        
        log_success "Backup created: $BACKUP_NAME"
        echo "$BACKUP_NAME" > .last_backup
    else
        log_warning "No existing deployment found to backup"
    fi
}

pre_deployment_checks() {
    log_info "Running pre-deployment checks..."
    
    # Check disk space
    AVAILABLE_SPACE=$(df / | awk 'NR==2 {print $4}')
    REQUIRED_SPACE=1048576  # 1GB in KB
    
    if [ "$AVAILABLE_SPACE" -lt "$REQUIRED_SPACE" ]; then
        log_error "Insufficient disk space. Available: ${AVAILABLE_SPACE}KB, Required: ${REQUIRED_SPACE}KB"
        exit 1
    fi
    
    # Check if image exists
    if ! docker manifest inspect "$DOCKER_IMAGE:$VERSION" &> /dev/null; then
        log_error "Docker image $DOCKER_IMAGE:$VERSION not found"
        exit 1
    fi
    
    # Validate environment configuration
    if [ ! -f ".env.${ENVIRONMENT}" ] && [ ! -f ".env" ]; then
        log_error "Environment configuration file not found"
        exit 1
    fi
    
    log_success "Pre-deployment checks passed"
}

pull_images() {
    log_info "Pulling latest Docker images..."
    
    docker-compose -f docker-compose.yml pull
    
    log_success "Images pulled successfully"
}

deploy_application() {
    log_info "Deploying application..."
    
    # Set environment file
    ENV_FILE=".env"
    if [ -f ".env.${ENVIRONMENT}" ]; then
        ENV_FILE=".env.${ENVIRONMENT}"
    fi
    
    # Deploy with Docker Compose
    docker-compose \
        -f docker-compose.yml \
        --env-file "$ENV_FILE" \
        up -d --remove-orphans
    
    log_success "Application deployed"
}

wait_for_health() {
    log_info "Waiting for application to be healthy..."
    
    local attempts=0
    local max_attempts=$((HEALTH_CHECK_TIMEOUT / 5))
    
    while [ $attempts -lt $max_attempts ]; do
        if curl -f http://localhost:8501/_stcore/health &> /dev/null; then
            log_success "Application is healthy"
            return 0
        fi
        
        attempts=$((attempts + 1))
        log_info "Health check attempt $attempts/$max_attempts..."
        sleep 5
    done
    
    log_error "Application failed to become healthy within $HEALTH_CHECK_TIMEOUT seconds"
    return 1
}

run_smoke_tests() {
    log_info "Running smoke tests..."
    
    # Test main endpoint
    if ! curl -f http://localhost:8501 &> /dev/null; then
        log_error "Main endpoint is not responding"
        return 1
    fi
    
    # Test health endpoint
    if ! curl -f http://localhost:8501/_stcore/health &> /dev/null; then
        log_error "Health endpoint is not responding"
        return 1
    fi
    
    # Test with sample request (if API endpoints exist)
    # Add more specific tests here based on your application
    
    log_success "Smoke tests passed"
}

rollback_deployment() {
    log_warning "Rolling back deployment..."
    
    if [ -f ".last_backup" ]; then
        BACKUP_NAME=$(cat .last_backup)
        
        # Stop current containers
        docker-compose -f docker-compose.yml down || true
        
        # Restore from backup
        docker tag "$BACKUP_NAME" "$APP_NAME:rollback"
        
        # Start with backup image
        # This is a simplified rollback - adjust based on your needs
        docker run -d --name "$APP_NAME" -p 8501:8501 "$APP_NAME:rollback"
        
        log_success "Rollback completed"
    else
        log_error "No backup found for rollback"
    fi
}

cleanup_old_images() {
    log_info "Cleaning up old Docker images..."
    
    # Remove unused images
    docker image prune -f || true
    
    # Remove old backups (keep last 3)
    docker images --format "table {{.Repository}}\t{{.Tag}}" | \
        grep "$APP_NAME-backup" | \
        tail -n +4 | \
        awk '{print $1":"$2}' | \
        xargs -r docker rmi || true
    
    log_success "Cleanup completed"
}

post_deployment_tasks() {
    log_info "Running post-deployment tasks..."
    
    # Update monitoring configuration
    # Add any post-deployment scripts here
    
    # Send deployment notification
    if [ -n "$SLACK_WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"✅ $APP_NAME deployed successfully to $ENVIRONMENT (version: $VERSION)\"}" \
            "$SLACK_WEBHOOK_URL" || true
    fi
    
    log_success "Post-deployment tasks completed"
}

# Main deployment flow
main() {
    log_info "Starting deployment of $APP_NAME version $VERSION to $ENVIRONMENT"
    
    check_dependencies
    backup_current_deployment
    pre_deployment_checks
    pull_images
    deploy_application
    
    if wait_for_health && run_smoke_tests; then
        cleanup_old_images
        post_deployment_tasks
        log_success "Deployment completed successfully!"
    else
        log_error "Deployment validation failed"
        if [ "$ROLLBACK_ENABLED" = "true" ]; then
            rollback_deployment
        fi
        exit 1
    fi
}

# Command line options
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "rollback")
        rollback_deployment
        ;;
    "health")
        curl -f http://localhost:8501/_stcore/health && echo "✅ Healthy" || echo "❌ Unhealthy"
        ;;
    "logs")
        docker-compose -f docker-compose.yml logs -f
        ;;
    "stop")
        log_info "Stopping application..."
        docker-compose -f docker-compose.yml down
        log_success "Application stopped"
        ;;
    "restart")
        log_info "Restarting application..."
        docker-compose -f docker-compose.yml restart
        log_success "Application restarted"
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|health|logs|stop|restart}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Deploy the application (default)"
        echo "  rollback - Rollback to previous version"
        echo "  health   - Check application health"
        echo "  logs     - Show application logs"
        echo "  stop     - Stop the application"
        echo "  restart  - Restart the application"
        exit 1
        ;;
esac