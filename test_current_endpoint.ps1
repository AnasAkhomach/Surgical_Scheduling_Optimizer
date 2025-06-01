# PowerShell script to test the current endpoint
$baseUrl = "http://localhost:5000"

try {
    Write-Host "Testing authentication..."

    # Authentication request
    $authBody = @{
        username = "admin"
        password = "admin123"
    } | ConvertTo-Json

    $authHeaders = @{
        "Content-Type" = "application/json"
    }

    $authResponse = Invoke-WebRequest -Uri "$baseUrl/api/auth/login" -Method POST -Body $authBody -Headers $authHeaders -UseBasicParsing

    Write-Host "Auth Status Code: $($authResponse.StatusCode)"

    if ($authResponse.StatusCode -eq 200) {
        $authData = $authResponse.Content | ConvertFrom-Json
        $token = $authData.access_token

        Write-Host "Token received: $($token.Substring(0, 20))..."

        # Test current endpoint
        Write-Host "Testing /api/current endpoint..."

        $currentHeaders = @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }

        $currentResponse = Invoke-WebRequest -Uri "$baseUrl/api/current" -Method GET -Headers $currentHeaders -UseBasicParsing

        Write-Host "Current endpoint Status Code: $($currentResponse.StatusCode)"
        Write-Host "Response Content Type: $($currentResponse.Headers['Content-Type'])"
        Write-Host "Response Content Length: $($currentResponse.Content.Length)"
        Write-Host "Response Content: $($currentResponse.Content)"

        # Try to parse as JSON
        try {
            $currentData = $currentResponse.Content | ConvertFrom-Json
            Write-Host "Parsed JSON successfully"
            Write-Host "Data type: $($currentData.GetType().Name)"

            if ($currentData -is [System.Object[]]) {
                Write-Host "Response is an array with $($currentData.Length) items"
            } elseif ($currentData.PSObject.Properties) {
                Write-Host "Response object properties: $($currentData.PSObject.Properties.Name -join ', ')"
            }
        } catch {
            Write-Host "Failed to parse JSON: $($_.Exception.Message)"
        }

    } else {
        Write-Host "Authentication failed: $($authResponse.Content)"
    }

} catch {
    Write-Host "Error: $($_.Exception.Message)"
    Write-Host "Error Details: $($_.Exception.ToString())"
}