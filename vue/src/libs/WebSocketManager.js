/* 
 * Copyright 2025 HiGoal Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
import io from 'socket.io-client';

export default class WebSocketManager {
  constructor(userInfo, onMessage) {
    console.log('开始初始化');
    this.SOCKET_URL = 'http://localhost:8000'; // 注意协议改为http
    this.userInfo = userInfo;
    this.onMessage = onMessage; // 消息处理回调
    this.socket = null;
    this.taskId = null;
    this.socketStatus = false;
    this.pingInterval = null;
    console.log('WebSocketManager 初始化完成，SOCKET_URL:', this.SOCKET_URL);
  }

  connectSocket() {
    console.log('Socket.IO 连接中...');
    try {
      if (!this.socket) {
        // 创建 Socket.IO 连接
        this.socket = io(this.SOCKET_URL, {
          reconnection: true,
          reconnectionAttempts: Infinity,
          reconnectionDelay: 1000,
          reconnectionDelayMax: 5000,
          randomizationFactor: 0.5,
          transports: ['websocket'],
        });

        // 连接成功事件
        this.socket.on('connect', () => {
          console.log('Socket.IO 连接已建立');
          this.socketStatus = true;
          this.startPing(); // 开始发送心跳
          // 如果需要认证，可以在这里发送认证消息
          // this.socket.emit('authenticate', {
          //   user_id: this.userInfo?.id,
          //   timestamp: Date.now(),
          // });
        });

        // 接收消息事件
        this.socket.on('message', (message) => {
          console.log('Socket.IO 收到消息message:', message.data);
          const data=message.data
          const type=data.type
          switch (type) {
            case "chunk":
              this.handleIncomingMessage(data);
              break;
            case "result":
              this.handleIncomingMessage(data);
              break;
            case "status":
              this.handleTaskUpdate(data);
              break;
            case "connect_error":
              this.handleConnectionError();
              break;
            case "disconnect":
              this.handleDisconnect();
              break;
          }
        });
      }
    } catch (error) {
      console.log('Socket.IO 连接失败:', error);
      this.handleConnectionError();
    }
  }

  handleIncomingMessage(message) {
    console.log(message);
    if (message && typeof message === 'object') {
      if (message.type === 'pong') {
        return; // 忽略心跳响应
      }
  
      if (message.type === 'result' && message.task_id === this.taskId) {
        console.log('调用回调函数处理结果消息', message.data);
        this.onMessage(message); // 处理完整结果
      }
  
      if (message.type === 'chunk' && message.task_id === this.taskId) {
        console.log('处理流式chunk片段:', message);
       // 延迟80ms后执行
        // setTimeout(() => {
        this.onMessage(message);
        // }, 80);
      }
  
      // 状态消息也可能带 task_id
      if (message.status === 'pending' && message.task_id) {
        this.taskId = message.task_id;
        console.log('更新 task_id:', this.taskId);
      }
    }
  }

  handleResultMessage(data) {
    if (data.task_id === this.taskId) {
      console.log('调用回调函数处理结果消息', data);
      this.onMessage(data);
    }
  }

  handleTaskUpdate(data) {
    if (data?.status === 'pending' && data.task_id) {
      this.taskId = data.task_id;
      console.log('更新 task_id:', this.taskId);
    }
  }

  handleConnectionError() {
    this.socketStatus = false;
    this.cleanup();
    setTimeout(() => this.connectSocket(), 1000);
  }

  handleDisconnect() {
    this.socketStatus = false;
    this.cleanup();
    setTimeout(() => this.connectSocket(), 1000);
  }

  startPing() {
    // 清除之前的定时器
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
    }
    
    // 每30秒发送一次心跳
    this.pingInterval = setInterval(() => {
      if (this.socket && this.socketStatus) {
        this.socket.emit('ping');
      }
    }, 30000);
  }

  cleanup() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  closeSocket() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.socketStatus = false;
      this.cleanup();
    }
  }

  getTaskId() {
    return this.taskId;
  }

  sendMessage(type, data) {
    if (this.socket && this.socketStatus) {
      this.socket.emit('message', { type, ...data });
    } else {
      console.error('Socket.IO 未连接');
    }
  }
}