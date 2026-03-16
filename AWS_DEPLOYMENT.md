# AWS Deployment Guide - Sepsis Prediction App

## Step 1: Push Code to GitHub

```bash
# Initialize git repo locally
git init
git add .
git commit -m "Initial commit - Sepsis prediction app"

# Create new repo on GitHub (https://github.com/new)
# Then push:
git remote add origin https://github.com/YOUR-USERNAME/sepsis-prediction.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy on AWS EC2

### 2.1: Launch EC2 Instance
1. Go to [AWS Console](https://console.aws.amazon.com/)
2. Click **EC2 > Instances > Launch Instances**
3. Choose **Ubuntu Server 22.04 LTS** (free tier eligible)
4. Instance Type: **t2.micro** (free tier)
5. Configure Security Group:
   - Add Inbound Rule: **Port 8501** from **0.0.0.0/0**
   - Keep SSH (Port 22) open
6. Create/Select key pair and download `.pem` file
7. Launch instance

### 2.2: Connect to Instance
```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### 2.3: Install Docker
```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y docker.io
sudo usermod -aG docker ubuntu

# Exit and reconnect SSH
exit
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### 2.4: Clone and Deploy
```bash
# Clone from GitHub
git clone https://github.com/YOUR-USERNAME/sepsis-prediction.git sepsis-app
cd sepsis-app

# Build Docker image
docker build -t sepsis-prediction:latest .

# Run container
docker run -d --name sepsis-app -p 8501:8501 sepsis-prediction:latest

# Check if running
docker logs sepsis-app
```

### 2.5: Access Your App
Open browser and go to:
```
http://your-ec2-public-ip:8501
```

---

## Quick Commands

**View logs:**
```bash
docker logs sepsis-app
```

**Stop/Restart container:**
```bash
docker stop sepsis-app
docker start sepsis-app
```

**Update app (pull latest from GitHub):**
```bash
cd sepsis-app
git pull origin main
docker build -t sepsis-prediction:latest .
docker stop sepsis-app
docker rm sepsis-app
docker run -d --name sepsis-app -p 8501:8501 sepsis-prediction:latest
```

---

## Troubleshooting

**Container exits immediately:**
```bash
docker logs sepsis-app
```

**Can't access from browser:**
- Check Security Group allows port 8501
- Check container is running: `docker ps`
- Try: `http://your-ec2-public-ip:8501` (not https)

**Port already in use:**
```bash
docker run -d --name sepsis-app -p 8502:8501 sepsis-prediction:latest
```
