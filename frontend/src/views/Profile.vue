<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <!-- 左侧个人信息卡片 -->
      <el-col :span="12">
        <el-card class="profile-card">
          <template #header>
            <div class="card-header">
              <el-avatar :size="80" :icon="UserFilled" />
              <h2>{{ profileForm.name }}</h2>
              <div class="user-info">
                <span>{{ profileForm.grade }}年级</span>
                <el-tag size="small" type="info" class="user-id">ID: {{ profileForm.user_id }}</el-tag>
              </div>
            </div>
          </template>
          
          <el-descriptions direction="vertical" :column="1" border>
            <el-descriptions-item label="姓名">{{ profileForm.name }}</el-descriptions-item>
            <el-descriptions-item label="身份证号">{{ profileForm.id_card }}</el-descriptions-item>
            <el-descriptions-item label="年级">{{ profileForm.grade }}年级</el-descriptions-item>
            <el-descriptions-item label="手机号码">{{ profileForm.phone || '未设置' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <!-- 右侧修改信息表单 -->
      <el-col :span="12">
        <el-card class="edit-card">
          <template #header>
            <div class="edit-header">
              <h3>修改信息</h3>
            </div>
          </template>
          
          <el-form 
            :model="profileForm" 
            :rules="rules" 
            ref="profileFormRef"
            label-width="80px"
            class="edit-form"
          >
            <el-form-item label="姓名" prop="name">
              <el-input v-model="profileForm.name"></el-input>
            </el-form-item>
            
            <el-form-item label="年级" prop="grade">
              <el-select v-model="profileForm.grade" style="width: 100%">
                <el-option 
                  v-for="i in 6" 
                  :key="i" 
                  :label="`${i}年级`" 
                  :value="i"
                ></el-option>
              </el-select>
            </el-form-item>
            
            <el-form-item label="手机号码" prop="phone">
              <el-input v-model="profileForm.phone" placeholder="请输入手机号码"></el-input>
            </el-form-item>
            
            <el-divider content-position="left">修改密码</el-divider>
            
            <el-form-item label="新密码" prop="newPassword">
              <el-input 
                v-model="profileForm.newPassword" 
                type="password"
                placeholder="不修改请留空"
                show-password
              ></el-input>
            </el-form-item>
            
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input 
                v-model="profileForm.confirmPassword" 
                type="password"
                placeholder="不修改请留空"
                show-password
              ></el-input>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="handleUpdate">保存修改</el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { UserFilled } from '@element-plus/icons-vue'
import axios from 'axios'

export default defineComponent({
  name: 'Profile',
  setup() {
    const profileFormRef = ref()
    const profileForm = reactive({
      user_id: '',
      name: '',
      id_card: '',
      grade: '',
      phone: '',
      newPassword: '',
      confirmPassword: ''
    })
    
    const validatePass = (rule: any, value: string, callback: any) => {
      if (value === '') {
        callback()
      } else if (value.length < 6) {
        callback(new Error('密码不能少于6个字符'))
      } else {
        if (profileForm.confirmPassword !== '') {
          profileFormRef.value.validateField('confirmPassword')
        }
        callback()
      }
    }
    
    const validatePass2 = (rule: any, value: string, callback: any) => {
      if (value === '') {
        callback()
      } else if (value !== profileForm.newPassword) {
        callback(new Error('两次输入密码不一致!'))
      } else {
        callback()
      }
    }
    
    const rules = {
      name: [
        { required: true, message: '请输入姓名', trigger: 'blur' }
      ],
      grade: [
        { required: true, message: '请选择年级', trigger: 'change' }
      ],
      phone: [
        { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
      ],
      newPassword: [
        { validator: validatePass, trigger: 'blur' }
      ],
      confirmPassword: [
        { validator: validatePass2, trigger: 'blur' }
      ]
    }
    
    onMounted(() => {
      const userStr = localStorage.getItem('user')
      if (userStr) {
        const user = JSON.parse(userStr)
        // 获取用户详细信息
        axios.get(`/api/user/${user.user_id}`)
          .then(response => {
            const userData = response.data
            profileForm.user_id = userData.user_id
            profileForm.name = userData.name
            profileForm.id_card = userData.id_card
            profileForm.grade = userData.grade
            profileForm.phone = userData.phone || ''
          })
          .catch(error => {
            ElMessage.error('获取用户信息失败')
          })
      }
    })
    
    const handleUpdate = async () => {
      if (!profileFormRef.value) return
      
      await profileFormRef.value.validate(async (valid: boolean) => {
        if (valid) {
          try {
            const updateData = {
              name: profileForm.name,
              grade: profileForm.grade,
              phone: profileForm.phone
            }
            
            if (profileForm.newPassword) {
              updateData['password'] = profileForm.newPassword
            }
            
            await axios.put(`/api/user/${profileForm.user_id}`, updateData)
            ElMessage.success('个人信息更新成功')
            
            // 更新本地存储的用户信息
            const userStr = localStorage.getItem('user')
            if (userStr) {
              const user = JSON.parse(userStr)
              user.name = profileForm.name
              user.grade = profileForm.grade
              localStorage.setItem('user', JSON.stringify(user))
            }
          } catch (error: any) {
            ElMessage.error(error.response?.data?.error || '更新失败')
          }
        }
      })
    }
    
    const resetForm = () => {
      if (profileFormRef.value) {
        profileFormRef.value.resetFields()
      }
    }
    
    return {
      profileForm,
      profileFormRef,
      rules,
      handleUpdate,
      resetForm,
      UserFilled
    }
  }
})
</script>

<style scoped>
.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.card-header {
  text-align: center;
  padding: 20px 0;
}

.card-header h2 {
  margin: 16px 0 8px;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.user-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #606266;
  font-size: 14px;
}

.user-id {
  font-size: 12px;
}

.profile-card {
  height: 100%;
}

.edit-card {
  height: 100%;
}

.edit-header {
  padding: 8px 0;
}

.edit-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.edit-form {
  padding: 20px 0;
}

:deep(.el-descriptions) {
  padding: 0 20px;
}

:deep(.el-descriptions__label) {
  width: 80px;
  font-weight: bold;
  color: #606266;
}

:deep(.el-descriptions__content) {
  padding: 16px;
  font-size: 14px;
}

:deep(.el-descriptions__body) {
  background-color: #fafafa;
}

:deep(.el-descriptions__row) {
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-descriptions__row:last-child) {
  border-bottom: none;
}

.el-divider {
  margin: 24px 0;
}

:deep(.el-form-item) {
  margin-bottom: 22px;
}

:deep(.el-input), :deep(.el-select) {
  width: 100%;
}
</style> 