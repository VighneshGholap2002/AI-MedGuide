#!/bin/bash

# Import sample cases into MongoDB
echo "Importing sample clinical cases..."

mongoimport --uri="mongodb://admin:password@localhost:27017/clinical_summarizer" \
  --collection=patient_cases \
  --file=data/sample_cases.json \
  --jsonArray \
  --username=admin \
  --password=password \
  --authenticationDatabase=admin

echo "Sample cases imported successfully!"
