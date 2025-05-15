<!--
  Copyright 2025 HiGoal Corporation

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
-->
<!-- HomePage.vue -->
<template>
  <div class="layout-container">
    <div class="sidebar">
      <div class="logo">氦狗科技</div>
    </div>
    <div class="content" ref="chatMessagesContainer">
      <div class="chat-area" >
        <div>
          <div class="chat-messages" >
              <div
              v-for="message in messages" :key="message.id"
              class="message"
              :class="{ 'self': message.role === 'user', 'assistant': message.role === 'assistant' }"
              >
                <div
                class="message-bubble"
                :class="{ 'self': message.role === 'user', 'assistant': message.role === 'assistant' }"
              >
                <!-- 如果消息是“抱歉，繁忙”，则显示图标 -->
                <span v-if="message.isRetryable" class="retry-container">
                  {{ message.content }}
                  <button
                    class="retry-button"
                    @click="retrySendMessage(message)"
                  >
                    <img src="@/icons/refresh.svg" alt="刷新" width="20" height="20" />
                  </button>
                </span>
                <!-- 其他消息正常显示 -->
                <span v-else v-html="formatMessageAsHtml(message.content)"></span>
              </div>
              </div>
          </div>
        </div>
        <ChatInput
              v-model:selectedModel="selectedModel"
              :modelList="modelList"
              @send-message="handleSendMessage"
              @cancel-generation="handleCancelGeneration"
              @update:selected-model="handleSelectedModelUpdate"
              ref="chatInput"
             />
      </div>
        <!--双向绑定 -->
    </div>
  </div>
</template>

