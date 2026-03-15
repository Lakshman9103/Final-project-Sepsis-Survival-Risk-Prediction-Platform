#!/bin/bash

# AWS EC2 Setup Script for Sepsis Prediction App
# Run this on a fresh EC2 instance: bash setup.sh

set -e

echo "======================================"
echo "Sepsis Prediction App - AWS EC2 Setup"
echo "======================================"

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
echo "Installing Docker..."
sudo apt-get install -y docker.io docker-compose

# Enable Docker service
echo "Enabling Docker service..."
sudo systemctl enable docker
sudo systemctl start docker

# Add ubuntu user to docker group
echo "Adding ubuntu user to docker group..."
sudo usermod -aG docker ubuntu

# Install essential tools
echo "Installing essential tools..."
sudo apt-get install -y curl wget git htop

# Create app directory
echo "Creating app directory..."
mkdir -p /home/ubuntu/sepsis-app
cd /home/ubuntu/sepsis-app

# Display docker version
echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Docker version:"
docker --version
echo ""
echo "Docker Compose version:"
docker-compose --version
echo ""

echo "Next steps:"
echo "1. Upload your project files to /home/ubuntu/sepsis-app/"
echo "2. cd /home/ubuntu/sepsis-app"
echo "3. docker build -t sepsis-prediction:latest ."
echo "4. docker run -d --name sepsis-app -p 8501:8501 sepsis-prediction:latest"
echo ""
echo "Or use Docker Compose:"
echo "docker-compose up -d"
echo ""
echo "Access the app at: http://<your-ec2-public-ip>:8501"
echo ""

# Optional: Install Nginx for reverse proxy
read -p "Install Nginx for reverse proxy? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing Nginx..."
    sudo apt-get install -y nginx
    sudo systemctl enable nginx
    sudo systemctl start nginx
    echo "Nginx installed! Configure it in /etc/nginx/sites-available/sepsis"
fi

echo ""
echo "Setup complete! You can now upload your project."
