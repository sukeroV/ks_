<template>
  <el-config-provider>
    <router-view></router-view>
  </el-config-provider>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { ElConfigProvider } from 'element-plus'

export default defineComponent({
  name: 'App',
  components: {
    ElConfigProvider
  }
})
</script>

<style>
/* 移除最外层滚动条 */
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow: hidden;
}

#app {
  height: 100%;
  overflow: hidden;
}

/* 让每个页面的根容器自己处理滚动 */
.practice-container,
.mistakes-container,
.profile-container,
.home-container,
.practice-detail-container {
  height: 100%;
  overflow-y: auto;
  padding: 20px;
  box-sizing: border-box;
}

/* 美化内部滚动条 */
.practice-container::-webkit-scrollbar,
.mistakes-container::-webkit-scrollbar,
.profile-container::-webkit-scrollbar,
.home-container::-webkit-scrollbar,
.practice-detail-container::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.practice-container::-webkit-scrollbar-thumb,
.mistakes-container::-webkit-scrollbar-thumb,
.profile-container::-webkit-scrollbar-thumb,
.home-container::-webkit-scrollbar-thumb,
.practice-detail-container::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 3px;
}

.practice-container::-webkit-scrollbar-track,
.mistakes-container::-webkit-scrollbar-track,
.profile-container::-webkit-scrollbar-track,
.home-container::-webkit-scrollbar-track,
.practice-detail-container::-webkit-scrollbar-track {
  background: #f5f7fa;
  border-radius: 3px;
}
</style> 