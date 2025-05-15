# 📦 Full Installation Guide
To fully enable all features of **HiGoalV-AIOps**, you need to install the following components:
1. 🐍 **HiGoalV Core Engine** (Python backend)  
2. 🐇 **Redis Service** – Redis  
3. 🗃️ **Database** – MySQL, OceanBase, or SQLite 


## 1. 🐍 Set Up Python Environment

We recommend using **Python 3.12.4** with **Conda** for better dependency and CUDA management.

```bash
conda create --name HiGoalV python=3.12.4
conda activate HiGoalV
```

### Install Poetry
```bash
conda install poetry
```

### Set Up Project with Poetry

```bash
# Navigate to the project directory
cd HiGoalV-AIOps-dev
# Install dependencies
poetry install
```

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

HiGoalV supports multiple databases. Choose one based on your use case:

### 3.1 MySQL

Install MySQL and set up a database:

```bash
# On Linux/macOS
sudo apt install mysql-server

# Start MySQL shell and create a database
mysql -u root -p
CREATE DATABASE higoalv_db;
```

Update your `.env` file with the database credentials:

```
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=higoalv_db
```

### 3.2 OceanBase

HiGoalV supports [OceanBase](https://www.oceanbase.com/) for enterprise users.

- Follow the [official OceanBase installation guide](https://www.oceanbase.com/docs) to set up the instance.
- Configure connection info in your `.env` file accordingly.

---

## ✅ Next Steps

- [Back to README](../README.md)
