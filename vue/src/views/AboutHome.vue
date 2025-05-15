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
<template>
  <div class="layout-container">
    <div class="sidebar">
      <div class="logo">氦狗科技</div>
    </div>
    <div class="content">
      <div class="temporary-message">
        <img src="@/icons/chat.svg" alt="聊天" class="temporary-icon" />
        <p>临时对话，页面刷新后将被完全删除</p>
      </div>
      <ChatInput @send-message="handleSendMessage" />
    </div>
  </div>
</template>

<script>
import ChatInput from '@/components/ChatInput.vue';

export default {
  components: {
    ChatInput,
  },
  methods: {
    handleSendMessage(message) {
      // 保存用户发送的消息到本地存储
      localStorage.setItem('initialMessage', JSON.stringify(message));
      // 跳转到 HomePage.vue
      this.$router.push('/home');
    },
  },
};
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
  height: 650px; /* 设置固定高度 */
  scrollbar-width: none;  /* Firefox 隐藏滚动条 */
  -ms-overflow-style: none;  /* IE/Edge 隐藏滚动条 */
}


.logo {
  font-size: 22pt;
  margin-bottom: 20px;
  text-align: center;
  padding: 10px 0;
}


.temporary-message {
  position: absolute;
  top: 40%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #888;
  font-size: 14px;
  z-index: 100;
}

.temporary-icon {
  width: 60px;
  height: 60px;
  margin-bottom: 10px;
}
</style>