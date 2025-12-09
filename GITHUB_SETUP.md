# 🚀 GitHub Setup Guide

This guide will help you push the Reptile Tracker project to GitHub.

## Prerequisites

- Git installed on your computer
- A GitHub account (create one at https://github.com if you don't have one)

## Step-by-Step Instructions

### 1. Create a New Repository on GitHub

1. Go to https://github.com
2. Click the **"+"** icon in the top right corner
3. Select **"New repository"**
4. Fill in the details:
   - **Repository name**: `reptile-tracker` (or your preferred name)
   - **Description**: "A comprehensive desktop application for tracking reptile care, feeding schedules, and shed records"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click **"Create repository"**

### 2. Connect Your Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Navigate to your project directory
cd /Users/liamdouglas/Desktop

# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/reptile-tracker.git

# Push your code to GitHub
git push -u origin main
```

### 3. Verify the Upload

1. Refresh your GitHub repository page
2. You should see all your files:
   - reptile_tracker.py
   - reptile_tracker_db.py
   - README.md
   - REPTILE_TRACKER_README.md
   - LICENSE
   - CONTRIBUTING.md
   - requirements.txt
   - .gitignore
   - sample CSV files

### 4. Update the README (Optional)

After pushing, you may want to update the README.md to replace `YOUR_USERNAME` with your actual GitHub username:

1. Edit README.md
2. Replace `YOUR_USERNAME` in the clone URL
3. Commit and push:
   ```bash
   git add README.md
   git commit -m "Update README with correct GitHub username"
   git push
   ```

## Alternative: Using GitHub Desktop

If you prefer a GUI:

1. Download GitHub Desktop from https://desktop.github.com
2. Install and sign in with your GitHub account
3. Click **"Add"** → **"Add Existing Repository"**
4. Select your Desktop folder
5. Click **"Publish repository"**
6. Choose repository name and visibility
7. Click **"Publish Repository"**

## Using SSH Instead of HTTPS (Recommended for Security)

### Setup SSH Key

1. Generate SSH key (if you don't have one):
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. Add SSH key to ssh-agent:
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ```

3. Copy your public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

4. Add to GitHub:
   - Go to GitHub Settings → SSH and GPG keys
   - Click "New SSH key"
   - Paste your public key
   - Click "Add SSH key"

5. Change remote URL to SSH:
   ```bash
   git remote set-url origin git@github.com:YOUR_USERNAME/reptile-tracker.git
   ```

## Making Future Updates

After making changes to your code:

```bash
# Check what files changed
git status

# Add files you want to commit
git add filename.py
# Or add all changed files
git add .

# Commit with a descriptive message
git commit -m "Add new feature: description"

# Push to GitHub
git push
```

## Common Git Commands

```bash
# View commit history
git log

# View current status
git status

# View differences
git diff

# Create a new branch
git checkout -b feature-name

# Switch branches
git checkout main

# Pull latest changes from GitHub
git pull

# View remote repositories
git remote -v
```

## Troubleshooting

### Authentication Failed

If you get authentication errors:
- Make sure you're using the correct username
- Use a Personal Access Token instead of password
- Or set up SSH keys (recommended)

### Permission Denied

- Check that you own the repository
- Verify your GitHub credentials
- Try using SSH instead of HTTPS

### Files Not Showing Up

- Make sure files are added: `git add .`
- Check .gitignore isn't excluding them
- Verify commit was successful: `git log`

## Repository Settings (Optional)

After pushing, you can configure:

1. **Topics/Tags**: Add tags like `python`, `reptile-care`, `tkinter`, `sqlite`
2. **About**: Add description and website
3. **Releases**: Create releases for versions
4. **Issues**: Enable issue tracking
5. **Wiki**: Add additional documentation
6. **GitHub Pages**: Host documentation

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Add repository description and topics
3. ✅ Enable issues for bug reports
4. ✅ Share with the reptile keeping community
5. ✅ Accept contributions from others

## Repository URL Format

After setup, your repository will be available at:
- **HTTPS**: `https://github.com/YOUR_USERNAME/reptile-tracker`
- **SSH**: `git@github.com:YOUR_USERNAME/reptile-tracker.git`

Users can clone it with:
```bash
git clone https://github.com/YOUR_USERNAME/reptile-tracker.git
```

---

**Congratulations!** Your Reptile Tracker is now on GitHub! 🎉

Share the repository link with other reptile keepers who might find it useful!