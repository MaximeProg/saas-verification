# Test 1: Tenter d'acheter un plan SANS documents validés (doit bloquer)
Write-Host "`n=== TEST 1: Achat sans documents validés ===" -ForegroundColor Yellow

$headers = @{
    "Authorization" = "Bearer sk_ag4zpz9x1eHRWljNWa0HVdSxXusn5tITSp4P7bNkPZs"
    "Content-Type" = "application/json"
}

# D'abord, récupérer les plans disponibles
Write-Host "`nRécupération des plans disponibles..." -ForegroundColor Cyan
try {
    $plans = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/subscription-plans/public" -Method Get
    Write-Host "Plans disponibles:" -ForegroundColor Green
    $plans | ForEach-Object {
        Write-Host "  - $($_.name) ($($_.slug)): $($_.price) $($_.currency)/$($_.billing_period)" -ForegroundColor White
        Write-Host "    ID: $($_.id)" -ForegroundColor Gray
    }
    
    # Prendre le premier plan pour le test
    $planId = $plans[0].id
    Write-Host "`nPlan sélectionné pour le test: $($plans[0].name) (ID: $planId)" -ForegroundColor Cyan
} catch {
    Write-Host "Erreur lors de la récupération des plans:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit
}

# Tenter d'initialiser un paiement
Write-Host "`nTentative d'achat du plan..." -ForegroundColor Cyan
$body = @{
    plan_id = $planId
    payment_method = "mobile_money"
    customer_email = "kouassimaxime540@gmail.com"
    customer_phone = "+22997000000"
    callback_url = "http://localhost:3000/payment/callback"
    return_url = "http://localhost:3000/payment/success"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/payments/initialize" -Method Post -Headers $headers -Body $body
    Write-Host "✅ Paiement initialisé avec succès!" -ForegroundColor Green
    Write-Host "Payment ID: $($response.payment_id)" -ForegroundColor Cyan
    Write-Host "Reference: $($response.payment_reference)" -ForegroundColor Cyan
    Write-Host "Amount: $($response.amount) $($response.currency)" -ForegroundColor Cyan
    Write-Host "Payment URL: $($response.payment_url)" -ForegroundColor Cyan
    Write-Host "Status: $($response.status)" -ForegroundColor Cyan
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 403) {
        Write-Host "✅ Résultat attendu - Paiement bloqué (403):" -ForegroundColor Green
    } else {
        Write-Host "Erreur inattendue ($statusCode):" -ForegroundColor Red
    }
    
    if ($_.ErrorDetails.Message) {
        try {
            $errorData = $_.ErrorDetails.Message | ConvertFrom-Json
            Write-Host "  Message: $($errorData.detail)" -ForegroundColor Yellow
        } catch {
            Write-Host "  Message brut: $($_.ErrorDetails.Message)" -ForegroundColor Yellow
        }
    } else {
        Write-Host $_.Exception.Message
    }
}

Write-Host "`n=== FIN DU TEST ===" -ForegroundColor Yellow
