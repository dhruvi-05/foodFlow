#!/usr/bin/env bash
set -euo pipefail

echo "============================================================"
echo "WasteWise AI - AWS SAM Infrastructure Deployment"
echo "============================================================"

cd "$(dirname "$0")/../infra"

echo "Step 1: Building SAM Stack..."
sam build --parallel

echo "Step 2: Deploying to AWS..."
sam deploy --no-confirm-changeset --no-fail-on-empty-changeset

echo "Step 3: Fetching API Gateway URL..."
API=$(aws cloudformation describe-stacks --stack-name wastewise \
  --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text)

echo "Deployment Successful!"
echo "API Endpoint: $API"
echo "NEXT_PUBLIC_API_URL=$API" > ../frontend/.env.production

echo "Step 4: Running Health Smoke Test..."
curl -fsS "$API/api/plan?restaurant_id=R001&date=2026-09-19" > /dev/null && echo "✅ Smoke test OK! API active."
