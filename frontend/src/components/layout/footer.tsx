import Link from 'next/link'
import { Shield, Mail, Phone, MapPin, Github, Twitter, Linkedin } from 'lucide-react'

export function Footer() {
  return (
    <footer className="w-full max-w-full overflow-x-hidden bg-muted/30">
      <div className="container mx-auto w-full max-w-full px-4 py-16">
        <div className="grid grid-cols-1 gap-12 md:grid-cols-4">
          <div className="space-y-4 md:col-span-1">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-gradient-to-br from-emerald-600 to-emerald-700 p-2.5 shadow-lg">
                <Shield className="h-6 w-6 text-white" />
              </div>
              <div className="flex flex-col">
                <span className="text-xl font-bold leading-tight">KYC Platform</span>
                <span className="text-xs text-muted-foreground">Vérification d'identité</span>
              </div>
            </div>
            <p className="text-sm leading-relaxed text-muted-foreground">
              Solution professionnelle de vérification d'identité KYC/AML pour entreprises. Sécurisé, rapide et conforme.
            </p>
            <div className="flex gap-3">
              <a href="#" className="rounded-lg bg-muted p-2 transition-colors hover:bg-emerald-600 hover:text-white">
                <Twitter className="h-4 w-4" />
              </a>
              <a href="#" className="rounded-lg bg-muted p-2 transition-colors hover:bg-emerald-600 hover:text-white">
                <Linkedin className="h-4 w-4" />
              </a>
              <a href="#" className="rounded-lg bg-muted p-2 transition-colors hover:bg-emerald-600 hover:text-white">
                <Github className="h-4 w-4" />
              </a>
            </div>
          </div>

          <div>
            <h3 className="mb-6 text-sm font-bold uppercase tracking-wider">Produit</h3>
            <ul className="space-y-3 text-sm">
              <li>
                <Link href="/#features" className="text-muted-foreground hover:text-emerald-600 transition-colors">
                  Fonctionnalités
                </Link>
              </li>
              <li>
                <Link href="/#pricing" className="text-muted-foreground hover:text-emerald-600 transition-colors">
                  Tarifs
                </Link>
              </li>
              <li>
                <Link href="/docs" className="text-muted-foreground hover:text-emerald-600 transition-colors">
                  Documentation
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="mb-6 text-sm font-bold uppercase tracking-wider">Entreprise</h3>
            <ul className="space-y-3 text-sm">
              <li>
                <Link href="/company/login" className="text-muted-foreground hover:text-emerald-600 transition-colors">
                  Connexion
                </Link>
              </li>
              <li>
                <Link href="/company/register" className="text-muted-foreground hover:text-emerald-600 transition-colors">
                  Inscription
                </Link>
              </li>
              <li>
                <Link href="/company/dashboard" className="text-muted-foreground hover:text-emerald-600 transition-colors">
                  Dashboard
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="mb-6 text-sm font-bold uppercase tracking-wider">Contact</h3>
            <ul className="space-y-3 text-sm text-muted-foreground">
              <li className="flex items-center gap-2">
                <Mail className="h-4 w-4" />
                <span>contact@kycplatform.com</span>
              </li>
              <li className="flex items-center gap-2">
                <Phone className="h-4 w-4" />
                <span>+229 XX XX XX XX</span>
              </li>
              <li className="flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                <span>Cotonou, Bénin</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t pt-8 md:flex-row">
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} KYC Platform. Tous droits réservés.
          </p>
          <div className="flex gap-6 text-sm text-muted-foreground">
            <Link href="#" className="transition-colors hover:text-emerald-600">
              Politique de confidentialité
            </Link>
            <Link href="#" className="transition-colors hover:text-emerald-600">
              Conditions d'utilisation
            </Link>
            <Link href="#" className="transition-colors hover:text-emerald-600">
              Mentions légales
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
