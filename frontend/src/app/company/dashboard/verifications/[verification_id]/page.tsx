'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ArrowLeft, CheckCircle, XCircle, Clock, FileText, Mail, Phone, Calendar, Download } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import api from '@/lib/api'

interface VerificationDetails {
  verification_id: string
  full_name: string
  email: string
  phone?: string
  country?: string
  status: string
  verification_type: string
  document_type?: string
  document_number?: string
  document_front_url?: string
  document_back_url?: string
  selfie_url?: string
  created_at: string
  updated_at: string
  submitted_at?: string
  reviewed_at?: string
  rejection_reason?: string
}

export default function VerificationDetailsPage() {
  const params = useParams()
  const router = useRouter()
  const verification_id = params.verification_id as string

  const [verification, setVerification] = useState<VerificationDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [processing, setProcessing] = useState(false)

  useEffect(() => {
    fetchVerificationDetails()
  }, [verification_id])

  const fetchVerificationDetails = async () => {
    try {
      setLoading(true)
      const response = await api.get(`/verifications/${verification_id}`)
      setVerification(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors du chargement')
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async () => {
    if (!confirm('Êtes-vous sûr de vouloir approuver cette vérification ?')) return
    
    try {
      setProcessing(true)
      await api.post(`/verifications/${verification_id}/approve`)
      await fetchVerificationDetails()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de l\'approbation')
    } finally {
      setProcessing(false)
    }
  }

  const handleReject = async () => {
    const reason = prompt('Raison du rejet :')
    if (!reason) return
    
    try {
      setProcessing(true)
      await api.post(`/verifications/${verification_id}/reject`, { reason })
      await fetchVerificationDetails()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors du rejet')
    } finally {
      setProcessing(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { variant: any; icon: any; label: string }> = {
      pending: { variant: 'secondary', icon: Clock, label: 'En attente' },
      in_review: { variant: 'default', icon: Clock, label: 'En révision' },
      approved: { variant: 'default', icon: CheckCircle, label: 'Approuvé' },
      rejected: { variant: 'destructive', icon: XCircle, label: 'Rejeté' }
    }
    
    const config = variants[status] || variants.pending
    const Icon = config.icon
    
    return (
      <Badge variant={config.variant} className="flex items-center gap-1 w-fit">
        <Icon className="h-3 w-3" />
        {config.label}
      </Badge>
    )
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto mb-4" />
          <p className="text-muted-foreground">Chargement...</p>
        </div>
      </div>
    )
  }

  if (error || !verification) {
    return (
      <div className="container mx-auto max-w-4xl p-6">
        <Alert variant="destructive">
          <AlertDescription>{error || 'Vérification introuvable'}</AlertDescription>
        </Alert>
        <Button onClick={() => router.back()} className="mt-4">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Retour
        </Button>
      </div>
    )
  }

  return (
    <div className="container mx-auto max-w-6xl p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Détails de la vérification</h1>
            <p className="text-muted-foreground">{verification.verification_id}</p>
          </div>
        </div>
        {getStatusBadge(verification.status)}
      </div>

      {/* Statut de la vérification */}
      {verification.status === 'in_review' && (
        <Alert>
          <Clock className="h-4 w-4" />
          <AlertDescription>
            Cette vérification est en cours d'examen par notre équipe. Vous serez notifié du résultat par email.
          </AlertDescription>
        </Alert>
      )}

      {/* Rejection Reason */}
      {verification.status === 'rejected' && verification.rejection_reason && (
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertDescription>
            <strong>Raison du rejet :</strong> {verification.rejection_reason}
          </AlertDescription>
        </Alert>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        {/* Informations personnelles */}
        <Card>
          <CardHeader>
            <CardTitle>Informations personnelles</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground">Nom complet</p>
              <p className="font-medium">{verification.full_name}</p>
            </div>
            <div className="border-t" />
            <div>
              <p className="text-sm text-muted-foreground">Email</p>
              <p className="font-medium flex items-center gap-2">
                <Mail className="h-4 w-4" />
                {verification.email}
              </p>
            </div>
            {verification.phone && (
              <>
                <div className="border-t" />
                <div>
                  <p className="text-sm text-muted-foreground">Téléphone</p>
                  <p className="font-medium flex items-center gap-2">
                    <Phone className="h-4 w-4" />
                    {verification.phone}
                  </p>
                </div>
              </>
            )}
            {verification.country && (
              <>
                <div className="border-t" />
                <div>
                  <p className="text-sm text-muted-foreground">Pays</p>
                  <p className="font-medium">{verification.country}</p>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Informations de vérification */}
        <Card>
          <CardHeader>
            <CardTitle>Informations de vérification</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground">Type de vérification</p>
              <p className="font-medium">{verification.verification_type}</p>
            </div>
            {verification.document_type && (
              <>
                <div className="border-t" />
                <div>
                  <p className="text-sm text-muted-foreground">Type de document</p>
                  <p className="font-medium">{verification.document_type}</p>
                </div>
              </>
            )}
            {verification.document_number && (
              <>
                <div className="border-t" />
                <div>
                  <p className="text-sm text-muted-foreground">Numéro de document</p>
                  <p className="font-medium">{verification.document_number}</p>
                </div>
              </>
            )}
            <div className="border-t" />
            <div>
              <p className="text-sm text-muted-foreground">Date de création</p>
              <p className="font-medium flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                {new Date(verification.created_at).toLocaleString('fr-FR')}
              </p>
            </div>
            {verification.submitted_at && (
              <>
                <div className="border-t" />
                <div>
                  <p className="text-sm text-muted-foreground">Date de soumission</p>
                  <p className="font-medium flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    {new Date(verification.submitted_at).toLocaleString('fr-FR')}
                  </p>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Documents */}
      {(verification.document_front_url || verification.selfie_url) && (
        <Card>
          <CardHeader>
            <CardTitle>Documents soumis</CardTitle>
            <CardDescription>Cliquez sur une image pour l'agrandir</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              {verification.document_front_url && (
                <div>
                  <p className="mb-2 text-sm font-medium">Recto du document</p>
                  <a href={verification.document_front_url} target="_blank" rel="noopener noreferrer">
                    <img 
                      src={verification.document_front_url} 
                      alt="Recto" 
                      className="rounded-lg border hover:opacity-80 transition-opacity cursor-pointer w-full h-48 object-cover"
                    />
                  </a>
                </div>
              )}
              {verification.document_back_url && (
                <div>
                  <p className="mb-2 text-sm font-medium">Verso du document</p>
                  <a href={verification.document_back_url} target="_blank" rel="noopener noreferrer">
                    <img 
                      src={verification.document_back_url} 
                      alt="Verso" 
                      className="rounded-lg border hover:opacity-80 transition-opacity cursor-pointer w-full h-48 object-cover"
                    />
                  </a>
                </div>
              )}
              {verification.selfie_url && (
                <div>
                  <p className="mb-2 text-sm font-medium">Selfie</p>
                  <a href={verification.selfie_url} target="_blank" rel="noopener noreferrer">
                    <img 
                      src={verification.selfie_url} 
                      alt="Selfie" 
                      className="rounded-lg border hover:opacity-80 transition-opacity cursor-pointer w-full h-48 object-cover"
                    />
                  </a>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
