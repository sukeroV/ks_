<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <h2>口算练习系统 - 注册</h2>
      </template>
      
      <el-form :model="registerForm" :rules="rules" ref="registerFormRef" label-width="100px">
        <el-form-item prop="user_id" label="用户ID">
          <el-input v-model="registerForm.user_id" placeholder="请输入用户ID"></el-input>
        </el-form-item>
        
        <el-form-item prop="name" label="姓名">
          <el-input v-model="registerForm.name" placeholder="请输入姓名"></el-input>
        </el-form-item>
        
        <el-form-item prop="id_card" label="身份证号">
          <el-input v-model="registerForm.id_card" placeholder="请输入身份证号"></el-input>
        </el-form-item>
        
        <el-form-item prop="grade" label="年级">
          <el-select v-model="registerForm.grade" placeholder="请选择年级" style="width: 100%">
            <el-option v-for="i in 6" :key="i" :label="`${i}年级`" :value="i"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item prop="password" label="密码">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        
        <el-form-item prop="phone" label="电话">
          <el-input v-model="registerForm.phone" placeholder="请输入电话号码"></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleRegister" style="width: 100%">注册</el-button>
        </el-form-item>
        
        <div class="login-link">
          <router-link to="/login">已有账号？立即登录</router-link>
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
  name: 'Register',
  setup() {
    const router = useRouter()
    const registerFormRef = ref()
    
    const registerForm = reactive({
      user_id: '',
      name: '',
      id_card: '',
      grade: '',
      password: '',
      phone: ''
    })
    
    const rules = {
      user_id: [
        { required: true, message: '请输入用户ID', trigger: 'blur' },
        { min: 3, max: 15, message: '长度在 3 到 15 个字符', trigger: 'blur' }
      ],
      name: [
        { required: true, message: '请输入姓名', trigger: 'blur' }
      ],
      id_card: [
        { required: true, message: '请输入身份证号', trigger: 'blur' },
        { pattern: /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/, message: '请输入正确的身份证号', trigger: 'blur' }
      ],
      grade: [
        { required: true, message: '请选择年级', trigger: 'change' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' }
      ],
      phone: [
        { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
      ]
    }
    
    const handleRegister = async () => {
      if (!registerFormRef.value) return
      
      await registerFormRef.value.validate(async (valid: boolean) => {
        if (valid) {
          try {
            await axios.post('/api/user', registerForm)
            ElMessage.success('注册成功')
            router.push('/login')
          } catch (error: any) {
            const errorMsg = error.response?.data?.error || '注册失败，请稍后重试'
            ElMessage.error(errorMsg)
          }
        }
      })
    }
    
    return {
      registerForm,
      registerFormRef,
      rules,
      handleRegister
    }
  }
})
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.register-card {
  width: 500px;
}

.login-link {
  text-align: center;
  margin-top: 15px;
}

.login-link a {
  color: #409eff;
  text-decoration: none;
}
</style> 