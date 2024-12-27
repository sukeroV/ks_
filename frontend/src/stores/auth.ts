import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '@/utils/request'

export const useAuthStore = defineStore('auth', () => {
    const token = ref(localStorage.getItem('token') || '')
    const user = ref(JSON.parse(localStorage.getItem('user') || '{}'))

    async function login(username: string, password: string) {
        const { data } = await request.post('/auth/login', {
            username,
            password
        })
        
        token.value = data.token
        user.value = data.user
        
        localStorage.setItem('token', data.token)
        localStorage.setItem('user', JSON.stringify(data.user))
    }

    async function verifyToken() {
        if (!token.value) return false
        
        try {
            const { data } = await request.post('/auth/verify')
            user.value = data.user
            return true
        } catch {
            logout()
            return false
        }
    }

    function logout() {
        token.value = ''
        user.value = {}
        localStorage.removeItem('token')
        localStorage.removeItem('user')
    }

    return {
        token,
        user,
        login,
        logout,
        verifyToken
    }
}) 