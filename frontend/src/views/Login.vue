<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2>口算练习系统 - 登录</h2>
      </template>
      
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef">
        <el-form-item prop="user_id" label="用户">
          <el-input v-model="loginForm.user_id" placeholder="请输入用户ID"></el-input>
        </el-form-item>
        
        <el-form-item prop="password" label="密码">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleLogin" style="width: 100%">登录</el-button>
        </el-form-item>
        
        <div class="register-link">
          <router-link to="/register">没有账号？立即注册</router-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import axios from 'axios'

export default defineComponent({
  name: 'Login',
  setup() {
    const router = useRouter()
    const loginFormRef = ref()
    
    const loginForm = reactive({
      user_id: '',
      password: ''
    })
    
    const rules = {
      user_id: [
        { required: true, message: '请输入用户ID', trigger: 'blur' },
        { min: 3, max: 15, message: '长度在 3 到 15 个字符', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
      ]
    }
    
    const handleLogin = async () => {
      if (!loginFormRef.value) return
      
      await loginFormRef.value.validate(async (valid: boolean) => {
        if (valid) {
          try {
            const response = await axios.post('/api/login', loginForm)
            localStorage.setItem('user', JSON.stringify(response.data))
            ElMessage.success('登录成功')
            router.push('/practice')
          } catch (error: any) {
            const errorMsg = error.response?.data?.error || '登录失败，请稍后重试'
            ElMessage.error(errorMsg)
          }
        }
      })
    }
    
    return {
      loginForm,
      loginFormRef,
      rules,
      handleLogin
    }
  }
})
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.login-card {
  width: 400px;
}

.register-link {
  text-align: center;
  margin-top: 15px;
}

.register-link a {
  color: #409eff;
  text-decoration: none;
}
</style> 