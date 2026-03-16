# AWS Deployment Guide - Sepsis Prediction App

## Option 1: Deploy Directly from GitHub (CI/CD with GitHub Actions)

### Step 1: Push Code to GitHub
```bash
# Initialize git repo locally (if not already done)
git init
git add .
git commit -m "Initial commit - Sepsis prediction app"

# Create new repo on GitHub (https://github.com/new)
# Then push:
git remote add origin https://github.com/YOUR-USERNAME/sepsis-prediction.git
git branch -M main
git push -u origin main
```

### Step 2: Create GitHub Secrets
1. Go to **GitHub** → Your Repo → **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:
   - `AWS_ACCESS_KEY_ID` - Your AWS access key
   - `AWS_SECRET_ACCESS_KEY` - Your AWS secret key
   - `AWS_REGION` - Your AWS region (e.g., `us-east-1`)
   - `EC2_HOST` - Your EC2 public IP address
   - `EC2_USER` - `ubuntu`
   - `EC2_KEY` - Your EC2 private key (.pem file content)

### Step 3: Create GitHub Actions Workflow
Create file: `.github/workflows/deploy.yml`

```yaml
name: Deploy to AWS EC2

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to EC2
      env:
        PRIVATE_KEY: ${{ secrets.EC2_KEY }}
        HOSTNAME: ${{ secrets.EC2_HOST }}
        USER_NAME: ${{ secrets.EC2_USER }}
      run: |
        mkdir -p ~/.ssh
        echo "$PRIVATE_KEY" > ~/.ssh/private_key
        chmod 600 ~/.ssh/private_key
        ssh-keyscan -H $HOSTNAME >> ~/.ssh/known_hosts
        
        ssh -i ~/.ssh/private_key ${USER_NAME}@${HOSTNAME} << 'EOF'
          cd ~/sepsis-app
          git pull origin main
          docker build -t sepsis-prediction:latest .
          docker stop sepsis-app || true
          docker rm sepsis-app || true
          docker run -d --name sepsis-app -p 8501:8501 sepsis-prediction:latest
        EOF
```

### Step 4: Set Up EC2 (One-time)
Follow the manual deployment steps below (Step 3-4 only), then just push to GitHub - it auto-deploys!

---

## Option 2: Quick Manual Deploy on AWS EC2

### Step 1: Launch EC2 Instance
1. Go to [AWS Console](https://console.aws.amazon.com/)
2. Click **EC2 > Instances > Launch Instances**
3. Choose **Ubuntu Server 22.04 LTS** (free tier eligible)
4. Instance Type: **t2.micro** (free tier) or **t2.small** ($10/month)
5. Configure Security Group:
   - Add Inbound Rule: **Port 8501** from **0.0.0.0/0** (Anywhere)
   - Keep SSH (Port 22) open
6. Create/Select key pair and download `.pem` file
7. Launch instance and wait 2-3 minutes to start

### Step 2: Connect to Instance
```bash
# On your local machine (Windows PowerShell/Terminal)
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

Replace `your-ec2-public-ip` with your instance's public IP from AWS console.

### Step 3: Install Docker
```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
sudo apt-get install -y docker.io docker-compose

# Add ubuntu user to docker group (avoid using sudo)
sudo usermod -aG docker ubuntu

# Verify installation
docker --version
docker-compose --version

# Exit and reconnect SSH for changes to take effect
exit
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### Step 4: Upload Project Files
```bash
# From your local machine, upload entire project
scp -i your-key.pem -r "C:\Users\laksh\Projects\Final project Sepsis Survival & Risk Prediction Platform" ubuntu@your-ec2-public-ip:~/sepsis-app

# Connect back and navigate to project
ssh -i your-key.pem ubuntu@your-ec2-public-ip
cd sepsis-app
```

### Step 5: Build and Run Docker Container
```bash
# Build Docker image
docker build -t sepsis-prediction:latest .

# Run container
docker run -d \
  --name sepsis-app \
  -p 8501:8501 \
  sepsis-prediction:latest

# Check if running
docker ps

# View logs
docker logs sepsis-app

# Stop container
docker stop sepsis-app

# Restart container
docker start sepsis-app
```

### Step 6: Access Your App
Open browser and go to:
```
http://your-ec2-public-ip:8501
```

## Troubleshooting

**Container exits immediately:**
```bash
docker logs sepsis-app
```

**Port already in use:**
```bash
docker run -d --name sepsis-app -p 8501:8501 sepsis-prediction:latest
# Or use different port: -p 8502:8501
```

**Can't access from browser:**
- Check Security Group allows port 8501
- Run: `docker logs sepsis-app`
- Try: `http://your-ec2-public-ip:8501` (not https)

**Update app code:**
```bash
# Navigate to app directory
cd ~/sepsis-app

# Pull latest code (if using git)
git pull

# Rebuild image
docker build -t sepsis-prediction:latest .

# Stop and remove old container
docker stop sepsis-app
docker rm sepsis-app

# Run new container
docker run -d --name sepsis-app -p 8501:8501 sepsis-prediction:latest
```

## Stopping and Cleanup

```bash
# Stop container
docker stop sepsis-app

# Remove container
docker rm sepsis-app

# Remove image
docker rmi sepsis-prediction:latest
```

## Cost

- **t2.micro**: Free tier (12 months, 750 hours/month)
- **t2.small**: ~$10/month
- **Data transfer**: ~$1-2/month for light usage
- **Total**: Free-$12/month

## Next Steps (Optional)

For production deployment with domain name:
- Purchase domain (Route 53 or external)
- Use Nginx reverse proxy on EC2
- Set up SSL with Let's Encrypt
- Configure auto-reload with supervisor/systemd

---

## Comparison: GitHub Actions vs Manual

| Feature | GitHub Actions | Manual |
|---------|---|---|
| Auto-deploy on push | ✅ Yes | ❌ No |
| Setup time | ~10 min | ~15 min |
| Monthly cost | Free | Free (t2.micro) |
| Complexity | Medium | Low |
| Best for | Continuous development | One-time deployment |

**Choose GitHub Actions if:** You'll update code frequently and want automatic deployments
**Choose Manual if:** You just want it running on AWS with minimal setup
