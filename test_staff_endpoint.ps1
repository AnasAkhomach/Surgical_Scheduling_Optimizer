$headers = @{
    'Authorization' = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwicm9sZSI6InVzZXIiLCJleHAiOjE3NDg3ODA3MTd9.yflalTYTlKv80iwXUJ8dlX_YXD8OV1qLgOuWyXW-gpg'
    'Content-Type' = 'application/json'
}

try {
    $response = Invoke-RestMethod -Uri 'http://localhost:5000/api/staff' -Headers $headers -Method GET
    Write-Host "Success! Response:"
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        Write-Host "Status: $($_.Exception.Response.StatusCode)"
        Write-Host "Response: $($_.Exception.Response.Content)"
    }
}