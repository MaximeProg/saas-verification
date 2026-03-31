'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { AdminUser } from '@/types'

export function useAdminAuth() {
  const router = useRouter()
  const [admin, setAdmin] = useState<AdminUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('admin_token')
    const adminData = localStorage.getItem('admin')

    if (!token || !adminData) {
      router.push('/admin/login')
      return
    }

    try {
      setAdmin(JSON.parse(adminData))
    } catch (error) {
      router.push('/admin/login')
    } finally {
      setLoading(false)
    }
  }, [router])

  const logout = () => {
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin')
    router.push('/admin/login')
  }

  return { admin, loading, logout }
}
