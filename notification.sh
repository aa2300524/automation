#!/bin/bash

# sh SendMessage.sh 
# 'https://asus.webhook.office.com/webhookb2/08e42c77-7185-4cae-ad87-1ff3a4855166@301f59c4-c269-4a66-8a8c-f5daab211fa3/
# IncomingWebhook/cd614c68599345ceac62f82437a9d096/ba639ed9-4805-4b69-bd25-8f3fd4c30042' data.json

# cat data.json | sed 's/TITLE_NAME/ZL/' | sed 's/DESCRIPTION/ZL/' | sed 's/COLOR/#####/' 
# | sed 's/NAME_1/#####/' | sed 's/CONTENT_1/#####/' | sed 's/NAME_2/#####/' | sed 's/CONTENT_2/#####/' 
# | sed 's/URL/V/'  > data.json

if [ $# -lt 2 ]; then
    echo "Usage: $0 \$webhook_uri \$json_data"
    exit 0;
fi

curl -H "Content-Type:application/json" -d \@$2 $1

sleep 2