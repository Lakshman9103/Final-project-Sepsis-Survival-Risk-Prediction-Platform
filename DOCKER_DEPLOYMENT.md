# Docker & AWS EC2 Deployment Guide

## 📦 Docker Setup

### Files Created

1. **Dockerfile** - Container image definition
2. **.dockerignore** - Files to exclude from image
3. **.streamlit/config.toml** - Streamlit configuration
4. **docker-compose.yml** - Docker Compose for local testing

---

## 🏗️ Building the Docker Image

### Option 1: Using Docker CLI

```bash
# Navigate to project directory
cd "c:\Users\laksh\Projects\Final project Sepsis Survival & Risk Prediction Platform"

# Build the image
docker build -t sepsis-prediction:latest .

# Test locally
docker run -p 8501:8501 sepsis-prediction:latest
```

Visit: `http://localhost:8501`

---

### Option 2: Using Docker Compose

```bash
# Build and run
docker-compose up --build

# Stop
docker-compose down
```

---

## ☁️ AWS EC2 Deployment

### Step 1: Launch EC2 Instance

1. **AWS Console** → EC2 → Launch Instances
2. **AMI**: Ubuntu 22.04 LTS (free tier eligible)
3. **Instance Type**: `t2.micro` (free tier) or `t3.small` (1 vCPU, 2GB RAM recommended)
4. **Storage**: 20 GB (default is fine)
5. **Security Groups**: 
   - Allow SSH (port 22) from your IP
   - Allow HTTP (port 80) for Streamlit port forwarding
   - Allow HTTPS (port 443) if using SSL
   - Allow port 8501 for direct Streamlit access

6. **Key Pair**: Create or select a key pair (.pem file)

### Step 2: Connect to EC2 Instance

```bash
# Make key private (Windows)
icacls your-key.pem /inheritance:r /grant:r "%username%:F"

# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### Step 3: Install Docker on EC2

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
sudo apt-get install -y docker.io

# Install Docker Compose
sudo apt-get install -y docker-compose

# Add ubuntu user to docker group (avoid sudo)
sudo usermod -aG docker ubuntu

# Log out and back in for group changes to take effect
exit
# SSH back in
```

### Step 4: Clone/Transfer Project

**Option A: Clone from Git** (if you have a Git repo)

```bash
cd /home/ubuntu
git clone <your-repo-url> sepsis-app
cd sepsis-app
```

**Option B: Upload files directly**

```bash
# From your local machine
scp -i your-key.pem -r "path/to/project/*" ubuntu@your-ec2-ip:/home/ubuntu/sepsis-app/
```

### Step 5: Build and Run Docker Container

```bash
cd ~/sepsis-app

# Build the image
docker build -t sepsis-prediction:latest .

# Run the container
docker run -d \
  --name sepsis-app \
  -p 8501:8501 \
  --restart unless-stopped \
  sepsis-prediction:latest

# Check if running
docker ps

# View logs
docker logs -f sepsis-app
```

### Step 6: Access the App

Visit: `http://your-ec2-public-ip:8501`

---

## 🔐 Production Deployment with Nginx Reverse Proxy

### Step 1: Install Nginx

```bash
sudo apt-get install -y nginx

# Enable Nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### Step 2: Configure Nginx

Create `/etc/nginx/sites-available/sepsis`:

```bash
sudo nano /etc/nginx/sites-available/sepsis
```

Add this config:

```nginx
upstream streamlit {
    server localhost:8501;
}