<script>
import WebSocketManager  from '@/libs/WebSocketManager.js'; 
import ChatInput from '@/components/ChatInput.vue';
import MarkdownIt from 'markdown-it' // 新增导入
import DOMPurify from 'dompurify';
// import mdTypographer from 'markdown-it-typographer';
// import mdTaskLists from 'markdown-it-task-lists';
// import mdContainer from 'markdown-it-container';
import hljs from 'highlight.js';
import { getOrCreateUserId } from '@/libs/userId';
export default {
  components: {
    ChatInput,
  },
  data() {
    return {
      userId: null,
      webSocketManager:null,
      selectedModel: '1', // 默认选择通义千问
      modelList: [
    {
      "key": 1,
      "value": "通义千问"
    },
    {
      "key": 2,
      "value": "其他模型"
    }
  ], // 从后端获取的模型列表
      messages: [
        { role: 'assistant', content: '我是海狗，你的智能助手' },
         
      ],
      mdParser: new MarkdownIt({
        breaks: true,
        linkify: true,
        html: true, // 允许 HTML 标签
      }),
    };
  },

 created() {
  this.mdParser = new MarkdownIt({
    breaks: true,
    linkify: true,
    html: true,          // 允许解析 HTML（需配合 DOMPurify）
    xhtmlOut: true,      // 输出 XHTML 格式
    typographer: true,   // 启用智能排版（需插件）
  });

  // 启用插件
  // this.mdParser.use(mdTypographer);
  
  // 自定义代码高亮
  this.mdParser.highlight = function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return `<pre class="hljs"><code>${hljs.highlight(str, { language: lang }).value}</code></pre>`;
      // eslint-disable-next-line no-empty
      } catch (__) {}
    }
    return `<pre class="hljs"><code>${this.utils.escapeHtml(str)}</code></pre>`;
  };
  // 启用任务列表
  // this.mdParser.use(mdTaskLists);

  // 启用自定义容器（如警告框）
  // this.mdParser.use(mdContainer, 'warning', {
  //   validate: params => params.trim().match(/^warning\s*(.*)$/),
  //   render: (tokens, idx) => tokens[idx].nesting === 1
  //     ? '<div class="alert alert-warning">\n'
  //     : '</div>\n',
  // });
},
  mounted() {
    // 检查是否有初始消息
    const initialMessage = localStorage.getItem('initialMessage');
    this.initWebSocket();
    this.userId = getOrCreateUserId();
    console.log('当前用户ID:', this.userId);
    if (initialMessage) {
      const message = JSON.parse(initialMessage);
      localStorage.removeItem('initialMessage'); // 移除本地存储中的初始消息
      console.log("发送初始消息"+message)
      setTimeout(() => {
        this.handleSendMessage(message);
      }, 1000);
    }
  },
  methods: {
    handleSelectedModelUpdate(newKey) {
      this.selectedModel = newKey;
    },
    initWebSocket() {
      console.log("正在初始化Socket.IO");
      this.webSocketManager = new WebSocketManager(
        {id: this.userId},
        this.getAIStatus 
      );
      this.webSocketManager.connectSocket();
      console.log("初始化成功");
    },
    getAIStatus(data) {

      if (data.type === 'result') {
        // 非流式处理
        this.messages = this.messages.filter(msg => msg.content !== "AI正在思考");
        this.messages.push({ role: 'assistant', content: data.content });
        this.scrollToBottom();
        this.updateGeneratingStatus(false);
      }
      console.log(data)
      console.log(data.type)

      // 修改后的 getAIStatus（处理 chunk 类型）
      if (data.type === 'chunk') {
        console.log("回调函数")
        const existing = this.messages.find(msg => msg.content === "AI正在思考");
        if (existing) {
          this.messages = this.messages.filter(msg => msg !== existing);
          this.messages.push({ role: 'assistant', content: '' });
        }
        // 安全更新数组（避免递归更新）
        const lastIndex = this.messages.findLastIndex(msg => msg.role === 'assistant');
        if (lastIndex !== -1) {
          this.messages.splice(lastIndex, 1, { ...this.messages[lastIndex], content: this.messages[lastIndex].content + data.content });
        }

        this.scrollToBottom();

        if (data.is_final) {
          this.updateGeneratingStatus(false); // 标记生成完成
        }
      }
    },
    updateGeneratingStatus(isGenerating) {
      // 通知子组件更新状态
      this.$refs.chatInput.updateIsGenerating(isGenerating);
    },
    scrollToBottom() {
      // 获取 chat-messages 容器
      const container = this.$refs.chatMessagesContainer;
      if (container) {
        // 滚动到容器的底部
        container.scrollTop = container.scrollHeight;
      }
    },
    //固定返回调用
    async handleSendMessage(message) {
      this.messages.push(message); // 添加用户发送的消息到消息列表
      console.log('当前选择的模型:', this.selectedModel);
      this.messages.push({ role: 'assistant', content: "AI正在思考" });

      const sendData = {
        type: "create",
        user_id: this.userId,
        query: message.content,
        model: this.selectedModel,
        stream: true
      };
    
      try {
        if (this.webSocketManager && this.webSocketManager.socketStatus) {
          // 使用 Socket.IO 的 emit 方法发送消息
          this.webSocketManager.sendMessage('message', sendData);
        } else {
          console.error('Socket.IO 未连接');
        }
      } catch (error) {
        console.error('获取 AI 回复失败:', error);
        this.messages.push({ role: 'assistant', content: '抱歉，繁忙', isRetryable: true });
      } finally {
        this.isGenerating = false;
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      }
  },
 handleCancelGeneration() {
    const taskId = this.webSocketManager.getTaskId();
    if (taskId) {
      const cancelData = {
        type: 'cancel',
        task_id: taskId,
      };
      if (this.webSocketManager && this.webSocketManager.socketStatus) {
        // 使用 Socket.IO 的 emit 方法发送取消消息
        this.webSocketManager.sendMessage('cancel', cancelData);
        // 更新消息列表，将 "AI正在思考" 替换为 "AI已停止思考"
      const index = this.messages.findIndex(msg => msg.content === "AI正在思考");
      if (index !== -1) {
        this.messages[index].content = 'AI已停止思考';
      }
      } else {
        console.error('Socket.IO 未连接');
      }
    }
  },
    
    formatMessageAsHtml(content) {
      let formatted = content; // 如果不需要替换换行符，可以直接使用
      // 如果需要替换换行符
      // formatted = content.replace(/\n/g, '<br>');
      const html = this.mdParser.render(formatted);
      return DOMPurify.sanitize(html);
    },
      // 修改后的 retrySendMessage
    async retrySendMessage() {
  const index = this.messages.findIndex(m => m.content === '抱歉，繁忙' && m.isRetryable);
  if (index !== -1) {
    this.messages.splice(index, 1); // 移除可重试消息

    // 找到需要重试的原始用户消息
    const originalMessage = this.messages
      .slice()
      .reverse()
      .find(m => m.role === 'user' && !m.isRetryable);

    if (originalMessage) {
      try {
        // 直接发送原始消息，不重复添加用户消息
        const sendData = {
          type: "create",
          user_id: this.userId,
          query: originalMessage.content,
          model: this.selectedModel,
          stream: true
        };

        if (this.webSocketManager && this.webSocketManager.socketStatus) {
          this.webSocketManager.sendMessage('message', sendData);
          this.messages.push({ role: 'assistant', content: "AI正在思考" });
          this.scrollToBottom();
        } else {
          throw new Error('WebSocket未连接');
        }
      } catch (error) {
        console.error('重试发送失败:', error);
        this.messages.push({ role: 'assistant', content: '抱歉，繁忙', isRetryable: true });
        this.scrollToBottom();
      }
    }
  }
}
  },

  // beforeUnmount() {
  //   if (this.webSocketManager) {
  //     this.webSocketManager.closeWebSocket();
  //   }
  // },

};
    // 流式返回调用
    // async handleSendMessage(message) {
    //   this.messages.push(message); // 添加用户发送的消息到消息列表
    //   // 调用 OpenAI API 获取 AI 的回复
    //   const assistantMessage = { role: 'assistant', content: 'AI正在思考請稍後' };
    //   this.messages.push(assistantMessage); // 先添加一个空的 AI 消息
    //   try {
    //     const isFinished = await sendMessageToGPT(message.content, (chunkContent) => {
    //       console.log('Updating assistant message with chunk:', chunkContent);
    //       assistantMessage.content += chunkContent;
    //     });

    //     if (!isFinished) {
    //       console.warn('Stream did not finish properly.');
    //     }
    //   } catch (error) {
    //     console.error('获取 AI 回复失败:', error);
    //     this.messages.push({ role: 'assistant', content: '抱歉，繁忙', isRetryable: true }); // 添加可重试的消息
    //   }
    // },
