#!/bin/bash

COLOR_R="d7000d"
COLOR_B="0078D7"
F_TEMPLATE="data.template"
F_OUT="data.json"

if [ $# -lt 5 ]; then
    echo "Usage: $0 \$webhook_uri \$TYPE[INFO|ERROR] \$title \$Message \$Link"
    exit 0;
fi

if [ $2 == "INFO" ]; then
    sed "s#T_COLOR#$COLOR_B#" $F_TEMPLATE > $F_OUT
else
    sed "s#T_COLOR#$COLOR_R#" $F_TEMPLATE > $F_OUT
fi

sed -i "s#C_TITLE#${3}#" $F_OUT
sed -i "s#C_TEXT#${4}#" $F_OUT
sed -i "s#B_NAME#${5}#" $F_OUT
sed -i "s#B_LINK#${5}#" $F_OUT

curl -H "Content-Type:application/json" -d \@$F_OUT $1
#rm $F_OUT
