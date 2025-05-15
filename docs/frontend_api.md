# **接口文档**

> 本文档包含 WebSocket 接口和 HTTP 接口两部分说明。

# **WebSocket 接口（WS接口）**

所有 WebSocket 消息格式都是 JSON，字段 type 决定了操作种类。

## **通用响应结构（MessageResponse）**

```json
{
  "status": "响应状态", # 1成功 0错误
  "code": "http状态码",
  "message": "提示信息", 
  "data": {},
  "timestamps": "时间戳"
}
```



## **1. 创建任务**

- **接口类型**：create
- **说明**：提交一个新的任务，进入处理流程

### **请求参数（WSCreateRequest）**

| **参数名** | **类型** | **必填** | **说明**                      |
| ---------- | -------- | -------- | ----------------------------- |
| type       | string   | 是       | 固定为 create                 |
| query      | string   | 是       | 提问内容                      |
| user_id    | string   | 否       | 用户ID，默认 default          |
| model      | string   | 是       | 指定使用的模型id              |
| stream     | bool     | 否       | 是否启用流式传输（默认false） |

### **请求示例**

```json
{
  "type": "create",
  "query": "你是谁？",
  "user_id": "ABC23",
  "model": 1,
  "stream": true,
}
```

### **响应示例**

```json
# 确认收到，返回taskid
{
  "status": 1,
  "code": 200,
  "message": "AI正在思考中..", 
  "data":
  {
    "type": "status",
    "task_id": "as8di2jdhsiduhi1u2d",
    "status": "pending"
  },
  "timestamps": 1231231231
}

# 流式碎片
{
  "status": 1,
  "code": 200,
  "message": "", 
  "data":
  {
    "type": "chunk",
    "chunk_index": 1,
    "content": "我是",
    "task_id": "as8di2jdhsiduhi1u2d",
    "is_final": False
  },
  "timestamps": 1231231231
}

# 完整结果
{
  "status": 1,
  "code": 200,
  "message": "", 
  "data":
  {
    "type": "result",
    "content": "我是通义千问",
    "task_id": "as8di2jdhsiduhi1u2d"
  },
  "timestamps": 1231231231
}

# 错误
{
  "status": 0,
  "code": 501,
  "message": "服务器内部错误",
  "timestamps": 1231231231
}
```



## **2. 取消任务**

- **接口类型**：cancel
- **说明**：取消一个正在执行中的任务

### **请求参数（WSCancelRequest）**

| **参数名** | **类型** | **必填** | **说明**       |
| ---------- | -------- | -------- | -------------- |
| type       | string   | 是       | 固定为 cancel  |
| task_id    | string   | 是       | 要取消的任务ID |

### **请求示例**

```json
{
  "type": "cancel",
  "task_id": "as8di2jdhsiduhi1u2d"
}
```

### **响应示例**

```json
# 成功取消
{
  "status": 1,
  "code": 200,
  "message": "任务已取消", 
  "data":
  {
    "type": "status",
    "task_id": "as8di2jdhsiduhi1u2d",
    "status": "cancelled"
  },
  "timestamps": 1231231231
}

```

## **3. 心跳检测**

- **接口类型**：ping
- **说明**：检测 WebSocket 连接是否健康

### **请求示例**

```json
{
  "type": "ping"
}
```

### **响应示例**

```json
{
  "type": "pong"
}
```



# **普通HTTP接口**



# **1. 获取模型**

## 请求信息

- **方法**：GET
- **URL**：`/getModel`
- **入参**：无

## 响应信息

### 成功响应

- **状态码**：200
- **返回格式**：JSON
- **示例**：

```json
{
  "status": 1,
  "code": 200,
  "data": [
    {
      "key": 1,
      "value": "通义千问"
    },
    {
      "key": 2,
      "value": "其他模型"
    }
  ],
  "message": "操作成功",
  "timestamps": 1716886968834
}
```

| 字段名     | 类型   | 说明                       |
| ---------- | ------ | -------------------------- |
| status     | int    | 状态码，1 表示成功         |
| data       | array  | 模型列表                   |
| data.key   | int    | 模型的唯一标识符           |
| data.value | string | 模型的名称                 |
| message    | string | 操作结果的描述             |
| timestamps | int    | 时间戳，表示响应生成的时间 |