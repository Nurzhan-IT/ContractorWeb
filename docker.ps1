# docker.ps1 — Shortcuts for the local Docker Compose workflow.
# Usage: .\docker.ps1 <command>
#   build    docker compose build
#   up       docker compose up --build (foreground; Ctrl+C to stop)
#   down     docker compose down
#   migrate  docker compose exec web python manage.py migrate
#   shell    docker compose exec web python manage.py shell
#   test     docker compose exec web python manage.py test

param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet('build', 'up', 'down', 'migrate', 'shell', 'test')]
    [string]$Command
)

Set-Location $PSScriptRoot

switch ($Command) {
    'build'   { docker compose build }
    'up'      { docker compose up --build }
    'down'    { docker compose down }
    'migrate' { docker compose exec web python manage.py migrate }
    'shell'   { docker compose exec web python manage.py shell }
    'test'    { docker compose exec web python manage.py test }
}

exit $LASTEXITCODE
