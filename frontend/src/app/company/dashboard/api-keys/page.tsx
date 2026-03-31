'use client'

import { useEffect, useState } from 'react'
import { Key, Copy, Eye, EyeOff, RefreshCw, AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { useAuth } from '@/hooks/useAuth'
import api from '@/lib/api'

export default function APIKeysPage() {
  const { company } = useAuth()
  const [showSecretKey, setShowSecretKey] = useState(false)
  const [copied, setCopied] = useState<string | null>(null)

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text)
    setCopied(key)
    setTimeout(() => setCopied(null), 2000)
  }

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold">Clés API</h2>
        <p className="text-muted-foreground">
          Gérez vos clés d'authentification pour l'API
        </p>
      </div>

      <Alert className="mb-6">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          Ne partagez jamais votre clé secrète. Elle donne un accès complet à votre compte.
        </AlertDescription>
      </Alert>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Clé publique</CardTitle>
            <CardDescription>
              Utilisez cette clé pour identifier votre compte dans les requêtes API
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2">
              <Input
                value={company?.public_key || ''}
                readOnly
                className="font-mono text-sm"
              />
              <Button
                variant="outline"
                onClick={() => copyToClipboard(company?.public_key || '', 'public')}
              >
                {copied === 'public' ? (
                  <>Copié !</>
                ) : (
                  <>
                    <Copy className="mr-2 h-4 w-4" />
                    Copier
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Clé secrète</CardTitle>
            <CardDescription>
              Cette clé doit rester confidentielle et être utilisée uniquement côté serveur
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex gap-2">
                <Input
                  type={showSecretKey ? 'text' : 'password'}
                  value={company?.secret_key || ''}
                  readOnly
                  className="font-mono text-sm"
                />
                <Button
                  variant="outline"
                  onClick={() => setShowSecretKey(!showSecretKey)}
                >
                  {showSecretKey ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
                <Button
                  variant="outline"
                  onClick={() => copyToClipboard(company?.secret_key || '', 'secret')}
                >
                  {copied === 'secret' ? (
                    <>Copié !</>
                  ) : (
                    <>
                      <Copy className="mr-2 h-4 w-4" />
                      Copier
                    </>
                  )}
                </Button>
              </div>
              
              {company?.status === 'sandbox' && (
                <Alert>
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    La régénération des clés API n'est disponible que pour les comptes en mode production.
                    Soumettez vos documents business pour activer votre compte.
                  </AlertDescription>
                </Alert>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Exemple d'utilisation</CardTitle>
            <CardDescription>
              Voici comment utiliser vos clés API dans vos requêtes
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <p className="mb-2 text-sm font-medium">cURL</p>
                <pre className="overflow-x-auto rounded-lg bg-muted p-4 text-sm">
{`curl -X POST https://api.kyc-platform.com/api/v1/verifications/initiate \\
  -H "Authorization: Bearer ${company?.secret_key || 'YOUR_SECRET_KEY'}" \\
  -H "Content-Type: application/json" \\
  -d '{
    "full_name": "John Doe",
    "email": "john@example.com",
    "external_reference": "USER_123"
  }'`}
                </pre>
              </div>

              <div>
                <p className="mb-2 text-sm font-medium">JavaScript</p>
                <pre className="overflow-x-auto rounded-lg bg-muted p-4 text-sm">
{`const response = await fetch('https://api.kyc-platform.com/api/v1/verifications/initiate', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ${company?.secret_key || 'YOUR_SECRET_KEY'}',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    full_name: 'John Doe',
    email: 'john@example.com',
    external_reference: 'USER_123'
  })
});`}
                </pre>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
