'use client'

import { useEffect, useState } from 'react'
import { FileCheck, Search, Filter, Eye, Calendar, CheckCircle, XCircle, Clock } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import api from '@/lib/api'
import Link from 'next/link'

interface Verification {
  verification_id: string
  full_name: string
  email: string
  status: string
  verification_type: string
  created_at: string
  updated_at: string
}

export default function VerificationsPage() {
  const [verifications, setVerifications] = useState<Verification[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  useEffect(() => {
    fetchVerifications()
  }, [statusFilter, page])

  const fetchVerifications = async () => {
    try {
      setLoading(true)
      const params: any = { page }
      if (statusFilter !== 'all') {
        params.status_filter = statusFilter
      }
      
      const response = await api.get('/verifications/', { params })
      setVerifications(response.data.verifications || [])
      setTotalPages(response.data.total_pages || 1)
    } catch (error) {
      console.error('Error fetching verifications:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { variant: any; icon: any; label: string }> = {
      pending: { variant: 'secondary', icon: Clock, label: 'En attente' },
      in_review: { variant: 'default', icon: Eye, label: 'En révision' },
      approved: { variant: 'default', icon: CheckCircle, label: 'Approuvée' },
      rejected: { variant: 'destructive', icon: XCircle, label: 'Rejetée' },
    }
    
    const config = variants[status] || variants.pending
    const Icon = config.icon
    
    return (
      <Badge variant={config.variant} className="gap-1">
        <Icon className="h-3 w-3" />
        {config.label}
      </Badge>
    )
  }

  const filteredVerifications = verifications.filter(v => 
    v.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    v.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
    v.verification_id.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold">Vérifications</h2>
        <p className="text-muted-foreground">
          Gérez et suivez toutes vos vérifications d'identité
        </p>
      </div>

      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Rechercher par nom, email ou ID..."
            className="pl-10"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        
        <div className="flex gap-2">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[180px]">
              <Filter className="mr-2 h-4 w-4" />
              <SelectValue placeholder="Filtrer par statut" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Tous les statuts</SelectItem>
              <SelectItem value="pending">En attente</SelectItem>
              <SelectItem value="in_review">En révision</SelectItem>
              <SelectItem value="approved">Approuvées</SelectItem>
              <SelectItem value="rejected">Rejetées</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <FileCheck className="mx-auto h-12 w-12 animate-pulse text-muted-foreground" />
            <p className="mt-2 text-sm text-muted-foreground">Chargement...</p>
          </div>
        </div>
      ) : filteredVerifications.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <FileCheck className="h-12 w-12 text-muted-foreground" />
            <h3 className="mt-4 text-lg font-semibold">Aucune vérification</h3>
            <p className="mt-2 text-sm text-muted-foreground">
              {searchQuery ? 'Aucun résultat trouvé pour votre recherche' : 'Commencez par initier votre première vérification'}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredVerifications.map((verification) => (
            <Card key={verification.verification_id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <CardTitle className="text-lg">{verification.full_name}</CardTitle>
                    <CardDescription className="flex items-center gap-2">
                      <span>{verification.email}</span>
                      <span>•</span>
                      <span className="font-mono text-xs">{verification.verification_id}</span>
                    </CardDescription>
                  </div>
                  {getStatusBadge(verification.status)}
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      {new Date(verification.created_at).toLocaleDateString('fr-FR')}
                    </div>
                    <Badge variant="outline">{verification.verification_type}</Badge>
                  </div>
                  <Link href={`/company/dashboard/verifications/${verification.verification_id}`}>
                    <Button variant="outline" size="sm">
                      <Eye className="mr-2 h-4 w-4" />
                      Voir détails
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-center gap-2">
          <Button
            variant="outline"
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
          >
            Précédent
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} sur {totalPages}
          </span>
          <Button
            variant="outline"
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
          >
            Suivant
          </Button>
        </div>
      )}
    </div>
  )
}
