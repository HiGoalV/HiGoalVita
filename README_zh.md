[English](./README.md) | [中文](./README_zh.md)

# 🚀 HiGoalVita – 模块化、可扩展、可运营的 RAG 框架

**HiGoalVita** 是一个生产就绪的检索增强生成（RAG）平台，提供完整的全栈解决方案，包括服务器、后端服务、前端界面和异步任务管道，可让用户向 LLM 提问并获得基于客户数据的回答。

我们的开源框架具有模块化和可扩展性，原生集成：关系型数据库（SQLite、MySQL、OceanBase）、向量存储（LanceDB、OceanBase）、缓存后端（内存、Redis、文件）。面向真实生产环境打造，HiGoalV-AIOps 提供企业级可靠性、可伸缩性和适应性——支持 Docker 化部署，并提供可选的 Web 界面。

最初由 HiGoal 团队开发并在商业环境中验证，现已开源以赋能社区，提供灵活的生产级 RAG 解决方案。

---
⚒️ 项目架构
![1](https://github.com/user-attachments/assets/a3cc0bad-d331-4ef5-8272-10e9a5257680)

## HiGoalVita组件：
  - 数据层​：数据源​/元数据存储/LLM网关​/向量数据库/索引作业/API服务器
  - 核心服务层：企业知识库/数字员工/服务智能体/对客智能路由
  - 产品层：语料工程/提示词工程/应用工具层/可插拔的Agent插件
  - 模型服务层：微调框架/垂直领域预训练/混合部署
  - 交互层：Web UI

**为你的用例自定义**
  - 自定义 Dataloaders
  - 自定义 Embedder
  - 自定义 VectorDB

## ✨ 功能特性

- 🔍 **RAG 驱动检索**  
  - 与 LLM 模型交互，支持本地或 API 调用
  - 基于客户数据进行回答：  
    - 将客户文档进行嵌入和索引，按需检索以为答案赋能  
    - 将平面文档处理为具有关联关系的可检索知识库  
    - 将每一次对话及系统提示持久化到数据库，实现精细审计、分析和持续迭代
  - 多模式摄取.txt .pdf .json
  - 支持增量索引，支持批量摄取整个文档
    
-🔗知识图谱：自动提取实体和关系
    - 自动提取实体和关系（v2.0 可用） 
    - 图数据库驱动的索引、检索与回答（v3.0 可用）

- 🏗️ **生产级后端**  
  - 基于 FastAPI + Gunicorn，支持 Docker/Docker-Compose 容器化及水平扩展 
  - Docker 化部署（v2.0 可用）  
  - 基于角色的认证与访问控制（v2.0 可用）

- 🖥️ **端到端工具链**  
  - CLI：文档导入、嵌入构建、查询执行与管道测试  
  - Web UI：交互式问答会话  
  - Web UI：文档上传、处理、注释与标注（v2.0 可用）  
  - 自动记录每次 API 调用、用户查询及 LLM 回复

- 🧱 **模块化架构 & 可配置组件**  
  - 数据库：SQLite、MySQL、OceanBase  
  - 向量存储：LanceDB、OceanBase  
  - 缓存：内存、Redis、文件  
  - LLM 提供商：OpenAI、DeepSeek、Qianwen

- 🤖 **Agent 模块**  
  - NL2SQL：自然语言转数据库查询（v2.0 可用），支持查询、编辑与自动化分析、可视化与摘要  
  - 域专用 Agent（v3.0 可用）：预构建的行业助手，提供定制化工作流


---

## 📌 开源路线图

### 🚀 版本 1.0 – 核心 RAG 与运营套件  
基础发布，提供端到端的 RAG 引擎和运维工具：关系型数据库索引、生产级后端、CLI 工具及基础 Web UI。

### 🛡️ 版本 2.0 – 运营与安全增强 & NL→SQL Agent  
面向企业环境，新增安全、文档管理与实时流功能，并引入首个数据库自动化 Agent。

### 🌐 版本 3.0 – 图 RAG 与高级 Agent  
转型为图数据库原生系统，支持多跳推理、预构建行业 Agent 及基于图分析的推荐与预测。

---

## DEMO  
添加演示图片或操作示例。

---

## 安装指南

要体验 HiGoalVita 的全部功能，请安装以下组件：  
1. **Python 引擎**：核心引擎、API Server 及 CLI 工具  
2. **中间件**：Redis  
3. **数据库**：SQLite、MySQL 或 OceanBase

详见 [安装指南](docs/installation_guide.md)。

---

## 快速开始

### 后端独立模式
```bash
# 克隆仓库
git clone https://github.com/HiGoalV/HiGoalVita.git

# 安装依赖
poetry install

# 构建索引并查询示例
higoalcore index
higoalcore query --query "这是一个示例问题"
```

### 完整套件
```bash
# 克隆仓库并安装依赖
git clone https://github.com/HiGoalV/HiGoalVita.git
poetry install

# 拉取并启动 Redis 容器
docker pull redis:latest

docker run -d --name redis -p 6379:6379 redis:latest

# 启动后端服务
uvicorn higoalengine.app.main:app

# 启动前端 (Vue)
cd vue && npm run serve
```

---

## 📜 许可协议

本项目采用 Apache License 2.0 许可，详见 [LICENSE](LICENSES/APACHE_LICENSE)。

---

## 💼 关于

HiGoalVita 由 HiGoal Corporation 开发维护，专注于基于大型语言模型的企业级知识解决方案。  
商业合作、集成或伙伴关系洽谈，请联系 **partner@higoall.com** 或访问 **https://higoal.com**。

---

## 💡 鸣谢

本项目包含来自微软 [graphrag](https://github.com/microsoft/graphrag) 的未修改代码，相关部分基于 [MIT 许可协议](https://opensource.org/licenses/MIT) 发布。  
我们感谢微软对开源社区的贡献。

虽然本项目整体以 Apache License 2.0 发布，但所包含的 MIT 代码仍保留其原始许可协议。