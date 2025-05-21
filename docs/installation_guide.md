# 📦 Full Installation Guide
To fully enable all features of **HiGoalVita**, you need to install the following components:
1. 🐍 **HiGoalV Core Engine** (Python backend)  
2. 🐇 **Redis Service** – Redis  
3. 🗃️ **Database** – MySQL, OceanBase, or SQLite 
4. 🌐 **Frontend** – Vue.js


## 1. 🐍 Set Up Python Environment

We recommend using **Python 3.12.4** with **Conda** for better dependency and CUDA management.

```bash
conda create --name HiGoalV python=3.12.4
conda activate HiGoalV
```
### Install CUDA
If you do not wish to use CUDA acceleration or are a CPU-only user, you can skip this step.
```bash
conda install -y cudatoolkit=12.4 cuda-nvcc cuda-cupti -c nvidia
```

### Install Poetry
```bash
conda install poetry
# set poetry to use the current environment(conda)
poetry config virtualenvs.create false
```

### Set Up Project with Poetry
```bash
# Navigate to the project directory
cd HiGoalVita
# Install dependencies
poetry install
```
### Install Pytorch
```bash
# CUDA-12.4
pip install torch==2.6.0+cu124 -f https://download.pytorch.org/whl/torch_stable.html
# CPU
pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu
```

### 📦 Configuration Instructions

Copy the config_example directory inside datavolume to a new directory named config, and rename the .env_config file within it to .env. This config folder will serve as the system configuration directory.

To configure values using environment variables (including those defined in the .env file), use the ${YOUR_ENV_KEY} syntax in your configuration file.
If the same environment variable is defined in multiple places, the system environment variable takes precedence over the value defined in the .env file.

---

## 2. 🔁 Install Redis (via Docker)

HiGoalV uses Redis as an in-memory data store for caching and lightweight background coordination. You’ll need Redis running to enable proper pipeline execution and state tracking.
If you're not familiar with Docker, please refer to the docker website and download the docker desktop: https://www.docker.com/

```bash
# Pull and run Redis container
docker pull redis:latest
docker run -d --name some-redis -p 6379:6379 redis:latest
```

---

## 3. 🗃️ Set Up Database

HiGoalV supports multiple databases. When you download and use HiGoalVita for the first time, it uses SQLite as the default relational database and LanceDB as the default vector database.
Of course, you can also choose and configure any other supported database from the options we provide.
The table creation statements for the relational database are located in `datavolume/database/init.sql`.

### 3.1 MySQL

Install MySQL and set up a database. We provide an example using Docker to install MySQL. If you have already installed MySQL or are using another installation method, you can skip this step.

```bash
# Create a MySQL container with root and app user credentials
docker run --name mysql-higoalv \
  -e MYSQL_ROOT_PASSWORD=root_pass \
  -e MYSQL_DATABASE=higoalv_db \
  -e MYSQL_USER=higoalv_user \
  -e MYSQL_PASSWORD=higoalv_pass \
  -p 3306:3306 \
  -d mysql:8.0

# initialize the database
docker exec -i mysql-higoalv mysql -u higoalv_user -p'higoalv_pass' higoalv_db < datavolume/database/init.sql
```
Update your `datavolume/config/system_config.config` file with the database credentials:
```yaml
mysql_config:
  host: "localhost"
  port: 3306
  user: "higoalv_user"
  password: "higoalv_pass"
  database: "higoalv_db"
```

### 3.2 OceanBase

HiGoalV supports [OceanBase](https://www.oceanbase.com/) for enterprise users.

- Follow the [official OceanBase installation guide](https://www.oceanbase.com/docs) to set up the instance.
- Configure connection info in your `datavolume/config/system_config.config` file accordingly.

---

## 4. 🌐 Install Node.js

This project recommends using Node.js v20.x.
If you already have Node.js installed, or if you do not need to use the frontend interface, feel free to skip this section.

### 4.1 Install Node.js using nvm

We recommend using [nvm](https://github.com/nvm-sh/nvm) to manage your Node.js versions.  
With nvm, you can install and switch between multiple versions. If you do not need version management or already have nvm, you may skip this step and install Node.js manually.

#### 4.1.1 (Windows Users)

Visit the [nvm-windows releases page](https://github.com/coreybutler/nvm-windows/releases) and download the latest `nvm-setup.zip`, then unzip and install.

After installation, run the following commands:

```bash
# Check if nvm is installed
nvm --version

# Install Node.js v20
nvm install 20

# Use Node.js v20
nvm use 20

# Enable nvm environment (mount node)
nvm on

# Verify Node.js is active
node --version
```
#### 4.1.2 (macOS / Linux Users)
```bash
# Install nvm (you may check https://github.com/nvm-sh/nvm/releases for other versions)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

# Check current shell
echo $SHELL

# Based on the shell type, add the following to your shell config file.
# Note: if you installed nvm to a custom path, replace "$HOME/.nvm" with your actual install path.

## If using bash (/bin/bash), configure both interactive and login shells:
echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.bashrc
echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> ~/.bashrc
source ~/.bashrc

echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.bash_profile
echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> ~/.bash_profile
source ~/.bash_profile

## If using zsh (/bin/zsh):
echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.zshrc
echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> ~/.zshrc
source ~/.zshrc

# Verify installation
nvm --version

# Install Node.js v20
nvm install 20

# Use Node.js v20
nvm use 20

# Check if Node.js is working
node --version
```

### 4.2 Configure npm registry with nrm
We recommend using nrm to easily manage and switch npm registry sources.
```bash
# Basic npm registry commands:

# Set Taobao mirror globally
npm config set registry https://registry.npmmirror.com

# Check current registry
npm config get registry

# Use specific registry for a single install
npm install <package_name> --registry=https://registry.npmmirror.com
```
If you don’t plan to use nrm, you may skip the following section.
```bash
# Install nrm globally using Taobao mirror
npm install -g nrm --registry=https://registry.npmmirror.com

# Verify installation
nrm --version

# Common nrm commands:

nrm ls                    # List all registries
nrm use <registry-name>   # Switch to a registry (e.g. nrm use taobao)
nrm add <name> <url>      # Add custom registry (e.g. nrm add taobao https://registry.npmmirror.com)
nrm del <name>            # Remove registry
nrm test                  # Test registry speed
```

### 4.3 Install project dependencies
```bash
# Make sure you're in the frontend directory
cd vue

# Install npm packages
npm install
```

---

## ✅ Next Steps

- [Back to README](../README.md)
