$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing

$ManualRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$BaseDir = Join-Path $ManualRoot 'capturas\base'
$FinalDir = Join-Path $ManualRoot 'capturas\finales'
$ManifestPath = Join-Path $FinalDir 'metadata_capturas_finales.json'

if (-not ($ManualRoot.Path -like 'C:\Projects\pre_explotaglobos\docs\manual_usuario*')) {
    throw "Ruta no autorizada: $($ManualRoot.Path)"
}

New-Item -ItemType Directory -Force -Path $FinalDir | Out-Null

$cropSpecs = @{
    'MU-005-registro-escolar.png' = @{ X = 70;  Y = 115; W = 1240; H = 760; Reason = 'Recorte del formulario escolar diligenciado, conservando panel lateral y accion de envio.' }
    'MU-007-registro-universitario.png' = @{ X = 70;  Y = 115; W = 1240; H = 760; Reason = 'Recorte del formulario universitario y campo semestre, conservando contexto de registro.' }
    'MU-016-formato-manual.png' = @{ X = 85;  Y = 270; W = 1260; H = 610; Reason = 'Recorte de la zona de configuracion inicial editable.' }
    'MU-017-distribucion-grupos.png' = @{ X = 85;  Y = 270; W = 1260; H = 610; Reason = 'Recorte de la distribucion manual con selects y filas de participantes.' }
    'MU-025-propuesta-manual.png' = @{ X = 300; Y = 115; W = 890;  H = 720; Reason = 'Recorte del modal/asistente de fase manual y propuesta visible.' }
    'MU-034-nueva-plantilla.png' = @{ X = 95;  Y = 145; W = 1180; H = 650; Reason = 'Recorte del formulario de nueva plantilla DOCX.' }
    'MU-037-destinatario-manual.png' = @{ X = 650; Y = 150; W = 660;  H = 650; Reason = 'Recorte del formulario de destinatario manual.' }
    'MU-041-admin-registros.png' = @{ X = 300; Y = 85;  W = 1110; H = 500; Reason = 'Recorte del listado admin de registros ficticios, con filtros y acciones.' }
    'MU-042-admin-torneo.png' = @{ X = 300; Y = 85;  W = 1110; H = 500; Reason = 'Recorte del listado admin de competencias ficticias.' }
}

$annotationSpecs = @{
    'MU-014-generar-competencia.png' = @(
        @{ N = 1; X = 940; Y = 610; W = 360; H = 90; Label = '' },
        @{ N = 2; X = 120; Y = 405; W = 1180; H = 185; Label = '' }
    )
    'MU-020-guardar-todos.png' = @(
        @{ N = 1; X = 955; Y = 470; W = 330; H = 70; Label = '' },
        @{ N = 2; X = 120; Y = 410; W = 1180; H = 450; Label = '' }
    )
    'MU-022-crear-fase-recomendada.png' = @(
        @{ N = 1; X = 930; Y = 480; W = 360; H = 75; Label = '' },
        @{ N = 2; X = 145; Y = 575; W = 1130; H = 245; Label = '' }
    )
    'MU-023-repechaje.png' = @(
        @{ N = 1; X = 890; Y = 500; W = 370; H = 70; Label = '' },
        @{ N = 2; X = 135; Y = 600; W = 1140; H = 240; Label = '' }
    )
    'MU-024-asistente-manual.png' = @(
        @{ N = 1; X = 135; Y = 500; W = 1140; H = 250; Label = '' },
        @{ N = 2; X = 935; Y = 765; W = 340; H = 65; Label = '' }
    )
    'MU-030-edicion-participante.png' = @(
        @{ N = 1; X = 440; Y = 145; W = 560; H = 100; Label = '' },
        @{ N = 2; X = 430; Y = 360; W = 610; H = 310; Label = '' },
        @{ N = 3; X = 780; Y = 720; W = 250; H = 60; Label = '' }
    )
}

