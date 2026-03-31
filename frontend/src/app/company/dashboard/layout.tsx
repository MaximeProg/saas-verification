'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Shield, Key, FileCheck, CreditCard, LogOut, Menu, X, BarChart, Settings } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ThemeToggle } from '@/components/theme-toggle'
import { useAuth } from '@/hooks/useAuth'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const pathname = usePathname()
  const { company, loading, logout } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="mb-4 inline-flex rounded-lg bg-emerald-600 p-3">
            <Shield className="h-8 w-8 animate-pulse text-white" />
          </div>
          <p className="text-muted-foreground">Chargement...</p>
        </div>
      </div>
    )
  }

  const menuItems = [
    { href: '/company/dashboard', label: 'Dashboard', icon: BarChart },
    { href: '/company/dashboard/verifications', label: 'Vérifications', icon: FileCheck },
    { href: '/company/dashboard/api-keys', label: 'Clés API', icon: Key },
    { href: '/company/dashboard/subscription', label: 'Abonnement', icon: CreditCard },
    { href: '/company/dashboard/settings', label: 'Paramètres', icon: Settings },
  ]

  return (
    <div className="flex min-h-screen bg-background">
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 h-screen flex flex-col transform border-r bg-card transition-transform duration-200 ease-in-out lg:translate-x-0 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex h-16 items-center gap-2 border-b px-6 flex-shrink-0">
          <div className="rounded-lg bg-emerald-600 p-2">
            <Shield className="h-5 w-5 text-white" />
          </div>
          <span className="text-lg font-bold">KYC Platform</span>
        </div>

        <nav className="flex-1 overflow-y-auto space-y-1 p-4">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = pathname === item.href
            return (
              <Link key={item.href} href={item.href}>
                <Button
                  variant={isActive ? 'default' : 'ghost'}
                  className="w-full justify-start"
                >
                  <Icon className="mr-2 h-4 w-4" />
                  {item.label}
                </Button>
              </Link>
            )
          })}
        </nav>

        <div className="border-t p-4 flex-shrink-0">
          <div className="mb-2 text-sm">
            <p className="font-medium">{company?.company_name}</p>
            <p className="text-xs text-muted-foreground">{company?.email}</p>
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

      <div className="flex-1 lg:ml-64">
        <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b bg-background px-6">
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
          <div className="ml-auto flex items-center gap-2">
            <ThemeToggle />
          </div>
        </header>

        <main className="p-6">{children}</main>
      </div>
    </div>
  )
}
