'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Company } from '@/types'
import api from '@/lib/api'

export function useAuth() {
  const router = useRouter()
  const [company, setCompany] = useState<Company | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchCompany = async () => {
      const token = localStorage.getItem('token')

      if (!token) {
        router.push('/company/login')
        return
      }

      try {
        // Récupérer les données de l'entreprise depuis l'API
        const response = await api.get('/companies/me')
        setCompany(response.data)
      } catch (error) {
        console.error('Error fetching company:', error)
        // Token invalide ou expiré
        localStorage.removeItem('token')
        router.push('/company/login')
      } finally {
        setLoading(false)
      }
    }

    fetchCompany()
  }, [router])

  const logout = () => {
    localStorage.removeItem('token')
    router.push('/company/login')
  }

  return { company, loading, logout }
}
