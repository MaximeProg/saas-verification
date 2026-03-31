'use client'

import { useEffect, useState } from 'react'
import { Shield, Users, FileCheck, CreditCard, LogOut, Menu, X, BarChart, Settings, Package } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ThemeToggle } from '@/components/theme-toggle'
import { useAdminAuth } from '@/hooks/useAdminAuth'
import api from '@/lib/api'

export default function AdminDashboardPage() {
  const { admin, loading, logout } = useAdminAuth()
  const [stats, setStats] = useState({
    total_companies: 0,
    active_companies: 0,
    total_verifications: 0,
    total_revenue: 0,
  })
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    if (admin) {
      fetchStats()
    }
  }, [admin])

  const fetchStats = async () => {
    try {
      const response = await api.get('/admin/stats', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('admin_token')}`
        }
      })
      setStats(response.data)
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="mb-4 inline-flex rounded-lg bg-rose-600 p-3">
            <Shield className="h-8 w-8 animate-pulse text-white" />
          </div>
          <p className="text-muted-foreground">Chargement...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen bg-background">
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 transform border-r bg-card transition-transform duration-200 ease-in-out lg:relative lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-16 items-center gap-2 border-b px-6">
          <div className="rounded-lg bg-rose-600 p-2">
            <Shield className="h-5 w-5 text-white" />
          </div>
          <span className="text-lg font-bold">Admin Panel</span>
        </div>

        <nav className="space-y-1 p-4">
          <Button variant="destructive" className="w-full justify-start">
            <BarChart className="mr-2 h-4 w-4" />
            Dashboard
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <Users className="mr-2 h-4 w-4" />
            Entreprises
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <FileCheck className="mr-2 h-4 w-4" />
            Vérifications
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <Package className="mr-2 h-4 w-4" />
            Plans d'abonnement
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <CreditCard className="mr-2 h-4 w-4" />
            Paiements
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <Settings className="mr-2 h-4 w-4" />
            Paramètres
          </Button>
        </nav>

        <div className="absolute bottom-0 w-full border-t p-4">
          <div className="mb-2 text-sm">
            <p className="font-medium">{admin?.full_name}</p>
            <p className="text-xs text-muted-foreground">{admin?.role}</p>
          </div>
          <Button variant="outline" className="w-full" onClick={logout}>
            <LogOut className="mr-2 h-4 w-4" />
            Déconnexion
          </Button>
        </div>
      </aside>

      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <div className="flex-1">
        <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-background px-6">
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
          <h1 className="text-xl font-semibold">Dashboard Administrateur</h1>
          <div className="ml-auto flex items-center gap-2">
            <Badge variant="destructive">Admin</Badge>
            <ThemeToggle />
          </div>
        </header>

        <main className="p-6">
          <div className="mb-6">
            <h2 className="text-2xl font-bold">Bienvenue, {admin?.full_name}</h2>
            <p className="text-muted-foreground">
              Vue d'ensemble de la plateforme
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Entreprises</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total_companies}</div>
                <p className="text-xs text-muted-foreground">
                  {stats.active_companies} actives
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Vérifications</CardTitle>
                <FileCheck className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total_verifications}</div>
                <p className="text-xs text-muted-foreground">Total effectuées</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Revenus</CardTitle>
                <CreditCard className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total_revenue.toLocaleString()} FCFA</div>
                <p className="text-xs text-muted-foreground">Ce mois</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Taux d'activité</CardTitle>
                <BarChart className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {stats.total_companies > 0 
                    ? ((stats.active_companies / stats.total_companies) * 100).toFixed(1)
                    : 0}%
                </div>
                <p className="text-xs text-muted-foreground">Entreprises actives</p>
              </CardContent>
            </Card>
          </div>

          <div className="mt-6 grid gap-6 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Dernières entreprises</CardTitle>
                <CardDescription>
                  Entreprises récemment inscrites
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Entreprise Example SARL</p>
                      <p className="text-sm text-muted-foreground">contact@example.com</p>
                    </div>
                    <Badge>Actif</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Tech Solutions</p>
                      <p className="text-sm text-muted-foreground">info@techsolutions.com</p>
                    </div>
                    <Badge>Actif</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Digital Services</p>
                      <p className="text-sm text-muted-foreground">hello@digital.com</p>
                    </div>
                    <Badge variant="secondary">Inactif</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Derniers paiements</CardTitle>
                <CardDescription>
                  Paiements récents effectués
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Plan Professional</p>
                      <p className="text-sm text-muted-foreground">Entreprise Example</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">50,000 FCFA</p>
                      <Badge className="mt-1">Complété</Badge>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Plan Starter</p>
                      <p className="text-sm text-muted-foreground">Tech Solutions</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">15,000 FCFA</p>
                      <Badge className="mt-1">Complété</Badge>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Plan Enterprise</p>
                      <p className="text-sm text-muted-foreground">Digital Services</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">150,000 FCFA</p>
                      <Badge variant="secondary" className="mt-1">En attente</Badge>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}
