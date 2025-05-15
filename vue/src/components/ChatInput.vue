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
<!-- ChatInput.vue -->
<template>
  <div class="chat-input fixed">
      <textarea
        class="code-input"
        v-model="inputMessage"
        @keydown="handleKeydown"
        placeholder="Shift + Enter 换行"
        :style="{ height: inputHeight + 'px' }"
      ></textarea>
    <div class="send-button-container">
      <div class="char-count" v-if="charCount > 1800">
        {{ charCount }}/2000
      </div>
      <select v-model="selectedModel" @change="updateSelectedModel" class="model-select">
        <option v-for="model in modelList" :key="model.key" :value="model.key">
          {{ model.value }}
        </option>
      </select>
      <button
        class="send-button"
        :disabled="!isSendable"
        @click="sendMessage"
        :title="sendButtonTitle"
      >
        <img :src="sendIcon" alt="发送" />
      </button>
    </div>
  </div>
  <div class="footer">
      <p class="footer-text">所有内容均由AI生成，仅供参考</p>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      inputMessage: '',
      inputHeight: 40,
      charCount: 0,
      selectedModel: null,  // 不设默认值，后端动态决定
      modelList: [],
      isGenerating: false,
    };
  },
  computed: {
    isSendable() {
      return this.inputMessage.trim() !== '' || this.isGenerating;
    },
    sendIcon() {
      if (this.isGenerating) {
        return require('@/icons/stop.svg');
      }
      return this.isSendable
        ? require('@/icons/sendIcon.svg')
        : require('@/icons/sendIconDisabled.svg');
    },
    sendButtonTitle() {
      return this.isGenerating ? '停止生成' : (this.isSendable ? '发送消息' : '请输入问题');
    },
  },
  async mounted() {
    try {
      const response = await this.fetchModelList();
      if (response.status === 1 && Array.isArray(response.data) && response.data.length > 0) {
        this.modelList = response.data;
        this.selectedModel = this.modelList[0].key; // 设置默认选中为第一个
        this.$emit('update:selected-model', this.selectedModel); // 通知父组件
      } else {
        console.error('模型列表为空或获取失败:', response.msg);
      }
    } catch (error) {
      console.error('请求模型列表失败:', error);
    }
  },
  methods: {
    updateIsGenerating(isGenerating) {
      this.isGenerating = isGenerating;
    },
    cancelGeneration() {
      if (this.isGenerating) {
        this.$emit('cancel-generation', { type: 'cancel', task_id: '' });
        this.isGenerating = false;
      }
    },
    updateSelectedModel() {
      this.$emit('update:selected-model', this.selectedModel);
    },
    async fetchModelList() {
      const response = await axios.get('/qa/getModel');
      return response.data;
    },
    handleKeydown(event) {
      if (event.shiftKey && event.key === 'Enter') {
        this.adjustHeight();
      } else if (event.key === 'Enter') {
        event.preventDefault();
        this.sendMessage();
      }
    },
    adjustHeight() {
      const lines = (this.inputMessage.match(/\n/g) || []).length + 1;
      this.inputHeight = Math.min(40 * lines, 120);
    },
    checkLength() {
      this.charCount = this.inputMessage.length;
      if (this.charCount > 2000) {
        alert('字数超限');
        this.inputMessage = this.inputMessage.slice(0, 2000);
        this.charCount = 2000;
      }
    },
    async sendMessage() {
      if (this.isGenerating) {
        this.cancelGeneration();
      } else {
        this.isGenerating = true;
        this.$emit('send-message', { role: 'user', content: this.inputMessage });
        this.resetInput();
      }
    },
    resetInput() {
      this.inputMessage = '';
      this.inputHeight = 40;
      this.charCount = 0;
    },
  },
  watch: {
    inputMessage: {
      immediate: true,
      handler() {
        this.adjustHeight();
        this.checkLength();
      },
    },
  },
};
</script>
<style scoped>
:root {
  --widget-line: #e0e0e0;         /* 示例值：浅灰色边框 */
  --yb-input-switch-model-bg-color: rgba(0, 0, 0, 0.3); /* 示例值：浅蓝色背景 */
}
.fixed {
  position: fixed;
  bottom: 40px; /* 距离底部40px */
  left: calc(57%); /* 左侧导航栏宽度加上50% */
  transform: translateX(-50%); /* 向左偏移自身宽度的50% */
  width: 53%; /* 宽度为屏幕的60%*84% */
  padding: 10px;
  background-color: #ffffff;
  border: 1px solid #eee; /* 新增四周边框 */
  border-radius: 20px; /* 圆角 */
  margin-left: auto; /* 左外边距自动 */
  margin-right: auto; /* 右外边距自动 */
}

.footer {
  position: fixed;
  bottom: 0;
  left: calc(60%); /* 左侧导航栏宽度加上50% */
  transform: translateX(-50%); /* 向左偏移自身宽度的50% */
  width: 60%; /* 宽度为屏幕的50% */
  padding: 10px;
  text-align: center;
  height: 20px;
  z-index: 100;
  line-height: 0px; /* 垂直居中文本 */
  font-size: 12px; /* 调整字体大小以适应高度 */
  background-color: #fff; /* 建议添加背景色 */
}

.footer-text {
  font-size: 12px;
  color: #888;
}

.chat-input textarea {
  width: 100%; /* 设置宽度为父容器的100% */
  padding: 12px 16px;
  line-height: 20px;
  min-height: 60px;
  border: 1px solid #ccc;
  border-radius: 20px; /* 圆角 */
  resize: none; /* 禁止用户调整输入框大小 */
  box-sizing: border-box; /* 确保内边距和边框包含在宽度内 */
  scrollbar-width: none;  /* Firefox 隐藏滚动条 */
  -ms-overflow-style: none;  /* IE/Edge 隐藏滚动条 */
}

.chat-input .char-count {
  margin-left: 10px;
  margin-right: 20px;
  color: #888;
}

.send-button-container {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  height: 40px; /* 固定高度 */
}
.model-select {
    height: 40px;
    padding-left: 10px;
    padding-right: 8px;
    border-color: #cecece !important;
    background-color: #ecebeb !important;
    font-weight: 500;
    border-radius: 22px;
    margin-right: 33px;
}

.model-select:focus {
  outline: none;
  border-color: #ffffff;
}

.send-button {
  padding: 0; /* 移除内边距 */
  background-color: #ecebeb;
  color: #fff;
  border: none;
  border-radius: 20px; /* 圆角 */
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%; /* 使按钮高度与容器一致 */
  width: 40px; /* 固定宽度 */
}
.send-button img {
  max-width: 20px; /* 限制图标最大宽度 */
  max-height: 20px; /* 限制图标最大高度 */
  margin: auto; /* 居中对齐 */
}

.send-button:disabled {
  background-color: #656464;
  cursor: not-allowed;
}

.send-button:disabled img {
  filter: grayscale(100%);
  opacity: 0.5;
}

.code-input {
  --text-color: #000000;
  --bg-color: #ffffff;
  background-color: var(--bg-color);
  color: var(--text-color);
  border: 1px solid var(--bg-color) !important; /* 强制覆盖默认边框 */
  outline: none !important; /* 移除聚焦时的浏览器默认轮廓 */
  border-radius: 4px;
  margin: 0;
  font-size: 16px;
  line-height: 1.5;
  resize: none;
  transition: all 0.3s ease;
  outline: none; /* 覆盖浏览器默认轮廓 */
}

.code-input:focus {
  outline: none; /* 移除聚焦轮廓 */
  border-color: var(--bg-color) !important; /* 确保聚焦时边框颜色一致 */
}
</style>

