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

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/tailwind.css'

const app = createApp(App).use(router).mount('#app')

// createApp(App);

app.config.errorHandler = (err, instance, info) => {
  const msg = err?.message || '';
  if (msg.includes('Maximum recursive updates exceeded')) {
    // 👇 忽略这个递归更新的错误，不让它传递或打印
    console.warn('[已拦截递归更新错误]', msg);
    return;
  }

  // 对于其他错误继续抛出或记录
  console.error('[Vue 错误]', err, info);
};