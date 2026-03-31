'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Shield, Zap, Lock, CheckCircle, ArrowRight, Code, Users, ChevronDown, ChevronUp, Smartphone, Globe, FileCheck } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Navbar } from '@/components/layout/navbar'
import { Footer } from '@/components/layout/footer'

interface SubscriptionPlan {
  id: string
  name: string
  slug: string
  description: string
  price: number
  currency: string
  billing_period: string
  monthly_quota: number
  max_api_keys: number
  max_users: number
  advantages: string[]
  is_popular: boolean
  display_order: number
  has_webhook_support: boolean
  has_priority_support: boolean
  has_custom_branding: boolean
  has_api_access: boolean
  has_bulk_upload: boolean
  has_advanced_analytics: boolean
}

export default function HomePage() {
  const [openFaq, setOpenFaq] = useState<number | null>(null)
  const [plans, setPlans] = useState<SubscriptionPlan[]>([])
  const [loadingPlans, setLoadingPlans] = useState(true)

  const toggleFaq = (index: number) => {
    setOpenFaq(openFaq === index ? null : index)
  }

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/subscription-plans/public')
        if (response.ok) {
          const data = await response.json()
          setPlans(data)
        }
      } catch (error) {
        console.error('Erreur lors du chargement des plans:', error)
      } finally {
        setLoadingPlans(false)
      }
    }

    fetchPlans()
  }, [])

  return (
    <div className="flex min-h-screen flex-col overflow-x-hidden">
      <Navbar />
      
      <main className="flex-1 overflow-x-hidden w-full">
        <section className="container mx-auto px-4 py-12 md:py-16 lg:py-24">
          <div className="grid items-center gap-8 md:gap-12 lg:gap-16 lg:grid-cols-2">
            <div>
              <h1 className="mb-4 text-3xl font-bold leading-tight tracking-tight sm:text-4xl md:text-5xl lg:text-6xl">
                Plateforme de Vérification d'Identité KYC
              </h1>
              <p className="mb-6 text-base leading-relaxed text-muted-foreground sm:text-lg md:text-xl">
                Gérez les vérifications d'identité de vos utilisateurs avec notre plateforme sécurisée. 
                API REST complète, webhooks en temps réel et dashboards intuitifs.
              </p>
              <div className="flex flex-col gap-4 sm:flex-row">
                <Link href="/company/register">
                  <Button size="lg" className="w-full sm:w-auto">
                    Commencer Gratuitement
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
                <Link href="/docs">
                  <Button size="lg" variant="outline" className="w-full sm:w-auto">
                    Documentation API
                  </Button>
                </Link>
              </div>
            </div>

            <div className="relative w-full">
              <div className="aspect-[4/3] w-full overflow-hidden rounded-2xl bg-muted/50">
                <img 
                  src="https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&h=600&fit=crop" 
                  alt="Vérification d'identité sécurisée"
                  className="h-full w-full max-w-full object-cover"
                />
              </div>
            </div>
          </div>
        </section>

        <section id="features" className="py-12 md:py-16 lg:py-24">
          <div className="container mx-auto px-4">
            <div className="mx-auto mb-8 max-w-3xl text-center md:mb-12 lg:mb-16">
              <h2 className="mb-3 text-2xl font-bold tracking-tight sm:text-3xl md:text-4xl lg:text-5xl">
                Pourquoi Choisir Notre Plateforme ?
              </h2>
              <p className="text-base text-muted-foreground sm:text-lg md:text-xl">
                Des fonctionnalités puissantes pour simplifier vos vérifications KYC
              </p>
            </div>

            <div className="mb-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3 md:mb-12 lg:mb-16">
              <Card className="group overflow-hidden border-2 transition-all hover:shadow-lg">
                <div className="aspect-video overflow-hidden bg-gradient-to-br from-muted to-muted/50">
                  <img 
                    src="https://images.unsplash.com/photo-1633265486064-086b219458ec?w=600&h=400&fit=crop" 
                    alt="Sécurité"
                    className="h-full w-full object-cover transition-transform group-hover:scale-105"
                  />
                </div>
                <CardHeader className="pb-4">
                  <div className="mb-2 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
                    <Shield className="h-6 w-6" />
                  </div>
                  <CardTitle className="text-xl">Sécurité Maximale</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="leading-relaxed text-muted-foreground">
                    Authentification JWT, chiffrement SSL/TLS et stockage sécurisé. Vos données sont protégées à 100%.
                  </p>
                </CardContent>
              </Card>

              <Card className="group overflow-hidden border-2 transition-all hover:shadow-lg">
                <div className="aspect-video overflow-hidden bg-gradient-to-br from-muted to-muted/50">
                  <img 
                    src="https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=600&h=400&fit=crop" 
                    alt="Gestion"
                    className="h-full w-full object-cover transition-transform group-hover:scale-105"
                  />
                </div>
                <CardHeader className="pb-4">
                  <div className="mb-2 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
                    <FileCheck className="h-6 w-6" />
                  </div>
                  <CardTitle className="text-xl">Gestion Simplifiée</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="leading-relaxed text-muted-foreground">
                    Dashboard intuitif pour créer, suivre et gérer toutes vos vérifications en temps réel.
                  </p>
                </CardContent>
              </Card>

              <Card className="group overflow-hidden border-2 transition-all hover:shadow-lg">
                <div className="aspect-video overflow-hidden bg-gradient-to-br from-muted to-muted/50">
                  <img 
                    src="https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&h=400&fit=crop" 
                    alt="API"
                    className="h-full w-full object-cover transition-transform group-hover:scale-105"
                  />
                </div>
                <CardHeader className="pb-4">
                  <div className="mb-2 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
                    <Code className="h-6 w-6" />
                  </div>
                  <CardTitle className="text-xl">API Puissante</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="leading-relaxed text-muted-foreground">
                    API REST complète et documentée. Intégration en quelques minutes avec vos applications.
                  </p>
                </CardContent>
              </Card>

              <Card className="group overflow-hidden border-2 transition-all hover:shadow-lg">
                <div className="aspect-video overflow-hidden bg-gradient-to-br from-muted to-muted/50">
                  <img 
                    src="https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=600&h=400&fit=crop" 
                    alt="Équipe"
                    className="h-full w-full object-cover transition-transform group-hover:scale-105"
                  />
                </div>
                <CardHeader className="pb-4">
                  <div className="mb-2 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
                    <Users className="h-6 w-6" />
                  </div>
                  <CardTitle className="text-xl">Multi-entreprises</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="leading-relaxed text-muted-foreground">
                    Gérez plusieurs entreprises avec quotas personnalisés et statistiques détaillées.
                  </p>
                </CardContent>
              </Card>

              <Card className="group overflow-hidden border-2 transition-all hover:shadow-lg">
                <div className="aspect-video overflow-hidden bg-gradient-to-br from-muted to-muted/50">
                  <img 
                    src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&h=400&fit=crop" 
                    alt="Analytics"
                    className="h-full w-full object-cover transition-transform group-hover:scale-105"
                  />
                </div>
                <CardHeader className="pb-4">
                  <div className="mb-2 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
                    <Zap className="h-6 w-6" />
                  </div>
                  <CardTitle className="text-xl">Notifications Temps Réel</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="leading-relaxed text-muted-foreground">
                    Webhooks automatiques pour chaque événement. Restez informé en temps réel.
                  </p>
                </CardContent>
              </Card>

              <Card className="group overflow-hidden border-2 transition-all hover:shadow-lg">
                <div className="aspect-video overflow-hidden bg-gradient-to-br from-muted to-muted/50">
                  <img 
                    src="https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=600&h=400&fit=crop" 
                    alt="Mobile"
                    className="h-full w-full object-cover transition-transform group-hover:scale-105"
                  />
                </div>
                <CardHeader className="pb-4">
                  <div className="mb-2 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
                    <Smartphone className="h-6 w-6" />
                  </div>
                  <CardTitle className="text-xl">Sessions Sécurisées</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="leading-relaxed text-muted-foreground">
                    Liens uniques avec expiration automatique. Vos utilisateurs uploadent leurs documents en toute sécurité.
                  </p>
                </CardContent>
              </Card>
            </div>

            <div className="mt-8 overflow-hidden rounded-2xl bg-muted/50 md:mt-12 lg:mt-16">
              <div className="grid items-center gap-6 md:gap-8 lg:grid-cols-2">
                <div className="p-6 sm:p-8 lg:p-12">
                  <h3 className="mb-3 text-xl font-bold sm:text-2xl md:text-3xl">
                    Intégration Simple et Rapide
                  </h3>
                  <p className="mb-4 text-base text-muted-foreground sm:mb-6 sm:text-lg">
                    Notre API REST vous permet d'intégrer la vérification KYC dans votre application en quelques minutes. 
                    Documentation complète, exemples de code et support technique inclus.
                  </p>
                  <ul className="space-y-3">
                    <li className="flex items-start gap-3">
                      <CheckCircle className="mt-1 h-5 w-5 flex-shrink-0" />
                      <span>Documentation Swagger interactive</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <CheckCircle className="mt-1 h-5 w-5 flex-shrink-0" />
                      <span>Exemples de code prêts à l'emploi</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <CheckCircle className="mt-1 h-5 w-5 flex-shrink-0" />
                      <span>Webhooks pour notifications temps réel</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <CheckCircle className="mt-1 h-5 w-5 flex-shrink-0" />
                      <span>Gestion multi-clés API</span>
                    </li>
                  </ul>
                </div>
                <div className="h-full">
                  <img 
                    src="https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800&h=600&fit=crop" 
                    alt="Développement"
                    className="h-full w-full object-cover"
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="bg-muted/30 py-12 md:py-16 lg:py-24">
          <div className="container mx-auto px-4">
            <div className="mx-auto mb-8 max-w-3xl text-center md:mb-12 lg:mb-16">
              <h2 className="mb-3 text-2xl font-bold tracking-tight sm:text-3xl md:text-4xl lg:text-5xl">
                Intégration Facile
              </h2>
              <p className="text-base text-muted-foreground sm:text-lg md:text-xl">
                API REST et webhooks pour intégrer la vérification KYC dans vos applications
              </p>
            </div>

            <div className="grid gap-6 md:gap-8 lg:grid-cols-2">
              <Card className="overflow-hidden border-2">
                <div className="aspect-video overflow-hidden bg-gradient-to-br from-blue-500/10 to-blue-600/10">
                  <img 
                    src="https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&h=400&fit=crop" 
                    alt="API REST"
                    className="h-full w-full object-cover opacity-80"
                  />
                </div>
                <CardHeader>
                  <div className="mb-3 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
                    <Code className="h-6 w-6" />
                  </div>
                  <CardTitle className="text-2xl">API REST Complète</CardTitle>
                  <CardDescription>Documentation interactive avec Swagger</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-muted-foreground">
                    API REST documentée avec tous les endpoints nécessaires pour créer, gérer et suivre vos vérifications.
                  </p>
                  <Link href="/docs" className="block">
                    <Button className="w-full">
                      Voir la Documentation
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                </CardContent>
              </Card>

              <Card className="overflow-hidden border-2">
                <div className="aspect-video overflow-hidden bg-gradient-to-br from-green-500/10 to-green-600/10">
                  <img 
                    src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&h=400&fit=crop" 
                    alt="Webhooks"
                    className="h-full w-full object-cover opacity-80"
                  />
                </div>
                <CardHeader>
                  <div className="mb-3 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
                    <Globe className="h-6 w-6" />
                  </div>
                  <CardTitle className="text-2xl">Webhooks Temps Réel</CardTitle>
                  <CardDescription>Notifications automatiques</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-muted-foreground">
                    Configurez vos webhooks pour recevoir des notifications automatiques à chaque changement de statut.
                  </p>
                  <Link href="/docs" className="block">
                    <Button className="w-full">
                      Configurer Webhooks
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        <section className="border-t bg-muted/30 py-16 md:py-24">
          <div className="container mx-auto px-4">
            <div className="mx-auto mb-8 max-w-2xl text-center md:mb-12">
              <h2 className="mb-3 text-2xl font-bold tracking-tight sm:text-3xl md:text-4xl">
                Questions Fréquentes (FAQ)
              </h2>
              <p className="text-base text-muted-foreground sm:text-lg">
                Trouvez les réponses à vos questions les plus fréquentes
              </p>
            </div>

            <div className="space-y-4">
              <Card className="cursor-pointer" onClick={() => toggleFaq(0)}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">Comment créer une vérification via l'API ?</CardTitle>
                    {openFaq === 0 ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
                  </div>
                </CardHeader>
                {openFaq === 0 && (
                  <CardContent>
                    <div className="grid gap-6 md:grid-cols-2">
                      <div>
                        <p className="text-muted-foreground">
                          Utilisez l'endpoint POST /api/v1/verifications avec votre clé API. Fournissez les informations de l'utilisateur 
                          (nom, email, référence externe) et recevez un lien de vérification unique.
                        </p>
                      </div>
                      <div className="overflow-hidden rounded-lg">
                        <img 
                          src="https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=600&h=400&fit=crop" 
                          alt="API Documentation"
                          className="h-full w-full object-cover"
                        />
                      </div>
                    </div>
                  </CardContent>
                )}
              </Card>

              <Card className="cursor-pointer" onClick={() => toggleFaq(1)}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">Comment fonctionnent les webhooks ?</CardTitle>
                    {openFaq === 1 ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
                  </div>
                </CardHeader>
                {openFaq === 1 && (
                  <CardContent>
                    <div className="grid gap-6 md:grid-cols-2">
                      <div>
                        <p className="text-muted-foreground">
                          Configurez une URL webhook dans votre dashboard. Vous recevrez des notifications automatiques 
                          pour chaque changement de statut : pending, approved, rejected.
                        </p>
                      </div>
                      <div className="overflow-hidden rounded-lg">
                        <img 
                          src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&h=400&fit=crop" 
                          alt="Webhooks Configuration"
                          className="h-full w-full object-cover"
                        />
                      </div>
                    </div>
                  </CardContent>
                )}
              </Card>

              <Card className="cursor-pointer" onClick={() => toggleFaq(2)}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">Comment sont stockés les documents ?</CardTitle>
                    {openFaq === 2 ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
                  </div>
                </CardHeader>
                {openFaq === 2 && (
                  <CardContent>
                    <div className="grid gap-6 md:grid-cols-2">
                      <div>
                        <p className="text-muted-foreground">
                          Les documents uploadés sont stockés de manière sécurisée avec URLs accessibles via l'API. 
                          Chaque vérification conserve les liens vers les documents (recto, verso, selfie).
                        </p>
                      </div>
                      <div className="overflow-hidden rounded-lg">
                        <img 
                          src="https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=600&h=400&fit=crop" 
                          alt="Stockage sécurisé"
                          className="h-full w-full object-cover"
                        />
                      </div>
                    </div>
                  </CardContent>
                )}
              </Card>

              <Card className="cursor-pointer" onClick={() => toggleFaq(3)}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">Quels sont les plans d'abonnement disponibles ?</CardTitle>
                    {openFaq === 3 ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
                  </div>
                </CardHeader>
                {openFaq === 3 && (
                  <CardContent>
                    <div className="grid gap-6 md:grid-cols-2">
                      <div>
                        <p className="text-muted-foreground">
                          Nous proposons trois plans : Starter (100 vérifications/mois), Professional (500 vérifications/mois) 
                          et Enterprise (2000 vérifications/mois). Paiement via FedaPay.
                        </p>
                      </div>
                      <div className="overflow-hidden rounded-lg">
                        <img 
                          src="https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=600&h=400&fit=crop" 
                          alt="Plans d'abonnement"
                          className="h-full w-full object-cover"
                        />
                      </div>
                    </div>
                  </CardContent>
                )}
              </Card>

              <Card className="cursor-pointer" onClick={() => toggleFaq(4)}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">Comment gérer plusieurs clés API ?</CardTitle>
                    {openFaq === 4 ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
                  </div>
                </CardHeader>
                {openFaq === 4 && (
                  <CardContent>
                    <div className="grid gap-6 md:grid-cols-2">
                      <div>
                        <p className="text-muted-foreground">
                          Chaque plan inclut un nombre de clés API (3 pour Starter, 10 pour Professional, 50 pour Enterprise). 
                          Gérez vos clés depuis votre dashboard entreprise.
                        </p>
                      </div>
                      <div className="overflow-hidden rounded-lg">
                        <img 
                          src="https://images.unsplash.com/photo-1510511459019-5dda7724fd87?w=600&h=400&fit=crop" 
                          alt="Gestion des clés API"
                          className="h-full w-full object-cover"
                        />
                      </div>
                    </div>
                  </CardContent>
                )}
              </Card>

              <Card className="cursor-pointer" onClick={() => toggleFaq(5)}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">Comment suivre mes statistiques ?</CardTitle>
                    {openFaq === 5 ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
                  </div>
                </CardHeader>
                {openFaq === 5 && (
                  <CardContent>
                    <div className="grid gap-6 md:grid-cols-2">
                      <div>
                        <p className="text-muted-foreground">
                          Votre dashboard affiche en temps réel le nombre de vérifications effectuées, votre quota mensuel 
                          et l'historique complet de toutes vos vérifications.
                        </p>
                      </div>
                      <div className="overflow-hidden rounded-lg">
                        <img 
                          src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&h=400&fit=crop" 
                          alt="Dashboard statistiques"
                          className="h-full w-full object-cover"
                        />
                      </div>
                    </div>
                  </CardContent>
                )}
              </Card>
            </div>
          </div>
        </section>

        <section id="pricing" className="bg-muted/30 py-12 md:py-16 lg:py-24">
          <div className="container mx-auto px-4">
            <div className="mx-auto mb-8 max-w-3xl text-center md:mb-12 lg:mb-16">
              <h2 className="mb-3 text-2xl font-bold tracking-tight sm:text-3xl md:text-4xl lg:text-5xl">
                Tarifs Simples et Transparents
              </h2>
              <p className="text-base text-muted-foreground sm:text-lg md:text-xl">
                Choisissez le plan adapté à vos besoins. Pas de frais cachés.
              </p>
            </div>

            {loadingPlans ? (
              <div className="py-12 text-center">
                <p className="text-muted-foreground">Chargement des plans...</p>
              </div>
            ) : plans.length === 0 ? (
              <div className="py-12 text-center">
                <p className="text-muted-foreground">Aucun plan disponible pour le moment.</p>
              </div>
            ) : (
              <div className="grid gap-6 sm:gap-8 md:grid-cols-2 lg:grid-cols-3">
                {plans.map((plan) => (
                  <Card key={plan.id} className={plan.is_popular ? "relative border-2" : ""}>
                    {plan.is_popular && (
                      <div className="absolute right-0 top-0 bg-foreground px-4 py-1 text-xs font-semibold text-background">
                        RECOMMANDÉ
                      </div>
                    )}
                    <CardHeader className={plan.is_popular ? "pb-8 pt-8" : "pb-8"}>
                      <CardTitle className="text-2xl">{plan.name}</CardTitle>
                      <CardDescription className="text-base">{plan.description}</CardDescription>
                      <div className="mt-6">
                        <span className="text-5xl font-bold">{plan.price.toLocaleString('fr-FR')}</span>
                        <span className="text-lg text-muted-foreground"> {plan.currency}</span>
                        <p className="mt-1 text-sm text-muted-foreground">par {plan.billing_period === 'monthly' ? 'mois' : 'an'}</p>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4 pb-8">
                      <ul className="space-y-3">
                        <li className="flex items-start gap-3">
                          <CheckCircle className="mt-0.5 h-5 w-5 flex-shrink-0" />
                          <span className="text-sm"><strong>{plan.monthly_quota.toLocaleString('fr-FR')}</strong> vérifications/mois</span>
                        </li>
                        <li className="flex items-start gap-3">
                          <CheckCircle className="mt-0.5 h-5 w-5 flex-shrink-0" />
                          <span className="text-sm"><strong>{plan.max_api_keys}</strong> clés API</span>
                        </li>
                        {plan.max_users > 1 && (
                          <li className="flex items-start gap-3">
                            <CheckCircle className="mt-0.5 h-5 w-5 flex-shrink-0" />
                            <span className="text-sm"><strong>{plan.max_users}</strong> utilisateurs</span>
                          </li>
                        )}
                        {plan.advantages.map((advantage, idx) => (
                          <li key={idx} className="flex items-start gap-3">
                            <CheckCircle className="mt-0.5 h-5 w-5 flex-shrink-0" />
                            <span className="text-sm">{advantage}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                    <CardFooter>
                      <Link href="/company/register" className="w-full">
                        <Button 
                          size="lg" 
                          className="w-full"
                          variant={plan.is_popular ? "default" : "outline"}
                        >
                          {plan.slug === 'enterprise' ? 'Nous Contacter' : 'Commencer Maintenant'}
                          {plan.is_popular && <ArrowRight className="ml-2 h-4 w-4" />}
                        </Button>
                      </Link>
                    </CardFooter>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </section>

        <section className="relative w-full max-w-full overflow-hidden py-16 md:py-24 lg:py-32">
          {/* Background with single image */}
          <div className="absolute inset-0 -z-10 w-full">
            <img 
              src="https://images.unsplash.com/photo-1557804506-669a67965ba0?w=1920&h=1080&fit=crop" 
              alt="Team collaboration"
              className="h-full w-full max-w-full object-cover"
            />
            <div className="absolute inset-0 w-full bg-gradient-to-r from-black/90 via-black/85 to-black/90" />
          </div>

          {/* Content */}
          <div className="container relative mx-auto w-full max-w-full px-4">
            <div className="mx-auto max-w-4xl text-center">
              <div className="mb-6 inline-flex rounded-full bg-emerald-600/20 px-6 py-2">
                <span className="text-sm font-semibold text-emerald-400">Commencez Gratuitement</span>
              </div>
              
              <h2 className="mb-4 text-3xl font-bold text-white sm:text-4xl md:text-5xl lg:text-6xl">
                Prêt à Transformer Votre Processus KYC ?
              </h2>
              
              <p className="mb-8 text-base text-gray-300 sm:text-lg md:mb-12 md:text-xl lg:text-2xl">
                Rejoignez des centaines d'entreprises qui font confiance à notre plateforme pour sécuriser leurs vérifications d'identité.
              </p>

              <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:justify-center md:mb-12">
                <Link href="/company/register">
                  <Button size="lg" className="h-12 w-full px-4 text-base sm:h-14 sm:px-8 sm:text-lg md:w-auto">
                    Créer un Compte Gratuit
                    <ArrowRight className="ml-2 h-4 w-4 sm:h-5 sm:w-5" />
                  </Button>
                </Link>
                <Link href="/docs">
                  <Button 
                    size="lg" 
                    variant="outline" 
                    className="h-12 w-full border-2 border-white bg-transparent px-4 text-base text-white hover:bg-white hover:text-foreground sm:h-14 sm:px-8 sm:text-lg md:w-auto"
                  >
                    Documentation API
                  </Button>
                </Link>
              </div>

              {/* Features Grid */}
              <div className="grid gap-6 sm:grid-cols-2 md:gap-8 lg:grid-cols-3">
                <div className="rounded-lg bg-white/10 p-4 backdrop-blur-sm sm:p-6">
                  <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-emerald-600">
                    <Shield className="h-6 w-6 text-white" />
                  </div>
                  <h3 className="mb-2 text-lg font-semibold text-white">100% Sécurisé</h3>
                  <p className="text-sm text-gray-300">
                    Chiffrement SSL/TLS et conformité RGPD garantis
                  </p>
                </div>

                <div className="rounded-lg bg-white/10 p-6 backdrop-blur-sm">
                  <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-emerald-600">
                    <Zap className="h-6 w-6 text-white" />
                  </div>
                  <h3 className="mb-2 text-lg font-semibold text-white">Intégration Rapide</h3>
                  <p className="text-sm text-gray-300">
                    API REST complète et documentation interactive
                  </p>
                </div>

                <div className="rounded-lg bg-white/10 p-6 backdrop-blur-sm">
                  <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-emerald-600">
                    <Users className="h-6 w-6 text-white" />
                  </div>
                  <h3 className="mb-2 text-lg font-semibold text-white">Support Dédié</h3>
                  <p className="text-sm text-gray-300">
                    Équipe disponible pour vous accompagner
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}
