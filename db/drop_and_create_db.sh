#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
source $DIR/db_info.sh

sudo -u postgres bash << EOF
    psql -c "drop database $DBNAME" && createdb -O $DBUSER $DBNAME
EOF
