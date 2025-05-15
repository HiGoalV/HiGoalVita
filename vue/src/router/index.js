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

import { createRouter, createWebHashHistory } from "vue-router";
// 从 'vue-router' 库中导入创建路由和创建哈希历史记录的方法

// 定义路由对象
const router = createRouter({
  history: createWebHashHistory(),
  // 使用 createWebHashHistory 方法创建哈希路由的历史记录模式

  routes: [
    // 定义路由配置数组
    {
      path: "/home",
      // 根路径
      name: "home",
      // 路由名称为 'home'
      component: () => import("../views/HomePage.vue"),
      // 当访问根路径时，通过动态导入加载 '../views/Home.vue' 组件
    },
    {
      path: "/",
      name: "about",
      // 路径为 '/about'，路由名称为 'about'
      component: () => import("../views/AboutHome.vue"),
      // 当访问 '/about' 路径时，通过动态导入加载 '../views/About.vue' 组件
    },
  
  ],
});

export default router;
// 将创建的路由对象导出，以便在其他模块中使用
