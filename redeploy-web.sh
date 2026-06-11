#!/bin/bash
# Rebuild the Expo web bundle and redeploy it to the public Heroku web app.
# Run from "NowTrendin v2.0/". Use this after any frontend change you want live
# on the web URL while traveling.
set -e
cd "$(dirname "$0")"
echo "Building web bundle…"
( cd frontend && npx expo export --platform web )
rm -rf web-deploy/dist && cp -r frontend/dist web-deploy/dist
cd web-deploy
git add -A && git commit -q -m "web rebuild $(date +%Y-%m-%d)" || echo "(no changes)"
git push heroku HEAD:main
echo "Done → https://nowtrendin-web-8c1bb8c9f7f2.herokuapp.com/"
