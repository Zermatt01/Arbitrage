# Script de Corrections Automatiques
# ==================================
# Ce script applique toutes les corrections nécessaires au projet

Write-Host "🔧 CORRECTIONS AUTOMATIQUES DU PROJET" -ForegroundColor Cyan
Write-Host "=" * 60

# 1. Renommer fichiers __init__ incorrects
Write-Host "`n📝 Étape 1: Renommer fichiers __init__.py incorrects" -ForegroundColor Yellow

if (Test-Path "src/models/models__init__.py") {
    Write-Host "  → Renommer models__init__.py → __init__.py"
    Move-Item "src/models/models__init__.py" "src/models/__init__.py" -Force
    Write-Host "  ✅ Fait" -ForegroundColor Green
} else {
    Write-Host "  ✓ models/__init__.py déjà correct" -ForegroundColor Green
}

if (Test-Path "src/config/config__init__.py") {
    Write-Host "  → Renommer config__init__.py → __init__.py"
    Move-Item "src/config/config__init__.py" "src/config/__init__.py" -Force
    Write-Host "  ✅ Fait" -ForegroundColor Green
} else {
    Write-Host "  ✓ config/__init__.py déjà correct" -ForegroundColor Green
}

# 2. Créer __init__.py manquants
Write-Host "`n📝 Étape 2: Créer __init__.py manquants" -ForegroundColor Yellow

$missing_inits = @(
    "src/database",
    "src/monitoring",
    "src/notifications",
    "src/reporting"
)

foreach ($dir in $missing_inits) {
    $init_file = Join-Path $dir "__init__.py"
    if (-not (Test-Path $init_file)) {
        Write-Host "  → Créer $init_file"
        "" | Out-File -FilePath $init_file -Encoding utf8
        Write-Host "  ✅ Créé" -ForegroundColor Green
    } else {
        Write-Host "  ✓ $init_file existe déjà" -ForegroundColor Green
    }
}

# 3. Ajouter .gitkeep dans dossiers vides
Write-Host "`n📝 Étape 3: Ajouter .gitkeep dans dossiers vides" -ForegroundColor Yellow

$empty_dirs = @(
    "src/monitoring",
    "src/notifications",
    "src/reporting"
)

foreach ($dir in $empty_dirs) {
    $gitkeep = Join-Path $dir ".gitkeep"
    if (-not (Test-Path $gitkeep)) {
        Write-Host "  → Créer $gitkeep"
        "# Fichier pour garder ce dossier dans Git" | Out-File -FilePath $gitkeep -Encoding utf8
        Write-Host "  ✅ Créé" -ForegroundColor Green
    } else {
        Write-Host "  ✓ $gitkeep existe déjà" -ForegroundColor Green
    }
}

# 4. Vérifier config/limits.json
Write-Host "`n📝 Étape 4: Vérifier config/limits.json" -ForegroundColor Yellow

if (-not (Test-Path "config/limits.json")) {
    Write-Host "  ⚠️  config/limits.json manquant!" -ForegroundColor Red
    Write-Host "  → Téléchargez le fichier limits.json fourni et placez-le dans config/"
} else {
    Write-Host "  ✓ config/limits.json existe" -ForegroundColor Green
}

# 5. Supprimer test_*.py à la racine (s'il en reste)
Write-Host "`n📝 Étape 5: Nettoyer test_*.py à la racine" -ForegroundColor Yellow

$root_tests = Get-ChildItem -Filter "test_*.py" -ErrorAction SilentlyContinue
if ($root_tests.Count -gt 0) {
    Write-Host "  → Trouver $($root_tests.Count) fichiers test_*.py à la racine"
    foreach ($test in $root_tests) {
        Write-Host "  → Supprimer $($test.Name)"
        Remove-Item $test.FullName
    }
    Write-Host "  ✅ Nettoyé" -ForegroundColor Green
} else {
    Write-Host "  ✓ Aucun test à la racine" -ForegroundColor Green
}

# 6. Vérifier structure des dossiers
Write-Host "`n📝 Étape 6: Vérifier structure du projet" -ForegroundColor Yellow

$required_dirs = @(
    "src/connectors",
    "src/collectors",
    "src/analyzers",
    "src/validators",
    "src/risk",
    "src/execution",
    "src/database",
    "src/models",
    "src/utils",
    "config",
    "tests",
    "scripts"
)

$all_ok = $true
foreach ($dir in $required_dirs) {
    if (Test-Path $dir) {
        Write-Host "  ✓ $dir" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $dir MANQUANT!" -ForegroundColor Red
        $all_ok = $false
    }
}

# 7. Vérifier fichiers essentiels
Write-Host "`n📝 Étape 7: Vérifier fichiers essentiels" -ForegroundColor Yellow

$required_files = @(
    ".gitignore",
    ".env.template",
    "README.md",
    "requirements.txt",
    "main.py"
)

foreach ($file in $required_files) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file MANQUANT!" -ForegroundColor Red
        $all_ok = $false
    }
}

# Résumé
Write-Host "`n" + ("=" * 60)
if ($all_ok) {
    Write-Host "✅ TOUTES LES CORRECTIONS APPLIQUÉES AVEC SUCCÈS!" -ForegroundColor Green
} else {
    Write-Host "⚠️  CERTAINS FICHIERS MANQUENT - Vérifiez ci-dessus" -ForegroundColor Yellow
}

Write-Host "`n📋 PROCHAINES ÉTAPES:" -ForegroundColor Cyan
Write-Host "  1. Vérifier que tout est correct"
Write-Host "  2. Ajouter les fichiers à Git:"
Write-Host "     git add ."
Write-Host "  3. Commiter:"
Write-Host "     git commit -m `"fix: Corrections structure et ajout documentation`""
Write-Host "  4. Pousser sur GitHub:"
Write-Host "     git push"
Write-Host ""
