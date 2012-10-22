#!/bin/bash
#call: script.sh production

PRODUCTION_MODE=0
ADDONS_PATH="/opt" #for production ,override in no production mode

if [ "$1" = "production" ]
then
    PRODUCTION_MODE=1
    # Make sure only root can run our script
    if [[ $EUID -ne 0 ]]; then
        echo "This script must be run as root" 1>&2
        exit 1
    fi
fi

########## FUNCTIONS #################
function development {
    ADDONS_PATH="$HOME/git/openerp-idu-addons"
    mkdir $ADDONS_PATH/externals/
    cd $ADDONS_PATH/externals/

    echo "ALTER USER openerp WITH PASSWORD 'openerp'" >> /tmp/openerp.sql
    sudo su postgres -c "psql -f /tmp/openerp.sql";
    rm /tmp/openerp.sql

    #crear el archivo de openerp para desarrollo
    CONFIG_FILE=$ADDONS_PATH/openerp-server.conf
    echo "creando archivo de configuración de openerp-server en $CONFIG_FILE ..."
    echo "[options]" > $CONFIG_FILE
    echo "db_host = False" >> $CONFIG_FILE
    echo "db_port = False" >> $CONFIG_FILE
    echo "db_user = openerp" >> $CONFIG_FILE
    echo "db_password = False" >> $CONFIG_FILE
    echo "addons_path = /usr/share/pyshared/openerp/addons/,$ADDONS_PATH/src,$ADDONS_PATH/externals/c2c-geoengine-addons" >> $CONFIG_FILE
}

function production {
    #crear el archivo de openerp para desarrollo
    CONFIG_FILE=/etc/openerp/openerp-server.conf
    echo "Actualizando archivo de configuración de openerp-server en $CONFIG_FILE ..."
    echo "addons_path = /usr/share/pyshared/openerp/addons/,$ADDONS_PATH/addons-idu,$ADDONS_PATH/c2c-geoengine-addons" >> $CONFIG_FILE
    echo "; xmlrpc_interface = 127.0.0.1" >> $CONFIG_FILE
    echo "; netrpc_interface = 127.0.0.1" >> $CONFIG_FILE
    echo "db_list = False" >> $CONFIG_FILE
}

#####################################################
#####################################################

if [ "$PRODUCTION_MODE" == 0 ]
then
     development
else
     production
fi

##Instalar geojson para geoengine
cd tmp
wget http://pypi.python.org/packages/source/g/geojson/geojson-1.0.tar.gz
tar zxvf geojson-1.0.tar.gz
cd geojson-1.0
sudo python setup.py install
rm geojson-1.0.tar.gz geojson-1.0 -rf

#Instalar c2c-geoengine - usado por ocs
cd $ADDONS_PATH
sudo bzr branch  http://bazaar.launchpad.net/~c2c/c2c-geoengine-addons/trunk/ c2c-geoengine-addons
