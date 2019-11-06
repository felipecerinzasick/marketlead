#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
source $DIR/db_info.sh

sudo -u postgres bash << EOF
    echo "DB User Password: $DBPASS"
    dropdb -U $DBUSER -W $DBNAME
EOF
