# First, get a fresh token using OAuth2 form data
$loginData = "username=user123&password=password123"

try {
    Write-Host "Getting fresh token..."
    $loginResponse = Invoke-RestMethod -Uri 'http://localhost:5000/api/auth/token' -Method POST -Body $loginData -ContentType 'application/x-www-form-urlencoded'
    $token = $loginResponse.access_token
    Write-Host "Token obtained: $($token.Substring(0,20))..."

    # Now test the staff endpoint
    $headers = @{
        'Authorization' = "Bearer $token"
        'Content-Type' = 'application/json'
    }

    Write-Host "Testing staff endpoint..."
    $staffResponse = Invoke-RestMethod -Uri 'http://localhost:5000/api/staff' -Headers $headers -Method GET
    Write-Host "Staff endpoint success! Response:"
    $staffResponse | ConvertTo-Json -Depth 10

} catch {
    Write-Host "Error: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        Write-Host "Status: $($_.Exception.Response.StatusCode)"
    }
}