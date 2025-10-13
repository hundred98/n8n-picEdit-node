# PowerShell script to get comprehensive system fonts
Write-Host "=== Windows System Fonts ==="

# Method 1: Get fonts from Windows Fonts directory
$fontDir = "C:\Windows\Fonts"
$fontFiles = Get-ChildItem -Path $fontDir -Name "*.ttf", "*.otf" | Sort-Object

Write-Host "`n=== Font Files in $fontDir ==="
$fontFiles | ForEach-Object {
    $fontName = $_.Replace('.ttf', '').Replace('.otf', '')
    Write-Host $fontName
}

Write-Host "`n=== Total Font Files: $($fontFiles.Count) ==="

# Method 2: Get fonts from registry
Write-Host "`n=== Registry Fonts ==="
try {
    $registryFonts = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts" -ErrorAction SilentlyContinue
    if ($registryFonts) {
        $registryFonts.PSObject.Properties | Where-Object { $_.Name -notlike "PS*" } | ForEach-Object {
            $fontName = $_.Name -replace ' \(TrueType\)', '' -replace ' \(OpenType\)', ''
            Write-Host $fontName
        } | Sort-Object | Get-Unique
    }
} catch {
    Write-Host "Could not access font registry"
}

Write-Host "`n=== Common Web-Safe Fonts ==="
$webSafeFonts = @(
    "Arial",
    "Arial Black", 
    "Arial Narrow",
    "Calibri",
    "Cambria",
    "Comic Sans MS",
    "Consolas",
    "Courier New",
    "Georgia",
    "Helvetica",
    "Impact",
    "Lucida Console",
    "Lucida Sans Unicode",
    "Microsoft Sans Serif",
    "Palatino Linotype",
    "Segoe UI",
    "Tahoma",
    "Times New Roman",
    "Trebuchet MS",
    "Verdana"
)

$webSafeFonts | Sort-Object | ForEach-Object {
    Write-Host $_
}