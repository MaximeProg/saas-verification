'use client'

import { useEffect, useState } from 'react'
import { CreditCard, Check, Zap, Crown, Rocket, AlertTriangle, CheckCircle, XCircle } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { useAuth } from '@/hooks/useAuth'
import api from '@/lib/api'

interface SubscriptionPlan {
  id: string
  name: string
  price: number
  monthly_quota: number
  features: string[]
  is_active: boolean
}

interface Payment {
  id: string
  payment_reference: string
  amount: number
  currency: string
  status: string
  payment_method: string
  created_at: string
  paid_at?: string
  description?: string
}

export default function SubscriptionPage() {
  const { company } = useAuth()
  const [plans, setPlans] = useState<SubscriptionPlan[]>([])
  const [loading, setLoading] = useState(true)
  const [purchasing, setPurchasing] = useState(false)
  const [showConfirmDialog, setShowConfirmDialog] = useState(false)
  const [showResultDialog, setShowResultDialog] = useState(false)
  const [showPaymentModal, setShowPaymentModal] = useState(false)
  const [selectedPlan, setSelectedPlan] = useState<{ id: string; name: string } | null>(null)
  const [resultMessage, setResultMessage] = useState({ type: '', title: '', message: '' })
  const [paymentUrl, setPaymentUrl] = useState('')
  const [paymentReference, setPaymentReference] = useState('')
  const [payments, setPayments] = useState<Payment[]>([])
  const [loadingPayments, setLoadingPayments] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPayments, setTotalPayments] = useState(0)
  const paymentsPerPage = 10

  useEffect(() => {
    fetchPlans()
    fetchPayments(1)
  }, [])

  const fetchPlans = async () => {
    try {
      const response = await api.get('/subscription-plans/public')
      setPlans(response.data || [])
    } catch (error) {
      console.error('Error fetching plans:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchPayments = async (page: number = 1) => {
    try {
      setLoadingPayments(true)
      const response = await api.get(`/payments/my-payments?page=${page}&page_size=${paymentsPerPage}`)
      setPayments(response.data.payments || [])
      setTotalPayments(response.data.total || 0)
      setCurrentPage(page)
    } catch (error: any) {
      console.error('Error fetching payments:', error)
      if (error.response?.status !== 401) {
        setPayments([])
        setTotalPayments(0)
      }
    } finally {
      setLoadingPayments(false)
    }
  }

  const handlePurchasePlan = (planId: string, planName: string) => {
    if (!company?.documents_validated) {
      setResultMessage({
        type: 'warning',
        title: 'Documents non validés',
        message: 'Vos documents d\'entreprise doivent être validés avant de pouvoir acheter un plan. Veuillez soumettre vos documents dans la section Paramètres.'
      })
      setShowResultDialog(true)
      return
    }

    setSelectedPlan({ id: planId, name: planName })
    setShowConfirmDialog(true)
  }

  const confirmPurchase = async () => {
    if (!selectedPlan) return
    
    setShowConfirmDialog(false)

    try {
      setPurchasing(true)
      
      // Initialiser le paiement
      const response = await api.post('/payments/initialize', {
        plan_id: selectedPlan.id,
        payment_method: 'mobile_money',
        customer_email: company?.email,
        customer_phone: company?.phone || '',
        callback_url: `${window.location.origin}/company/dashboard/subscription/callback`,
        return_url: `${window.location.origin}/company/dashboard/subscription`
      })

      const { payment_url, payment_reference } = response.data

      if (payment_url) {
        setPaymentUrl(payment_url)
        setPaymentReference(payment_reference)
        setShowPaymentModal(true)
      } else {
        setResultMessage({
          type: 'error',
          title: 'Erreur',
          message: 'URL de paiement non reçue. Veuillez réessayer.'
        })
        setShowResultDialog(true)
      }
    } catch (error: any) {
      console.error('Error purchasing plan:', error)
      const errorMessage = error.response?.data?.detail || 'Erreur lors de l\'initialisation du paiement'
      setResultMessage({
        type: 'error',
        title: 'Erreur de paiement',
        message: errorMessage
      })
      setShowResultDialog(true)
    } finally {
      setPurchasing(false)
    }
  }

  const getPlanIcon = (planName: string) => {
    const name = planName.toLowerCase()
    if (name.includes('starter')) return Zap
    if (name.includes('pro')) return Crown
    if (name.includes('enterprise')) return Rocket
    return CreditCard
  }

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold">Abonnement</h2>
        <p className="text-muted-foreground">
          Gérez votre plan d'abonnement et vos paiements
        </p>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Abonnement Actuel</CardTitle>
          <CardDescription>
            Votre plan actuel et son utilisation
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!company?.subscription_plan || company?.subscription_plan === 'free' ? (
            <div className="py-8 text-center">
              <CreditCard className="mx-auto h-12 w-12 text-muted-foreground" />
              <h3 className="mt-4 text-lg font-semibold">Aucun abonnement actif</h3>
              <p className="mt-2 text-sm text-muted-foreground">
                Choisissez un plan ci-dessous pour commencer à utiliser la plateforme
              </p>
            </div>
          ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Plan</span>
              <Badge className="capitalize">{company?.subscription_plan}</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Quota mensuel</span>
              <span className="font-medium">{company?.monthly_quota} vérifications</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Utilisé</span>
              <span className="font-medium">{company?.quota_used} / {company?.monthly_quota}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Statut</span>
              <Badge variant={company?.status === 'sandbox' ? 'secondary' : 'default'}>
                {company?.status === 'sandbox' ? 'Mode Test' : 'Production'}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Expire le</span>
              <span className="font-medium">
                {new Date(company.subscription_expires_at!).toLocaleDateString('fr-FR')}
              </span>
            </div>
          </div>
          )}
        </CardContent>
      </Card>

      <div className="mb-6">
        <h3 className="mb-4 text-xl font-semibold">Plans Disponibles</h3>
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <CreditCard className="h-12 w-12 animate-pulse text-muted-foreground" />
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {plans.map((plan) => {
              const Icon = getPlanIcon(plan.name)
              const isCurrentPlan = company?.subscription_plan?.toLowerCase() === plan.name.toLowerCase() && 
                                   company?.subscription_expires_at !== null
              
              return (
                <Card key={plan.id} className={isCurrentPlan ? 'border-emerald-500' : ''}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <Icon className="h-8 w-8 text-emerald-600" />
                      {isCurrentPlan && <Badge>Plan Actuel</Badge>}
                    </div>
                    <CardTitle className="capitalize">{plan.name}</CardTitle>
                    <CardDescription>
                      <span className="text-3xl font-bold">{plan.price.toLocaleString()}</span>
                      <span className="text-sm text-muted-foreground"> FCFA/mois</span>
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <p className="text-sm font-medium">
                          {plan.monthly_quota.toLocaleString()} vérifications/mois
                        </p>
                      </div>
                      <ul className="space-y-2">
                        {plan.features?.map((feature, index) => (
                          <li key={index} className="flex items-start gap-2 text-sm">
                            <Check className="mt-0.5 h-4 w-4 flex-shrink-0 text-emerald-600" />
                            <span>{feature}</span>
                          </li>
                        ))}
                      </ul>
                      <Button
                        className="w-full"
                        variant={isCurrentPlan ? 'outline' : 'default'}
                        disabled={isCurrentPlan || !plan.is_active || purchasing}
                        onClick={() => handlePurchasePlan(plan.id, plan.name)}
                      >
                        {isCurrentPlan ? 'Plan Actuel' : plan.is_active ? 'Choisir ce plan' : 'Indisponible'}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Historique des Paiements</CardTitle>
          <CardDescription>
            Vos dernières transactions
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loadingPayments ? (
            <div className="flex items-center justify-center py-8">
              <CreditCard className="h-8 w-8 animate-pulse text-muted-foreground" />
            </div>
          ) : payments.length === 0 ? (
            <p className="text-center text-sm text-muted-foreground py-8">
              Aucun paiement enregistré pour le moment
            </p>
          ) : (
            <div className="space-y-3">
              {payments.map((payment) => (
                <div
                  key={payment.id}
                  className="flex items-center justify-between rounded-lg border p-4 hover:bg-accent/50 transition-colors"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <p className="font-medium">{payment.description || 'Abonnement'}</p>
                      <Badge
                        variant={
                          payment.status === 'completed'
                            ? 'default'
                            : payment.status === 'pending' || payment.status === 'processing'
                            ? 'secondary'
                            : 'destructive'
                        }
                      >
                        {payment.status === 'completed'
                          ? 'Payé'
                          : payment.status === 'pending'
                          ? 'En attente'
                          : payment.status === 'processing'
                          ? 'En cours'
                          : payment.status === 'failed'
                          ? 'Échoué'
                          : payment.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Référence: {payment.payment_reference}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(payment.created_at).toLocaleDateString('fr-FR', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold">
                      {payment.amount.toLocaleString()} {payment.currency}
                    </p>
                    <p className="text-xs text-muted-foreground capitalize">
                      {payment.payment_method.replace('_', ' ')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
          {totalPayments > paymentsPerPage && (
            <div className="mt-4 flex items-center justify-between border-t pt-4">
              <p className="text-sm text-muted-foreground">
                Page {currentPage} sur {Math.ceil(totalPayments / paymentsPerPage)} ({totalPayments} paiement{totalPayments > 1 ? 's' : ''})
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => fetchPayments(currentPage - 1)}
                  disabled={currentPage === 1 || loadingPayments}
                >
                  Précédent
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => fetchPayments(currentPage + 1)}
                  disabled={currentPage >= Math.ceil(totalPayments / paymentsPerPage) || loadingPayments}
                >
                  Suivant
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dialog de confirmation */}
      <AlertDialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirmer l'achat</AlertDialogTitle>
            <AlertDialogDescription>
              Voulez-vous acheter le plan <strong>{selectedPlan?.name}</strong> ?
              <br /><br />
              Vous serez redirigé vers FedaPay pour effectuer le paiement de manière sécurisée.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Annuler</AlertDialogCancel>
            <AlertDialogAction onClick={confirmPurchase} disabled={purchasing}>
              {purchasing ? 'Traitement...' : 'Continuer'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Dialog de résultat */}
      <AlertDialog open={showResultDialog} onOpenChange={setShowResultDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <div className="flex items-center gap-2">
              {resultMessage.type === 'warning' && <AlertTriangle className="h-5 w-5 text-amber-500" />}
              {resultMessage.type === 'error' && <XCircle className="h-5 w-5 text-rose-500" />}
              {resultMessage.type === 'success' && <CheckCircle className="h-5 w-5 text-emerald-500" />}
              <AlertDialogTitle>{resultMessage.title}</AlertDialogTitle>
            </div>
            <AlertDialogDescription className="text-left">
              {resultMessage.message}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogAction>Fermer</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Modal FedaPay intégré */}
      <Dialog open={showPaymentModal} onOpenChange={(open) => {
        setShowPaymentModal(open)
        if (!open) {
          // Recharger les données après fermeture du modal
          fetchPayments(currentPage)
          window.location.reload() // Recharger pour mettre à jour l'abonnement
        }
      }}>
        <DialogContent className="max-w-2xl h-[80vh]">
          <DialogHeader>
            <DialogTitle>Paiement FedaPay</DialogTitle>
            <DialogDescription>
              Référence: {paymentReference}
            </DialogDescription>
          </DialogHeader>
          <div className="flex-1 overflow-hidden rounded-lg border">
            {paymentUrl && (
              <iframe
                src={paymentUrl}
                className="h-full w-full"
                title="FedaPay Payment"
                allow="payment"
              />
            )}
          </div>
          <div className="text-sm text-muted-foreground text-center">
            Complétez le paiement puis fermez cette fenêtre. Votre abonnement sera activé automatiquement.
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
