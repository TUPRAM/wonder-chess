# Shared read-only Shipping payload preflight; no process launch.
function Test-WCPackagedPayload {
    param($Manifest, [string]$PackageRoot)
    $resolvedRoot = [IO.Path]::GetFullPath($PackageRoot).TrimEnd('\','/')
    $payload = @($Manifest.files | Where-Object group -eq 'packaged_payload')
    if (-not $payload.Count -or $Manifest.input_files_stable_during_capture -ne $true) {
        throw 'Unverified payload provenance: a complete packaged_payload group and stable capture are required; legacy executable-only provenance cannot authorize this run'
    }
    $expectedPaths = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $verified = @()
    foreach ($item in $payload) {
        $path = [IO.Path]::GetFullPath($item.path)
        if (-not $path.StartsWith($resolvedRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Manifest payload path escapes package root' }
        if (-not $expectedPaths.Add($path)) { throw 'Duplicate packaged payload entry' }
        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Packaged payload file is missing: $path" }
        $before = Get-Item -LiteralPath $path
        $beforeSize = $before.Length
        $beforeTime = $before.LastWriteTimeUtc.Ticks
        $hash = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
        $after = Get-Item -LiteralPath $path
        if ($beforeSize -ne $after.Length -or $beforeTime -ne $after.LastWriteTimeUtc.Ticks -or $hash -ne $item.sha256 -or $after.Length -ne $item.bytes) {
            throw "Packaged payload differs from immutable provenance: $path"
        }
        $verified += [ordered]@{path=$path;bytes=$after.Length;sha256=$hash}
    }
    $actual = @(Get-ChildItem -LiteralPath $resolvedRoot -Recurse -File -Force | Where-Object {
        $relative = $_.FullName.Substring($resolvedRoot.Length + 1)
        'Saved' -notin ($relative -split '[\\/]')
    })
    if ($actual.Count -ne $expectedPaths.Count -or @($actual | Where-Object { -not $expectedPaths.Contains($_.FullName) }).Count) {
        throw 'Package file membership changed since provenance capture; only runtime Saved directories are excluded'
    }
    return [ordered]@{status='PASS';verified_utc=[DateTime]::UtcNow.ToString('o');files=$verified;file_count=$verified.Count
        excluded='Runtime Saved directories';boundary='All manifested packaged payload bytes and current file membership verified immediately before launch; source/art acceptance is separate'}
}