function Copy-Bitmap($sourcePath, $targetPath) {
    $img = [System.Drawing.Image]::FromFile($sourcePath)
    try {
        $bmp = New-Object System.Drawing.Bitmap $img.Width, $img.Height, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        try {
            $g.DrawImage($img, 0, 0, $img.Width, $img.Height)
        } finally {
            $g.Dispose()
        }
        $savePath = $targetPath
        $replaceAfterSave = $false
        if ([string]::Equals((Resolve-Path -LiteralPath $sourcePath).Path, $targetPath, [System.StringComparison]::OrdinalIgnoreCase)) {
            $savePath = "$targetPath.tmp.png"
            $replaceAfterSave = $true
        }
        $bmp.Save($savePath, [System.Drawing.Imaging.ImageFormat]::Png)
        if ($replaceAfterSave) {
            Move-Item -LiteralPath $savePath -Destination $targetPath -Force
        }
        $result = @{ Width = $bmp.Width; Height = $bmp.Height }
        $bmp.Dispose()
        return $result
    } finally {
        $img.Dispose()
    }
}

function Crop-Bitmap($sourcePath, $targetPath, $spec) {
    $img = [System.Drawing.Image]::FromFile($sourcePath)
    try {
        $rect = New-Object System.Drawing.Rectangle $spec.X, $spec.Y, $spec.W, $spec.H
        $bmp = New-Object System.Drawing.Bitmap $spec.W, $spec.H, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        try {
            $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
            $g.DrawImage($img, (New-Object System.Drawing.Rectangle 0, 0, $spec.W, $spec.H), $rect, [System.Drawing.GraphicsUnit]::Pixel)
        } finally {
            $g.Dispose()
        }
        $savePath = $targetPath
        $replaceAfterSave = $false
        if ([string]::Equals((Resolve-Path -LiteralPath $sourcePath).Path, $targetPath, [System.StringComparison]::OrdinalIgnoreCase)) {
            $savePath = "$targetPath.tmp.png"
            $replaceAfterSave = $true
        }
        $bmp.Save($savePath, [System.Drawing.Imaging.ImageFormat]::Png)
        if ($replaceAfterSave) {
            Move-Item -LiteralPath $savePath -Destination $targetPath -Force
        }
        $result = @{ Width = $bmp.Width; Height = $bmp.Height; Region = "$($spec.X),$($spec.Y),$($spec.W),$($spec.H)" }
        $bmp.Dispose()
        return $result
    } finally {
        $img.Dispose()
    }
}

