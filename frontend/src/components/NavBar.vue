<template>
  <el-menu
    :default-active="activeIndex"
    mode="horizontal"
    router
  >
    <el-menu-item index="/">
      <el-icon><Edit /></el-icon>
      开始练习
    </el-menu-item>
    <el-menu-item index="/home">
      <el-icon><House /></el-icon>
      首页
    </el-menu-item>
    <!-- ... 其他菜单项保持不变 ... -->
  </el-menu>
</template> 