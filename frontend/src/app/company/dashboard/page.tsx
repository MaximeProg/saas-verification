'use client'

import { useEffect, useState } from 'react'
import { FileCheck, CreditCard } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/hooks/useAuth'
import api from '@/lib/api'

export default function DashboardPage() {
  const { company } = useAuth()
  const [stats, setStats] = useState({
    total_verifications: 0,
    pending: 0,
    verified: 0,
    rejected: 0,
  })

  useEffect(() => {
    if (company) {
      fetchStats()
    }
  }, [company])

  const fetchStats = async () => {
    try {
      const response = await api.get('/verifications/stats')
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const quotaPercentage = company ? (company.quota_used / company.monthly_quota) * 100 : 0

  return (
    <div>
          <div className="mb-6">
            <h2 className="text-2xl font-bold">Bienvenue, {company?.company_name}</h2>
            <p className="text-muted-foreground">
              Voici un aperçu de votre activité
            </p>
          </div>

          <div className="mb-6">
            <Card>
              <CardHeader>
                <CardTitle>Quota mensuel</CardTitle>
                <CardDescription>
                  {company?.quota_used} / {company?.monthly_quota} vérifications utilisées
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
                    <div
                      className="h-full bg-emerald-600 transition-all"
                      style={{ width: `${Math.min(quotaPercentage, 100)}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>{quotaPercentage.toFixed(1)}% utilisé</span>
                    <span>{company?.monthly_quota - (company?.quota_used || 0)} restantes</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total</CardTitle>
                <FileCheck className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total_verifications}</div>
                <p className="text-xs text-muted-foreground">Vérifications totales</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">En attente</CardTitle>
                <Badge variant="secondary">{stats.pending}</Badge>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.pending}</div>
                <p className="text-xs text-muted-foreground">En cours de traitement</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Vérifiées</CardTitle>
                <Badge className="bg-emerald-600">{stats.verified}</Badge>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.verified}</div>
                <p className="text-xs text-muted-foreground">Identités vérifiées</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Rejetées</CardTitle>
                <Badge variant="destructive">{stats.rejected}</Badge>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.rejected}</div>
                <p className="text-xs text-muted-foreground">Vérifications rejetées</p>
              </CardContent>
            </Card>
          </div>

      <div className="mt-6">
        <Card>
          <CardHeader>
            <CardTitle>Abonnement actuel</CardTitle>
            <CardDescription>
              {company?.subscription_plan || 'Aucun plan actif'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Statut</span>
                <Badge variant={company?.status === 'sandbox' ? 'secondary' : 'default'}>
                  {company?.status === 'sandbox' ? 'Mode Test' : 'Production'}
                </Badge>
              </div>
              {company?.subscription_expires_at && (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Expire le</span>
                  <span className="text-sm font-medium">
                    {new Date(company.subscription_expires_at).toLocaleDateString('fr-FR')}
                  </span>
                </div>
              )}
              <Button className="w-full">
                <CreditCard className="mr-2 h-4 w-4" />
                Gérer l'abonnement
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
