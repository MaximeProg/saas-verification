'use client'

import { useState } from 'react'
import { Settings, Building, Webhook, FileText, Save, Upload, RefreshCw, AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { useAuth } from '@/hooks/useAuth'
import api from '@/lib/api'

export default function SettingsPage() {
  const { company } = useAuth()
  const [loading, setLoading] = useState(false)
  const [webhookUrl, setWebhookUrl] = useState(company?.webhook_url || '')
  const [showNewKeys, setShowNewKeys] = useState(false)
  const [newKeys, setNewKeys] = useState<{public_key: string, secret_key: string} | null>(null)
  const [businessDocs, setBusinessDocs] = useState({
    phone: company?.phone || '',
    address: company?.address || '',
    rccm: company?.rccm || '',
    tax_number: company?.tax_number || '',
    legal_representative: company?.legal_representative || '',
    website: company?.website || '',
  })

  const handleWebhookUpdate = async () => {
    try {
      setLoading(true)
      await api.put('/companies/webhook', { webhook_url: webhookUrl })
      alert('Webhook URL mise à jour avec succès')
      window.location.reload()
    } catch (error) {
      console.error('Error updating webhook:', error)
      alert('Erreur lors de la mise à jour du webhook')
    } finally {
      setLoading(false)
    }
  }

  const handleBusinessDocsSubmit = async () => {
    try {
      setLoading(true)
      await api.post('/companies/submit-business-documents', businessDocs)
      alert('Documents business soumis avec succès. En attente de validation admin.')
      window.location.reload()
    } catch (error: any) {
      console.error('Error submitting business docs:', error)
      alert(error.response?.data?.detail || 'Erreur lors de la soumission')
    } finally {
      setLoading(false)
    }
  }

  const handleRegenerateKeys = async () => {
    if (!confirm('⚠️ ATTENTION: La régénération des clés API invalidera vos anciennes clés. Toutes les intégrations utilisant les anciennes clés cesseront de fonctionner. Êtes-vous sûr de vouloir continuer ?')) {
      return
    }
    
    try {
      setLoading(true)
      const response = await api.post('/companies/regenerate-api-keys')
      setNewKeys(response.data)
      setShowNewKeys(true)
      alert('✅ Nouvelles clés générées avec succès! Copiez-les maintenant, elles ne seront plus affichées.')
    } catch (error: any) {
      console.error('Error regenerating keys:', error)
      alert(error.response?.data?.detail || 'Erreur lors de la régénération des clés')
    } finally {
      setLoading(false)
    }
  }

  const needsBusinessDocs = !company?.rccm || !company?.tax_number || !company?.legal_representative

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold">Paramètres</h2>
        <p className="text-muted-foreground">
          Gérez les paramètres de votre compte
        </p>
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Informations de l'entreprise</CardTitle>
            <CardDescription>
              Détails de votre compte
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <Label>Nom de l'entreprise</Label>
                <Input value={company?.company_name || ''} disabled />
              </div>
              <div>
                <Label>Email</Label>
                <Input value={company?.email || ''} disabled />
              </div>
              <div>
                <Label>Téléphone</Label>
                <Input value={company?.phone || 'Non renseigné'} disabled />
              </div>
              <div>
                <Label>Pays</Label>
                <Input value={company?.country || ''} disabled />
              </div>
              <div>
                <Label>Adresse</Label>
                <Input value={company?.address || 'Non renseignée'} disabled />
              </div>
              <div>
                <Label>RCCM</Label>
                <Input value={company?.rccm || 'Non renseigné'} disabled />
              </div>
              <div>
                <Label>Numéro Fiscal (IFU)</Label>
                <Input value={company?.tax_number || 'Non renseigné'} disabled />
              </div>
              <div>
                <Label>Représentant Légal</Label>
                <Input value={company?.legal_representative || 'Non renseigné'} disabled />
              </div>
              <div>
                <Label>Site Web</Label>
                <Input value={company?.website || 'Non renseigné'} disabled />
              </div>
              <div>
                <Label>Statut du compte</Label>
                <div className="mt-2">
                  <Badge variant={company?.status === 'sandbox' ? 'secondary' : 'default'}>
                    {company?.status === 'sandbox' ? 'Mode Test (Sandbox)' : 'Production'}
                  </Badge>
                </div>
              </div>
              <div>
                <Label>Documents validés</Label>
                <div className="mt-2">
                  <Badge variant={company?.documents_validated ? 'default' : 'secondary'}>
                    {company?.documents_validated ? 'Validés' : 'En attente'}
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {needsBusinessDocs && (
          <Card className="border-amber-500">
            <CardHeader>
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-amber-500" />
                <CardTitle>Documents Business Requis</CardTitle>
              </div>
              <CardDescription>
                Soumettez vos documents business pour passer en mode production
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label htmlFor="phone">Téléphone *</Label>
                  <Input
                    id="phone"
                    value={businessDocs.phone}
                    onChange={(e) => setBusinessDocs({ ...businessDocs, phone: e.target.value })}
                    placeholder="+229 XX XX XX XX"
                  />
                </div>
                <div>
                  <Label htmlFor="address">Adresse *</Label>
                  <Input
                    id="address"
                    value={businessDocs.address}
                    onChange={(e) => setBusinessDocs({ ...businessDocs, address: e.target.value })}
                    placeholder="Adresse complète"
                  />
                </div>
                <div>
                  <Label htmlFor="rccm">RCCM *</Label>
                  <Input
                    id="rccm"
                    value={businessDocs.rccm}
                    onChange={(e) => setBusinessDocs({ ...businessDocs, rccm: e.target.value })}
                    placeholder="Numéro RCCM"
                  />
                </div>
                <div>
                  <Label htmlFor="tax_number">IFU / Numéro Fiscal *</Label>
                  <Input
                    id="tax_number"
                    value={businessDocs.tax_number}
                    onChange={(e) => setBusinessDocs({ ...businessDocs, tax_number: e.target.value })}
                    placeholder="Numéro fiscal"
                  />
                </div>
                <div>
                  <Label htmlFor="legal_representative">Représentant Légal *</Label>
                  <Input
                    id="legal_representative"
                    value={businessDocs.legal_representative}
                    onChange={(e) => setBusinessDocs({ ...businessDocs, legal_representative: e.target.value })}
                    placeholder="Nom complet"
                  />
                </div>
                <div>
                  <Label htmlFor="website">Site Web (optionnel)</Label>
                  <Input
                    id="website"
                    value={businessDocs.website}
                    onChange={(e) => setBusinessDocs({ ...businessDocs, website: e.target.value })}
                    placeholder="https://example.com"
                  />
                </div>
              </div>
              <Button
                onClick={handleBusinessDocsSubmit}
                disabled={loading || !businessDocs.phone || !businessDocs.address || !businessDocs.rccm || !businessDocs.tax_number || !businessDocs.legal_representative}
                className="w-full"
              >
                <Upload className="mr-2 h-4 w-4" />
                {loading ? 'Soumission...' : 'Soumettre les documents'}
              </Button>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle>Configuration Webhook</CardTitle>
            <CardDescription>
              Recevez des notifications en temps réel sur les changements de statut
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="webhook">URL du Webhook</Label>
              <Input
                id="webhook"
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
                placeholder="https://votre-site.com/webhook"
              />
              <p className="mt-2 text-xs text-muted-foreground">
                Secret Webhook: <code className="rounded bg-muted px-1 py-0.5">{company?.webhook_secret}</code>
              </p>
            </div>
            <Button onClick={handleWebhookUpdate} disabled={loading}>
              <Save className="mr-2 h-4 w-4" />
              {loading ? 'Enregistrement...' : 'Enregistrer'}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Clés API</CardTitle>
            <CardDescription>
              Vos identifiants d'authentification
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {showNewKeys && newKeys ? (
              <div className="rounded-lg border border-amber-500 bg-amber-50 p-4 space-y-3">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="h-5 w-5 text-amber-600 mt-0.5" />
                  <div className="flex-1">
                    <p className="font-semibold text-amber-900">Nouvelles clés générées</p>
                    <p className="text-sm text-amber-800 mt-1">Copiez ces clés maintenant. Elles ne seront plus affichées après actualisation.</p>
                  </div>
                </div>
                <div>
                  <Label className="text-amber-900">Nouvelle Clé Publique</Label>
                  <Input value={newKeys.public_key} readOnly className="font-mono text-sm bg-white" />
                </div>
                <div>
                  <Label className="text-amber-900">Nouvelle Clé Secrète</Label>
                  <Input value={newKeys.secret_key} readOnly className="font-mono text-sm bg-white" />
                </div>
                <Button 
                  onClick={() => window.location.reload()} 
                  className="w-full"
                  variant="outline"
                >
                  J'ai copié mes clés - Actualiser
                </Button>
              </div>
            ) : (
              <>
                <div>
                  <Label>Clé Publique</Label>
                  <Input value={company?.public_key || ''} disabled className="font-mono text-sm" />
                </div>
                <div>
                  <Label>Clé Secrète</Label>
                  <Input type="password" value={company?.secret_key || ''} disabled className="font-mono text-sm" />
                </div>
                <Button 
                  onClick={handleRegenerateKeys} 
                  disabled={loading}
                  variant="outline"
                  className="w-full"
                >
                  <RefreshCw className="mr-2 h-4 w-4" />
                  {loading ? 'Régénération...' : 'Régénérer les clés API'}
                </Button>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
