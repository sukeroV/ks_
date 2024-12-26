<template>
  <el-container class="layout-container">
    <el-container class="main-container">
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <div class="header-left">
          <div class="logo">
            <el-icon :size="24"><Edit /></el-icon>
            <span class="logo-text">口算练习系统</span>
          </div>
          
          <el-menu 
            :default-active="activeMenu" 
            mode="horizontal" 
            class="header-menu"
            background-color="#ffffff"
            text-color="#303133"
            active-text-color="#409EFF"
            router
          >
            <el-menu-item index="/home" @click="handleMenuClick('/home')">
              <el-icon><House /></el-icon>首页
            </el-menu-item>
            
            <el-menu-item index="/practice" @click="handleMenuClick('/practice')">
              <el-icon><Edit /></el-icon>开始练习
            </el-menu-item>
            
            <el-menu-item index="/history" @click="handleMenuClick('/history')">
              <el-icon><List /></el-icon>练习历史
            </el-menu-item>
            
            <el-menu-item index="/mistakes" @click="handleMenuClick('/mistakes')">
              <el-icon><Warning /></el-icon>错题本
            </el-menu-item>
          </el-menu>
        </div>
        
        <div class="header-right">
          <el-dropdown trigger="click" @command="handleCommand">
            <span class="user-dropdown">
              <el-icon><User /></el-icon>
              <span class="username">{{ userName }}</span>
              <el-icon><CaretBottom /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人信息
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  House,
  User,
  Edit,
  List,
  Warning,
  CaretBottom,
  SwitchButton
} from '@element-plus/icons-vue'

export default defineComponent({
  name: 'Layout',
  components: {
    House,
    User,
    Edit,
    List,
    Warning,
    CaretBottom,
    SwitchButton
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    // 获取当前用户名
    const userName = computed(() => {
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      return user.name || '未登录'
    })
    
    // 计算当前激活的菜单项
    const activeMenu = computed(() => route.path)
    
    // 处理下拉菜单命令
    const handleCommand = (command: string) => {
      switch (command) {
        case 'profile':
          router.push('/profile')
          break
        case 'logout':
          localStorage.removeItem('user')
          router.push('/login')
          ElMessage.success('已退出登录')
          break
      }
    }
    
    // 添加菜单点击处理函数
    const handleMenuClick = (path: string) => {
      router.push(path)
    }
    
    return {
      userName,
      activeMenu,
      handleCommand,
      handleMenuClick
    }
  }
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.main-container {
  height: 100%;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 100;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  flex: 1;
}

.logo {
  display: flex;
  align-items: center;
  margin-right: 40px;
  flex-shrink: 0;
}

.logo-text {
  margin-left: 8px;
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  white-space: nowrap;
}

.header-menu {
  border-bottom: none;
  flex: 1;
  display: flex;
  justify-content: flex-start;
}

:deep(.el-menu--horizontal) {
  border-bottom: none;
  width: 100%;
}

:deep(.el-menu-item) {
  height: 60px;
  line-height: 60px;
  padding: 0 20px;
  font-size: 14px;
}

.header-right {
  margin-left: 20px;
  flex-shrink: 0;
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 0 12px;
  height: 40px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.username {
  margin: 0 8px;
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
}

.main-content {
  padding: 0;
  background-color: #f5f7fa;
  height: calc(100vh - 60px);
  overflow-y: auto;
}

:deep(.el-menu-item .el-icon) {
  margin-right: 4px;
  vertical-align: middle;
}

:deep(.el-menu-item) {
  min-width: auto !important;
}

:deep(.el-menu--horizontal > .el-sub-menu) {
  display: none !important;
}
</style> 