function Annotate-Bitmap($sourcePath, $targetPath, $items) {
    $img = [System.Drawing.Image]::FromFile($sourcePath)
    try {
        $bmp = New-Object System.Drawing.Bitmap $img.Width, $img.Height, ([System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        try {
            $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
            $g.DrawImage($img, 0, 0, $img.Width, $img.Height)

            $highlight = [System.Drawing.Color]::FromArgb(230, 0, 112, 150)
            $fill = [System.Drawing.Color]::FromArgb(14, 0, 112, 150)
            $safe = [System.Drawing.Color]::FromArgb(235, 36, 148, 88)
            $white = [System.Drawing.Color]::White
            $pen = New-Object System.Drawing.Pen $highlight, 3
            $brush = New-Object System.Drawing.SolidBrush $fill
            $numBrush = New-Object System.Drawing.SolidBrush $safe
            $textBrush = New-Object System.Drawing.SolidBrush $white
            $font = New-Object System.Drawing.Font 'Arial', 24, ([System.Drawing.FontStyle]::Bold), ([System.Drawing.GraphicsUnit]::Pixel)
            $smallFont = New-Object System.Drawing.Font 'Arial', 15, ([System.Drawing.FontStyle]::Bold), ([System.Drawing.GraphicsUnit]::Pixel)
            try {
                foreach ($item in $items) {
                    $rect = New-Object System.Drawing.Rectangle $item.X, $item.Y, $item.W, $item.H
                    $g.FillRectangle($brush, $rect)
                    $g.DrawRectangle($pen, $rect)
                    $cx = [Math]::Max(12, $item.X - 18)
                    $cy = [Math]::Max(12, $item.Y - 18)
                    $circle = New-Object System.Drawing.Rectangle $cx, $cy, 38, 38
                    $circleText = New-Object System.Drawing.RectangleF ([single]$cx), ([single]$cy), ([single]38), ([single]38)
                    $g.FillEllipse($numBrush, $circle)
                    $g.DrawEllipse($pen, $circle)
                    $sf = New-Object System.Drawing.StringFormat
                    $sf.Alignment = [System.Drawing.StringAlignment]::Center
                    $sf.LineAlignment = [System.Drawing.StringAlignment]::Center
                    $g.DrawString([string]$item.N, $font, $textBrush, $circleText, $sf)
                    $sf.Dispose()
                    if ($item.Label) {
                        $labelRect = New-Object System.Drawing.RectangleF ([single]($circle.Right + 6)), ([single]$cy), ([single]220), ([single]38)
                        $g.DrawString($item.Label, $smallFont, $textBrush, $labelRect)
                    }
                }
            } finally {
                $pen.Dispose(); $brush.Dispose(); $numBrush.Dispose(); $textBrush.Dispose(); $font.Dispose(); $smallFont.Dispose()
            }
        } finally {
            $g.Dispose()
        }
        $savePath = $targetPath
        $replaceAfterSave = $false
        if ([string]::Equals((Resolve-Path -LiteralPath $sourcePath).Path, $targetPath, [System.StringComparison]::OrdinalIgnoreCase)) {
            $savePath = "$targetPath.tmp.png"
            $replaceAfterSave = $true
        }
        $bmp.Save($savePath, [System.Drawing.Imaging.ImageFormat]::Png)
        $result = @{ Width = $bmp.Width; Height = $bmp.Height; Markers = $items.Count }
        $bmp.Dispose()
        if ($replaceAfterSave) {
            $img.Dispose()
            Move-Item -LiteralPath $savePath -Destination $targetPath -Force
        }
        return $result
    } finally {
        $img.Dispose()
    }
}

$manifest = @()
Get-ChildItem -LiteralPath $BaseDir -Filter 'MU-*.png' | Sort-Object Name | ForEach-Object {
    $source = $_.FullName
    $target = Join-Path $FinalDir $_.Name
    $sourceInfo = [System.Drawing.Image]::FromFile($source)
    $original = @{ Width = $sourceInfo.Width; Height = $sourceInfo.Height }
    $sourceInfo.Dispose()

    $kind = 'COPIA_BASE'
    $final = $null
    $region = '0,0,1440,900'
    $reason = 'Copia final sin recorte ni anotacion.'
    $markers = 0

    if ($cropSpecs.ContainsKey($_.Name)) {
        $spec = $cropSpecs[$_.Name]
        $final = Crop-Bitmap $source $target $spec
        $kind = 'RECORTE'
        $region = $final.Region
        $reason = $spec.Reason
    } else {
        $final = Copy-Bitmap $source $target
    }

    if ($annotationSpecs.ContainsKey($_.Name)) {
        $items = $annotationSpecs[$_.Name]
        $final = Annotate-Bitmap $target $target $items
        $kind = if ($kind -eq 'RECORTE') { 'RECORTE_Y_ANOTACION' } else { 'ANOTACION' }
        $markers = $final.Markers
        $reason = 'Anotacion uniforme con marcadores numerados y recuadros discretos.'
    }

    if ($_.Name -in @('MU-019-guardar-grupo.png', 'MU-028-confirmacion-correccion.png')) {
        $kind = 'CAPTURA_PREVIA_DIALOGO_NATIVO'
        $reason = 'Se conserva la captura previa; el dialogo nativo se resuelve mediante elemento editorial LaTeX.'
    }

    $manifest += [PSCustomObject]@{
        id = $_.BaseName.Substring(0, 6)
        archivo = $_.Name
        tipo = $kind
        original = "$($original.Width)x$($original.Height)"
        final = "$($final.Width)x$($final.Height)"
        region = $region
        marcadores = $markers
        privacidad = 'OK'
        justificacion = $reason
    }
}

$manifest | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $ManifestPath -Encoding UTF8
"CAPTURAS_FINALES=$($manifest.Count)"
