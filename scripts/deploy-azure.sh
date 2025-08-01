#!/bin/bash
# Azure Container Apps Deployment Script for Xyra
# This script builds and deploys the Xyra application to Azure Container Apps
# with automatic database migration support

set -e  # Exit on any error

# Configuration
RESOURCE_GROUP="${RESOURCE_GROUP:-xyra-rg}"
CONTAINER_APP_NAME="${CONTAINER_APP_NAME:-xyra-app}"
CONTAINER_REGISTRY="${CONTAINER_REGISTRY:-xyraregistry.azurecr.io}"
IMAGE_NAME="${IMAGE_NAME:-xyra}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if logged into Azure
    if ! az account show &> /dev/null; then
        log_error "Not logged into Azure. Please run 'az login' first."
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker Desktop."
        exit 1
    fi
    
    log_info "Prerequisites check passed!"
}

# Build and push Docker image
build_and_push_image() {
    log_info "Building Docker image..."
    
    # Build the image
    docker build -t ${CONTAINER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG} .
    
    if [ $? -ne 0 ]; then
        log_error "Docker build failed"
        exit 1
    fi
    
    log_info "Docker image built successfully!"
    
    # Login to Azure Container Registry
    log_info "Logging into Azure Container Registry..."
    az acr login --name ${CONTAINER_REGISTRY%%.azurecr.io}
    
    # Push the image
    log_info "Pushing Docker image to registry..."
    docker push ${CONTAINER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
    
    if [ $? -ne 0 ]; then
        log_error "Docker push failed"
        exit 1
    fi
    
    log_info "Docker image pushed successfully!"
}

# Update Container App
update_container_app() {
    log_info "Updating Azure Container App..."
    
    # Update the container app with new image
    az containerapp update \
        --resource-group ${RESOURCE_GROUP} \
        --name ${CONTAINER_APP_NAME} \
        --image ${CONTAINER_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
    
    if [ $? -ne 0 ]; then
        log_error "Container App update failed"
        exit 1
    fi
    
    log_info "Container App updated successfully!"
}

# Check deployment status
check_deployment() {
    log_info "Checking deployment status..."
    
    # Wait a bit for the deployment to start
    sleep 10
    
    # Get the latest revision
    LATEST_REVISION=$(az containerapp revision list \
        --resource-group ${RESOURCE_GROUP} \
        --name ${CONTAINER_APP_NAME} \
        --query "[0].name" -o tsv)
    
    log_info "Latest revision: ${LATEST_REVISION}"
    
    # Check if revision is active
    REVISION_STATUS=$(az containerapp revision show \
        --resource-group ${RESOURCE_GROUP} \
        --name ${CONTAINER_APP_NAME} \
        --revision ${LATEST_REVISION} \
        --query "properties.provisioningState" -o tsv)
    
    log_info "Revision status: ${REVISION_STATUS}"
    
    # Get app URL
    APP_URL=$(az containerapp show \
        --resource-group ${RESOURCE_GROUP} \
        --name ${CONTAINER_APP_NAME} \
        --query "properties.configuration.ingress.fqdn" -o tsv)
    
    if [ ! -z "${APP_URL}" ]; then
        log_info "Application URL: https://${APP_URL}"
    fi
}

# View logs
view_logs() {
    log_info "Recent application logs:"
    az containerapp logs show \
        --resource-group ${RESOURCE_GROUP} \
        --name ${CONTAINER_APP_NAME} \
        --follow false \
        --tail 50
}

# Main deployment function
main() {
    log_info "Starting Azure Container Apps deployment for Xyra..."
    log_info "Configuration:"
    log_info "  Resource Group: ${RESOURCE_GROUP}"
    log_info "  Container App: ${CONTAINER_APP_NAME}"
    log_info "  Registry: ${CONTAINER_REGISTRY}"
    log_info "  Image: ${IMAGE_NAME}:${IMAGE_TAG}"
    echo ""
    
    # Step 1: Check prerequisites
    check_prerequisites
    echo ""
    
    # Step 2: Build and push image
    build_and_push_image
    echo ""
    
    # Step 3: Update container app
    update_container_app
    echo ""
    
    # Step 4: Check deployment
    check_deployment
    echo ""
    
    # Step 5: Show recent logs
    view_logs
    echo ""
    
    log_info "Deployment completed successfully!"
    log_info "The application should be running with the latest database schema."
    log_info "Database migrations are automatically run during container startup."
}

# Show usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Environment Variables:"
    echo "  RESOURCE_GROUP      Azure resource group (default: xyra-rg)"
    echo "  CONTAINER_APP_NAME  Container app name (default: xyra-app)"
    echo "  CONTAINER_REGISTRY  Container registry URL (default: xyraregistry.azurecr.io)"
    echo "  IMAGE_NAME          Docker image name (default: xyra)"
    echo "  IMAGE_TAG           Docker image tag (default: latest)"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Deploy with defaults"
    echo "  IMAGE_TAG=v1.2.3 $0                 # Deploy with specific tag"
    echo "  RESOURCE_GROUP=my-rg $0             # Deploy to different resource group"
    echo ""
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        usage
        exit 0
        ;;
    *)
        main
        ;;
esac
