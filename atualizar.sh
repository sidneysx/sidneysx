#!/bin/sh
# Gera o README/SVGs com o Uptime de hoje e sobe pro GitHub (só commita se mudou)
set -e
cd "$(dirname "$0")"
git pull --rebase --autostash -q
python3 gerar-readme.py
git add README.md dark_mode.svg light_mode.svg
git diff --cached --quiet || { git commit -qm "Atualiza uptime" && git push -q; }
