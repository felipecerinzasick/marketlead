#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
source $DIR/db_info.sh

sudo -u postgres bash << EOF
    createdb -O $DBUSER $DBNAME
EOF

