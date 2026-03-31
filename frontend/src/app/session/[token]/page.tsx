'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Upload, CheckCircle, AlertCircle, FileText, Camera, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import axios from 'axios'

interface VerificationData {
  verification_id: string
  full_name: string
  email: string
  status: string
  session_expires_at: string
}

export default function VerificationSessionPage() {
  const params = useParams()
  const router = useRouter()
  const token = params.token as string

  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [verification, setVerification] = useState<VerificationData | null>(null)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  // Fichiers
  const [documentFront, setDocumentFront] = useState<File | null>(null)
  const [documentBack, setDocumentBack] = useState<File | null>(null)
  const [selfie, setSelfie] = useState<File | null>(null)
  const [documentNumber, setDocumentNumber] = useState('')
  const [documentType, setDocumentType] = useState('passport')

  // Preview URLs
  const [frontPreview, setFrontPreview] = useState<string | null>(null)
  const [backPreview, setBackPreview] = useState<string | null>(null)
  const [selfiePreview, setSelfiePreview] = useState<string | null>(null)

  useEffect(() => {
    fetchVerification()
  }, [token])

  const fetchVerification = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/api/v1/verifications/session/${token}`)
      setVerification(response.data)
      
      // Vérifier si la session a expiré
      const expiresAt = new Date(response.data.session_expires_at)
      if (expiresAt < new Date()) {
        setError('Ce lien de vérification a expiré')
      }
      
      // Vérifier si déjà soumis
      if (response.data.status !== 'pending') {
        setError('Cette vérification a déjà été soumise')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Lien de vérification invalide')
    } finally {
      setLoading(false)
    }
  }

  const handleFileChange = (
    e: React.ChangeEvent<HTMLInputElement>,
    setFile: (file: File | null) => void,
    setPreview: (url: string | null) => void
  ) => {
    const file = e.target.files?.[0]
    if (file) {
      setFile(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!documentFront || !selfie) {
      setError('Veuillez uploader au minimum le recto du document et un selfie')
      return
    }

    if (!documentNumber) {
      setError('Veuillez saisir le numéro du document')
      return
    }

    setSubmitting(true)
    setError('')

    try {
      const formData = new FormData()
      formData.append('document_front', documentFront)
      if (documentBack) {
        formData.append('document_back', documentBack)
      }
      formData.append('selfie', selfie)
      formData.append('document_type', documentType)
      formData.append('document_number', documentNumber)

      await axios.post(
        `http://localhost:8000/api/v1/verifications/session/${token}/submit`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )

      setSuccess(true)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de la soumission')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-emerald-50 to-white dark:from-gray-900 dark:to-gray-800">
        <Loader2 className="h-8 w-8 animate-spin text-emerald-600" />
      </div>
    )
  }

  if (success) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-emerald-50 to-white dark:from-gray-900 dark:to-gray-800 p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100 dark:bg-emerald-900">
              <CheckCircle className="h-8 w-8 text-emerald-600 dark:text-emerald-400" />
            </div>
            <CardTitle className="text-2xl">Documents soumis avec succès !</CardTitle>
            <CardDescription>
              Vos documents sont en cours de vérification. Vous recevrez une notification par email une fois la validation terminée.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-lg bg-gray-100 dark:bg-gray-800 p-4 text-sm">
              <p className="mb-2 font-semibold text-gray-900 dark:text-white">Prochaines étapes :</p>
              <ol className="list-decimal space-y-1 pl-5 text-gray-700 dark:text-gray-300">
                <li>Notre équipe examine vos documents</li>
                <li>Validation sous 24-48 heures</li>
                <li>Notification par email du résultat</li>
              </ol>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error && !verification) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-red-50 to-white dark:from-gray-900 dark:to-gray-800 p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-red-100 dark:bg-red-900">
              <AlertCircle className="h-8 w-8 text-red-600 dark:text-red-400" />
            </div>
            <CardTitle className="text-2xl">Lien invalide</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-emerald-50 to-white dark:from-gray-900 dark:to-gray-800 py-12">
      <div className="container mx-auto max-w-3xl px-4">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-600">
            <FileText className="h-8 w-8 text-white" />
          </div>
          <h1 className="mb-2 text-3xl font-bold text-gray-900 dark:text-white">Vérification d'identité</h1>
          <p className="text-gray-600 dark:text-gray-300">
            Bonjour {verification?.full_name}, veuillez soumettre vos documents pour finaliser votre vérification
          </p>
        </div>

        {/* Formulaire */}
        <Card>
          <CardHeader>
            <CardTitle>Documents requis</CardTitle>
            <CardDescription>
              Uploadez les photos de votre document d'identité et un selfie
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Type de document */}
              <div>
                <Label htmlFor="documentType" className="text-gray-700 dark:text-gray-200 font-medium">Type de document</Label>
                <select
                  id="documentType"
                  value={documentType}
                  onChange={(e) => setDocumentType(e.target.value)}
                  className="mt-1 w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                >
                  <option value="passport">Passeport</option>
                  <option value="id_card">Carte d'identité</option>
                  <option value="driver_license">Permis de conduire</option>
                </select>
              </div>

              {/* Numéro de document */}
              <div>
                <Label htmlFor="documentNumber" className="text-gray-700 dark:text-gray-200 font-medium">Numéro du document *</Label>
                <input
                  type="text"
                  id="documentNumber"
                  value={documentNumber}
                  onChange={(e) => setDocumentNumber(e.target.value)}
                  className="mt-1 w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white"
                  placeholder="Ex: AB123456"
                  required
                />
              </div>

              {/* Document recto */}
              <div>
                <Label className="text-gray-700 dark:text-gray-200 font-medium">Recto du document *</Label>
                <div className="mt-2">
                  {frontPreview ? (
                    <div className="relative">
                      <img src={frontPreview} alt="Recto" className="h-48 w-full rounded-lg object-cover" />
                      <Button
                        type="button"
                        size="sm"
                        variant="destructive"
                        className="absolute right-2 top-2"
                        onClick={() => {
                          setDocumentFront(null)
                          setFrontPreview(null)
                        }}
                      >
                        Supprimer
                      </Button>
                    </div>
                  ) : (
                    <label className="flex h-48 w-full cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-emerald-600 bg-gray-50 dark:bg-gray-800">
                      <Upload className="mb-2 h-8 w-8 text-gray-400 dark:text-gray-500" />
                      <span className="text-sm text-gray-600 dark:text-gray-400">Cliquez pour uploader</span>
                      <input
                        type="file"
                        accept="image/*"
                        className="hidden"
                        onChange={(e) => handleFileChange(e, setDocumentFront, setFrontPreview)}
                      />
                    </label>
                  )}
                </div>
              </div>

              {/* Document verso */}
              <div>
                <Label className="text-gray-700 dark:text-gray-200 font-medium">Verso du document {documentType !== 'passport' && '*'}</Label>
                <div className="mt-2">
                  {backPreview ? (
                    <div className="relative">
                      <img src={backPreview} alt="Verso" className="h-48 w-full rounded-lg object-cover" />
                      <Button
                        type="button"
                        size="sm"
                        variant="destructive"
                        className="absolute right-2 top-2"
                        onClick={() => {
                          setDocumentBack(null)
                          setBackPreview(null)
                        }}
                      >
                        Supprimer
                      </Button>
                    </div>
                  ) : (
                    <label className="flex h-48 w-full cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-emerald-600 bg-gray-50 dark:bg-gray-800">
                      <Upload className="mb-2 h-8 w-8 text-gray-400 dark:text-gray-500" />
                      <span className="text-sm text-gray-600 dark:text-gray-400">Cliquez pour uploader</span>
                      <input
                        type="file"
                        accept="image/*"
                        className="hidden"
                        onChange={(e) => handleFileChange(e, setDocumentBack, setBackPreview)}
                      />
                    </label>
                  )}
                </div>
              </div>

              {/* Selfie */}
              <div>
                <Label className="text-gray-700 dark:text-gray-200 font-medium">Selfie avec le document *</Label>
                <div className="mt-2">
                  {selfiePreview ? (
                    <div className="relative">
                      <img src={selfiePreview} alt="Selfie" className="h-48 w-full rounded-lg object-cover" />
                      <Button
                        type="button"
                        size="sm"
                        variant="destructive"
                        className="absolute right-2 top-2"
                        onClick={() => {
                          setSelfie(null)
                          setSelfiePreview(null)
                        }}
                      >
                        Supprimer
                      </Button>
                    </div>
                  ) : (
                    <label className="flex h-48 w-full cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 hover:border-emerald-600 bg-gray-50 dark:bg-gray-800">
                      <Camera className="mb-2 h-8 w-8 text-gray-400 dark:text-gray-500" />
                      <span className="text-sm text-gray-600 dark:text-gray-400">Cliquez pour prendre un selfie</span>
                      <input
                        type="file"
                        accept="image/*"
                        capture="user"
                        className="hidden"
                        onChange={(e) => handleFileChange(e, setSelfie, setSelfiePreview)}
                      />
                    </label>
                  )}
                </div>
              </div>

              {/* Erreur */}
              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              {/* Bouton submit */}
              <Button type="submit" className="w-full" size="lg" disabled={submitting}>
                {submitting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Envoi en cours...
                  </>
                ) : (
                  'Soumettre mes documents'
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Info sécurité */}
        <div className="mt-6 rounded-lg bg-blue-50 p-4 text-sm text-blue-900">
          <p className="mb-2 font-semibold">🔒 Vos données sont sécurisées</p>
          <p>
            Vos documents sont chiffrés et stockés de manière sécurisée. Ils ne seront utilisés que pour la vérification d'identité.
          </p>
        </div>
      </div>
    </div>
  )
}