</script>



<style scoped>
body {
  background-color: #fff;
  font-family: '思源黑体', sans-serif;
  margin: 0;
  padding: 0;
  height: 100vh;
  display: flex;
}

.layout-container {
  display: flex;
  flex: 1;
  width: 100%;
}

.sidebar {
  width: 16%;
  height: 100vh;
  background-color: #f3f3f3;
  padding: 20px;
  border: 1px solid #e3e2e2;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;

}

.content {
  display: flex;
  flex-direction: column;
  flex: 1;
  width: 84%;
  margin-left: 20%;
  padding: 20px;
  overflow-y: auto;
  scrollbar-width: none;  /* Firefox 隐藏滚动条 */
  -ms-overflow-style: none;  /* IE/Edge 隐藏滚动条 */
  height: 1000px;
}


.logo {
  font-size: 22pt;
  margin-bottom: 20px;
  text-align: center;
  padding: 10px 0;
}


.chat-area {
  width: 70%; /* 设置宽度为父容器的 70% */
  margin-left: 10%;
  display: flex;
  flex-direction: column;
  gap: 20px; /* 关键间距控制 */
}

.chat-messages {
  flex: 1;
  margin-bottom: 180px;
}


.message {
  margin-bottom: 16px;
  display: flex;
  /* 默认右对齐（用户消息） */
  justify-content: flex-end;
}

.message.assistant {
  /* 助手消息左对齐 */
  justify-content: flex-start;
}


.message-bubble {
  background-color: #e0e0e0; /* 用户消息的背景色 */
  border-radius: 11px; /* 气泡圆角 */
  padding: 8px 12px;
  max-width: 100%; /* 限制消息气泡的最大宽度 */
  word-wrap: break-word; /* 自动换行 */
  margin-bottom: 16px; /* 纵向间距 */
}

.message-bubble.assistant {
  background-color: #fff; /* AI消息背景色为白色 */
  border: none; /* 隐藏气泡描边 */
  border-radius: 0; /* 没有圆角 */
  margin-left: 0px; /* AI消息左对齐，边距左0px */
  margin-right: auto; /* 右边距自动 */
   max-width: 100%;
}

.message-bubble.self {
  margin-right: 0px; /* 用户消息右对齐，边距右0px */
  margin-left: auto; /* 左边距自动 */
   max-width: 80%;
}

.assistant-text {
  margin-left: 40%; 
  color: rgb(180, 184, 184);
}


.retry-container {
  display: flex;
  align-items: center;
}

.retry-button {
  margin-left: 10px;
  background-color: transparent;
  border: none;
  cursor: pointer;
}

.retry-button img {
  width: 20px;
  height: 20px;
}
@media (max-width: 768px) {
  .sidebar {
    display: none; /* 隐藏 sidebar */
  }
  .content {
    width: 100%; /* content 占满整个宽度 */
    margin-left: 0; /* 移除左边距 */
  }
}
</style>
