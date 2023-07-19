#!/bin/bash

if [ $# -lt 2 ]; then
    echo "Usage: $0 \$webhook_uri \$json_data"
    exit 0;
fi

curl -H "Content-Type:application/json" -d \@$2 $1

