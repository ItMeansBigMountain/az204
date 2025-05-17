#!/bin/bash

# Exit on any error
set -e

# Store the root directory
ROOT_DIR=$(pwd)
SUCCESS=true

# Find all main.tf files and process their directories
find . -name "main.tf" | while read -r tf_file; do
    # Get the directory containing the main.tf file
    tf_dir=$(dirname "$tf_file")
    echo "📁 Processing Terraform in: $tf_dir"
    
    # Change to the terraform directory
    cd "$tf_dir"
    
    # Initialize and apply Terraform
    echo "🔧 Initializing Terraform..."
    terraform init
    
    echo "🚀 Applying Terraform changes..."
    terraform apply -auto-approve
    
    # Check if terraform apply was successful
    if [ $? -ne 0 ]; then
        echo "❌ Terraform apply failed in $tf_dir"
        SUCCESS=false
        break
    fi
    
    # Return to root directory
    cd "$ROOT_DIR"
done

# If all terraform applies were successful, push to GitHub
if [ "$SUCCESS" = true ]; then
    echo "✅ All Terraform applies successful, pushing to GitHub..."
    git add .
    git commit -m "Infrastructure: Automated terraform apply across all directories"
    git push
    echo "🎉 Deploy complete!"
else
    echo "❌ Deploy failed! Check the errors above."
    exit 1
fi