server {
    listen 80;
    server_name your-domain.com;  # Or your EC2 public IP

    location / {
        proxy_pass http://streamlit;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/sepsis /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

Now access via: `http://your-ec2-ip/` (port 80)

---

## 🔒 SSL/HTTPS Setup (Optional but Recommended)

### Using Let's Encrypt

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com
```

---

## 📊 Docker Container Management

### Useful Commands

```bash
# View running containers
docker ps

# View logs
docker logs sepsis-app
docker logs -f sepsis-app  # Follow logs

# Stop container
docker stop sepsis-app

# Start container
docker start sepsis-app

# Remove container
docker rm sepsis-app

# Remove image
docker rmi sepsis-prediction:latest

# Container stats
docker stats
```

---

## 🚀 Using Docker Compose on EC2

```bash
# Upload docker-compose.yml to EC2
# Then run:

docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f sepsis-app

# Stop
docker-compose down
```

---

## 📈 Performance Optimization

### Increase Resources

For better performance, modify docker-compose.yml:

```yaml
services:
  sepsis-app:
    # ... rest of config
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

### Create EC2 with More Resources

For production:
- **Instance Type**: `t3.medium` or `t3.large`
- **RAM**: 4GB minimum (2GB Streamlit + 2GB buffer)
- **vCPU**: 2 minimum

---

## 🔄 CI/CD Pipeline (GitHub Actions)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS EC2

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Build Docker image
        run: |
          docker build -t sepsis-prediction:latest .
      
      - name: Push to Docker Hub
        env:
          DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
          DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
        run: |
          echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
          docker tag sepsis-prediction:latest $DOCKER_USERNAME/sepsis-prediction:latest
          docker push $DOCKER_USERNAME/sepsis-prediction:latest
      
      - name: Deploy to EC2
        env:
          EC2_IP: ${{ secrets.EC2_IP }}
          EC2_KEY: ${{ secrets.EC2_KEY }}
        run: |
          mkdir -p ~/.ssh
          echo "$EC2_KEY" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh -o StrictHostKeyChecking=no ubuntu@$EC2_IP << 'EOF'
            cd ~/sepsis-app
            docker pull ${{ secrets.DOCKER_USERNAME }}/sepsis-prediction:latest
            docker stop sepsis-app || true
            docker rm sepsis-app || true
            docker run -d --name sepsis-app -p 8501:8501 --restart unless-stopped ${{ secrets.DOCKER_USERNAME }}/sepsis-prediction:latest
          EOF
```

---

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find process using port 8501
sudo lsof -i :8501

# Kill the process
sudo kill -9 <PID>
```

### Container Not Starting

```bash
# Check logs
docker logs sepsis-app

# Run interactive mode for debugging
docker run -it sepsis-prediction:latest bash
```

### Out of Memory

```bash
# Free up space
docker system prune -a

# Check space usage
docker system df
```

### Model Loading Issues

Ensure models are mounted/copied correctly:

```bash
# Check if files exist in container
docker exec sepsis-app ls -la /app/models/
```

---

## 📝 Monitoring & Maintenance

### Set up CloudWatch Monitoring

1. **IAM Role**: Attach EC2 CloudWatch policy
2. **CloudWatch Agent**: Install on EC2
3. **Create Alarms**: Monitor CPU, memory, disk

### Log Rotation

Add to `/etc/docker/daemon.json`:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

---

## ✅ Deployment Checklist

- [ ] Docker image builds successfully
- [ ] App runs locally with `docker-compose up`
- [ ] EC2 instance is running
- [ ] Docker is installed on EC2
- [ ] Project files uploaded to EC2
- [ ] Container starts and stays running
- [ ] App accessible via public IP:8501
- [ ] Nginx configured (optional)
- [ ] SSL certificate installed (optional)
- [ ] Security groups allow necessary ports
- [ ] CloudWatch monitoring set up (optional)
- [ ] Auto-restart configured

---

## 📞 Support & References

- **Docker Docs**: https://docs.docker.com/
- **AWS EC2 Docs**: https://docs.aws.amazon.com/ec2/
- **Streamlit Docs**: https://docs.streamlit.io/
- **Nginx Docs**: https://nginx.org/en/docs/

---

**Last Updated**: March 15, 2026  
**Status**: ✅ Ready for Production
