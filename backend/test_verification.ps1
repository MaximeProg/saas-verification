$headers = @{
    "Authorization" = "Bearer sk_ag4zpz9x1eHRWljNWa0HVdSxXusn5tITSp4P7bNkPZs"
    "Content-Type" = "application/json"
}

$body = @{
    full_name = "Test User"
    email = "test@example.com"
    verification_type = "identity"
    external_reference = "TEST-001"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/verifications/initiate" -Method Post -Headers $headers -Body $body
    Write-Host "Success:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Error:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    if ($_.ErrorDetails.Message) {
        $_.ErrorDetails.Message | ConvertFrom-Json | ConvertTo-Json -Depth 10
    }
}
