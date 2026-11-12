param(
    [string]$Source = (Join-Path $PSScriptRoot '..\assets\pogoda-by-source.png')
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
    throw "Save the approved Pogoda.by PNG to $Source before building the integration icons."
}

Add-Type -AssemblyName System.Drawing
$brandDirectory = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\custom_components\pogoda_by\brand'))
[System.IO.Directory]::CreateDirectory($brandDirectory) | Out-Null
$sourceImage = [System.Drawing.Image]::FromFile([System.IO.Path]::GetFullPath($Source))

try {
    if ($sourceImage.Width -ne $sourceImage.Height) {
        throw 'The approved integration icon must be square.'
    }

    foreach ($size in @(256, 512)) {
        $fileName = if ($size -eq 256) { 'icon.png' } else { 'icon@2x.png' }
        $target = Join-Path $brandDirectory $fileName
        $bitmap = [System.Drawing.Bitmap]::new($size, $size, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        try {
            $graphics.CompositingMode = [System.Drawing.Drawing2D.CompositingMode]::SourceCopy
            $graphics.CompositingQuality = [System.Drawing.Drawing2D.CompositingQuality]::HighQuality
            $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
            $graphics.Clear([System.Drawing.Color]::Transparent)
            $graphics.DrawImage($sourceImage, [System.Drawing.Rectangle]::new(0, 0, $size, $size))
            $bitmap.Save($target, [System.Drawing.Imaging.ImageFormat]::Png)
            Write-Output "$fileName : ${size}x${size}"
        }
        finally {
            $graphics.Dispose()
            $bitmap.Dispose()
        }
    }
}
finally {
    $sourceImage.Dispose()
}
