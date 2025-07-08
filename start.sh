#!/bin/bash

set -e

echo "Building images *if needed* and starting Ollama server..."
docker-compose up --build -d ollama_server

echo "Waiting for Ollama to pass healthcheck..."

while ! curl -s http://localhost:11434 | grep -q 'Ollama'; do
  echo "🔄 Ollama not ready yet — waiting..."
  sleep 3
done

echo "Ollama is healthy!"

echo "Pulling the model..."
docker-compose exec ollama_server ollama pull mistral

echo "Bringing up Streamlit app..."
docker-compose up -d chatwithpdf

echo ""
echo "All set!"
echo "   - App:   http://<your-linux-ip>:8501"
echo "   - Ollama: http://<your-linux-ip>:11434"
echo ""
echo "To stop: docker-compose down"
echo "To see logs: docker-compose logs -f"
