#!/bin/bash

# Build Docker image
docker build -t ai-financial-planning-agent .

# Run Docker container locally
docker run -p 8000:8000 ai-financial-planning-agent

# Note: For AWS Lambda deployment, consider using AWS SAM or Serverless Framework
# This script is a starting point for local testing and containerization.
