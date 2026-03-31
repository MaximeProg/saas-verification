'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { CheckCircle, XCircle, Loader2 } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function PaymentCallbackPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')

  useEffect(() => {
    // Simuler la vérification du paiement
    // Dans un cas réel, vous devriez vérifier le statut via votre backend
    const timer = setTimeout(() => {
      const transactionId = searchParams.get('transaction_id')
      const statusParam = searchParams.get('status')
      
      if (statusParam === 'approved' || statusParam === 'completed') {
        setStatus('success')
        setMessage('Votre paiement a été effectué avec succès ! Votre plan sera activé sous peu.')
      } else if (statusParam === 'cancelled') {
        setStatus('error')
        setMessage('Le paiement a été annulé.')
      } else if (statusParam === 'failed') {
        setStatus('error')
        setMessage('Le paiement a échoué. Veuillez réessayer.')
      } else {
        setStatus('loading')
        setMessage('Vérification du paiement en cours...')
      }
    }, 2000)

    return () => clearTimeout(timer)
  }, [searchParams])

  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-center">
            {status === 'loading' && 'Traitement du paiement'}
            {status === 'success' && 'Paiement réussi'}
            {status === 'error' && 'Paiement échoué'}
          </CardTitle>
          <CardDescription className="text-center">
            {status === 'loading' && 'Veuillez patienter...'}
            {status === 'success' && 'Merci pour votre achat'}
            {status === 'error' && 'Une erreur est survenue'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex justify-center">
            {status === 'loading' && (
              <Loader2 className="h-16 w-16 animate-spin text-blue-600" />
            )}
            {status === 'success' && (
              <CheckCircle className="h-16 w-16 text-green-600" />
            )}
            {status === 'error' && (
              <XCircle className="h-16 w-16 text-red-600" />
            )}
          </div>
          
          <p className="text-center text-muted-foreground">
            {message}
          </p>

          {status !== 'loading' && (
            <div className="space-y-2">
              <Button 
                onClick={() => router.push('/company/dashboard/subscription')}
                className="w-full"
              >
                Retour à mes abonnements
              </Button>
              {status === 'error' && (
                <Button 
                  onClick={() => router.push('/company/dashboard/subscription')}
                  variant="outline"
                  className="w-full"
                >
                  Réessayer
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
