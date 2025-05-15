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

console.log('vue.config.js is loaded');
module.exports = {
  transpileDependencies: true,
  devServer: {
    open: true,
    port: 8081, // 前端项目运行在 8081 端口
    proxy: {
      '/qa': {
        target: 'http://localhost:8000', // 后端 API 服务运行在 8080 端口
        changeOrigin: true,
        logLevel: 'debug', // 添加日志级别，方便调试
        onProxyReq(proxyReq) {
          console.log('Proxy request:', proxyReq.path);
        }
      },
      '/socket.io': {
        target: 'http://localhost:8000', // WebSocket 和后端 API 服务运行在 8080 端口
        ws: true, // 启用 WebSocket 代理
        logLevel: 'debug', // 添加日志级别，方便调试
        changeOrigin: true, // 如果需要，可以添加这个选项
      },
    },
    client: {
      overlay: false  // ❌ 关闭页面上的红色错误提示框
    }
  }
};
console.log('Proxy config:', module.exports.devServer.proxy);