#!/bin/bash
# stress-test.sh - Automated Kubernetes stress testing

set -e

NAMESPACE="iris-api"
SERVICE_NAME="iris-api-service"
DURATION="2m"
THREADS=12

echo "========================================"
echo "🔍 Iris API Stress Testing Suite"
echo "========================================"
echo ""

echo "🔍 Fetching external IP..."
EXTERNAL_IP=$(kubectl get service $SERVICE_NAME -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

if [ -z "$EXTERNAL_IP" ]; then
    echo "❌ External IP not found!"
    echo "   Check: kubectl get svc -n $NAMESPACE"
    exit 1
fi

echo "✅ External IP: $EXTERNAL_IP"
echo "🌐 API URL: http://$EXTERNAL_IP/"
echo ""

run_load_test() {
    local connections=$1
    local description=$2
    local duration=$3
    
    echo "========================================"
    echo "🧪 Test: $description"
    echo "   Connections: $connections"
    echo "   Duration: $duration"
    echo "   Threads: $THREADS"
    echo "========================================"
    
    wrk -t${THREADS} -c${connections} -d${duration} --latency \
        -s wrk_iris_predict.lua \
        http://${EXTERNAL_IP}/predict
    
    echo ""
    echo "📊 Pod Status:"
    kubectl get pods -n $NAMESPACE -o wide
    
    echo ""
    echo "📈 HPA Status:"
    kubectl get hpa -n $NAMESPACE
    
    echo ""
    echo "⏸️  Waiting 30 seconds before next test..."
    sleep 30
}

# Scenario 1: Baseline
run_load_test 100 "Baseline - 100 connections" "30s"

# Scenario 2: Moderate Load
run_load_test 500 "Moderate Load - 500 connections" "1m"

# Scenario 3: High Load (trigger autoscaling)
echo ""
echo "🔥 HIGH LOAD TEST - Triggering Autoscaling"
run_load_test 1000 "High Load - 1000 connections" "${DURATION}"

echo "⏳ Waiting 60 seconds for autoscaling to stabilize..."
sleep 60

echo ""
echo "📊 Current Pod Count:"
kubectl get pods -n $NAMESPACE

echo ""
echo "📈 Final HPA Status:"
kubectl get hpa iris-api-hpa -n $NAMESPACE

# Scenario 4: BOTTLENECK
echo ""
echo "========================================"
echo "⚠️  BOTTLENECK TEST"
echo "   Restricting to 1 pod, increasing to 2000 connections"
echo "========================================"

kubectl patch hpa iris-api-hpa -n $NAMESPACE --type='json' \
    -p='[{"op": "replace", "path": "/spec/maxReplicas", "value": 1}]'

echo "🔧 HPA restricted: maxReplicas = 1"
sleep 10

kubectl scale deployment iris-api-deployment -n $NAMESPACE --replicas=1

echo "⏳ Waiting for scale down to 1 pod..."
kubectl wait --for=condition=available --timeout=120s \
    deployment/iris-api-deployment -n $NAMESPACE || true

echo "✅ Scaled to 1 pod"
kubectl get pods -n $NAMESPACE

run_load_test 2000 "BOTTLENECK - 2000 connections with 1 pod ONLY" "2m"

echo ""
echo "========================================"
echo "✅ Stress Testing Complete!"
echo "========================================"

echo "🔄 Restoring HPA to maxReplicas=3..."
kubectl patch hpa iris-api-hpa -n $NAMESPACE --type='json' \
    -p='[{"op": "replace", "path": "/spec/maxReplicas", "value": 3}]'

echo "✅ HPA restored"
echo ""
echo "📋 Test Summary:"
echo "   ✅ Baseline: 100 connections"
echo "   ✅ Moderate: 500 connections"
echo "   ✅ High Load: 1000 connections (autoscaling triggered)"
echo "   ✅ Bottleneck: 2000 connections (1 pod only)"
echo ""
echo "📊 View detailed results above"
echo "📈 Monitor HPA: kubectl get hpa -n $NAMESPACE -w"
echo "🔍 Check logs: kubectl logs -n $NAMESPACE -l app=iris-api -f"
