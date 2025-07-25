#!/bin/bash

# SonarQube Local Scan Script
# This script helps you run SonarQube analysis locally

echo "🚀 Starting SonarQube Local Scan..."

# Check if Docker and Docker Compose are running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start SonarQube services if not already running
echo "📦 Starting SonarQube services..."
docker-compose up -d sonarqube-db sonarqube

# Wait for SonarQube to be ready
echo "⏳ Waiting for SonarQube to be ready..."
until curl -s http://localhost:9000/api/system/status | grep -q '"status":"UP"'; do
    echo "   SonarQube is starting up..."
    sleep 10
done

echo "✅ SonarQube is ready!"
echo "🌐 SonarQube Web UI: http://localhost:9000"
echo "   Default login: admin/admin"
echo "   ⚠️  You'll be prompted to change the password on first login"
echo "   Change it to: 2202210@SIT.singaporetech.edu.sg"
echo ""

# Check if sonar-scanner is installed
if command -v sonar-scanner &> /dev/null; then
    echo "🔍 Running SonarQube analysis..."
    echo "   Using custom password. If login fails, ensure you've changed the password in SonarQube UI first."
    sonar-scanner \
        -Dsonar.host.url=http://localhost:9000 \
        -Dsonar.login=admin \
        -Dsonar.password=2202210@SIT.singaporetech.edu.sg
    echo "✅ Analysis complete! Check results at http://localhost:9000"
else
    echo "📋 To run analysis, you need to install sonar-scanner:"
    echo "   macOS: brew install sonar-scanner"
    echo "   Or download from: https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/"
    echo ""
    echo "   Then run: sonar-scanner -Dsonar.host.url=http://localhost:9000 -Dsonar.login=admin -Dsonar.password=2202210@SIT.singaporetech.edu.sg"
fi

echo ""
echo "🛑 To stop SonarQube: docker-compose down"
