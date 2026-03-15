# AWS EC2 Deployment - Quick Start

## 🚀 Quick Deployment (5 Steps)

### Step 1: Launch EC2

```
AWS Console → EC2 → Launch Instance
- AMI: Ubuntu 22.04 LTS
- Instance: t2.micro (free tier) or t3.small
- Storage: 20GB
- Security Group: Allow ports 22, 80, 443, 8501
- Key Pair: Download .pem file
```

### Step 2: Connect to Instance

```bash
ssh -i your-key.pem ubuntu@<your-public-ip>
```

### Step 3: Setup Docker (Run Once)

```bash
# Download and run setup script
curl -O https://raw.githubusercontent.com/your-repo/setup.sh
bash setup.sh
```

Or manually:
```bash
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker ubuntu
# Log out and back in
exit
```

### Step 4: Deploy App

```bash
# Upload files (from your machine)
scp -i your-key.pem -r ./* ubuntu@<your-ip>:/home/ubuntu/sepsis-app/

# SSH back in
ssh -i your-key.pem ubuntu@<your-public-ip>

# Build and run
cd ~/sepsis-app
docker build -t sepsis-prediction:latest .
docker run -d --name sepsis-app -p 8501:8501 --restart unless-stopped sepsis-prediction:latest
```

### Step 5: Access App

Open browser: `http://your-ec2-public-ip:8501`

---

## 📊 Recommended Configurations

### Development/Testing
- Instance: `t2.micro`
- vCPU: 1
- RAM: 1GB
- Storage: 10GB
- Cost: Free tier eligible

### Production
- Instance: `t3.small` or `t3.medium`
- vCPU: 2
- RAM: 4GB
- Storage: 50GB
- Cost: $10-20/month

### High Traffic
- Instance: `t3.large` or larger
- vCPU: 4+
- RAM: 8GB+
- Using Load Balancer
- Using RDS (if needed)

---

## 🔧 Common Docker Commands

```bash
# View running containers
docker ps

# View all containers
docker ps -a

# View logs
docker logs sepsis-app
docker logs -f sepsis-app  # Follow

# Stop/Start/Restart
docker stop sepsis-app
docker start sepsis-app
docker restart sepsis-app

# Remove container
docker rm sepsis-app

# View resource usage
docker stats
```

---

## 🐳 Docker Compose Commands

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all
docker-compose down

# Rebuild image
docker-compose up -d --build

# View services
docker-compose ps
```

---

## 🌐 Using Nginx as Reverse Proxy

### Config Example

```bash
# Edit nginx config
sudo nano /etc/nginx/sites-available/sepsis
```

```nginx
upstream streamlit {
    server localhost:8501;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://streamlit;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/sepsis /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

---

## 🔐 SSL with Let's Encrypt

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 📈 Monitoring & Health Checks

### Check Container Status

```bash
# Detailed info
docker inspect sepsis-app

# Health check
curl http://localhost:8501/_stcore/health
```

### Monitor Resources

```bash
# Real-time stats
docker stats sepsis-app

# View logs for errors
docker logs sepsis-app | grep -i error
```

---

## 🚨 Troubleshooting

### Container crashes
```bash
docker logs sepsis-app
# Check for missing dependencies or model files
```

### Port 8501 in use
```bash
sudo lsof -i :8501
sudo kill -9 <PID>
```

### Out of disk space
```bash
docker system prune -a  # Remove unused images/containers
df -h  # Check disk usage
```

### Model not found
```bash
docker exec sepsis-app ls -la /app/models/
# Ensure models directory is mounted/copied
```

---

## 💰 Cost Optimization

### AWS Free Tier
- 12 months free for:
  - t2.micro instance (750 hours/month)
  - 30 GB storage
  - Data transfer

**Recommendation**: Use t2.micro for testing, then upgrade for production

### Cost Estimation

| Instance | vCPU | RAM | Price/Month |
|----------|------|-----|------------|
| t2.micro | 1    | 1GB | Free       |
| t2.small | 1    | 2GB | $10-12     |
| t3.small | 2    | 2GB | $15-18     |
| t3.medium| 2    | 4GB | $25-30     |

---

## 📋 Pre-deployment Checklist

- [ ] Dockerfile created and tested locally
- [ ] All dependencies in Requirements.txt
- [ ] Model files present in `/models`
- [ ] EC2 key pair downloaded and secured
- [ ] Security groups configured
- [ ] DNS/Domain set up (optional)
- [ ] SSL certificate ready (optional)
- [ ] Monitoring alerts configured (optional)

---

## 🔗 Useful Links

- [AWS EC2 Launch Wizard](https://console.aws.amazon.com/ec2/)
- [AWS Security Groups](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html)
- [Docker Documentation](https://docs.docker.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

## 📞 Support Resources

1. **AWS Support**: AWS Console → Support → Create case
2. **Docker Community**: Docker Community Forums
3. **Streamlit Community**: Streamlit Community Forum
4. **Stack Overflow**: Tag questions with `docker`, `aws-ec2`, `streamlit`

---

**Last Updated**: March 15, 2026  
**Status**: ✅ Production Ready
