'use client'

import Link from 'next/link'
import { useState } from 'react'
import { Menu, X, Shield } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ThemeToggle } from '@/components/theme-toggle'

export function Navbar() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <nav className="sticky top-0 z-50 w-full max-w-full overflow-x-hidden bg-background/95 backdrop-blur-md shadow-sm supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto w-full max-w-full px-4">
        <div className="flex h-16 items-center justify-between md:h-20">
          <div className="flex items-center gap-2 md:gap-3">
            <Link href="/" className="flex items-center gap-2 transition-opacity hover:opacity-80 md:gap-3">
              <div className="rounded-lg bg-gradient-to-br from-emerald-600 to-emerald-700 p-2 shadow-lg md:rounded-xl md:p-2.5">
                <Shield className="h-5 w-5 text-white md:h-6 md:w-6" />
              </div>
              <div className="flex flex-col">
                <span className="text-base font-bold leading-tight md:text-xl">KYC Platform</span>
                <span className="hidden text-xs text-muted-foreground md:inline">Vérification d'identité</span>
              </div>
            </Link>
          </div>

          <div className="hidden md:flex md:items-center md:gap-8">
            <Link href="/#features" className="text-sm font-medium transition-colors hover:text-emerald-600">
              Fonctionnalités
            </Link>
            <Link href="/#pricing" className="text-sm font-medium transition-colors hover:text-emerald-600">
              Tarifs
            </Link>
            <Link href="/docs" target="_blank" rel="noopener noreferrer" className="text-sm font-medium transition-colors hover:text-emerald-600">
              Documentation
            </Link>
            <div className="h-6 w-px bg-border" />
            <Link href="/company/login" className="text-sm font-medium transition-colors hover:text-emerald-600">
              Connexion
            </Link>
            <Link href="/company/register">
              <Button size="lg" className="shadow-md">
                Commencer Gratuitement
              </Button>
            </Link>
            <ThemeToggle />
          </div>

          <div className="flex items-center gap-2 md:hidden">
            <ThemeToggle />
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsOpen(!isOpen)}
            >
              {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>

        {isOpen && (
          <div className="border-t py-4 md:hidden">
            <div className="flex flex-col gap-4">
              <Link
                href="/#features"
                className="text-sm font-medium hover:text-emerald-600 transition-colors"
                onClick={() => setIsOpen(false)}
              >
                Fonctionnalités
              </Link>
              <Link
                href="/#pricing"
                className="text-sm font-medium hover:text-emerald-600 transition-colors"
                onClick={() => setIsOpen(false)}
              >
                Tarifs
              </Link>
              <Link
                href="/docs"
                className="text-sm font-medium hover:text-emerald-600 transition-colors"
                onClick={() => setIsOpen(false)}
              >
                Documentation
              </Link>
              <Link
                href="/company/login"
                className="text-sm font-medium hover:text-emerald-600 transition-colors"
                onClick={() => setIsOpen(false)}
              >
                Connexion
              </Link>
              <Link href="/company/register" onClick={() => setIsOpen(false)}>
                <Button className="w-full">Commencer</Button>
              </Link>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
