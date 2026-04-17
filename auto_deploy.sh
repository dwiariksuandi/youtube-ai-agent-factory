#!/bin/bash
git add .
git commit -m "Auto-deploy $(date '+%Y-%m-%d %H:%M') #MATTZAI" || echo "No changes"
git push origin main
echo "✅ AUTO-PUSH COMPLETE"
