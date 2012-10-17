#!/bin/bash
ADDONS_PATH="$HOME/git/openerp-idu-addons"
mkdir $ADDONS_PATH/externals/
cd $ADDONS_PATH/externals/

#zend framework
#svn co http://framework.zend.com/svn/framework/standard/tags/release-1.12.0/library/ zend
ZF_RELEASE='ZendFramework-1.12.0'
wget "http://packages.zendframework.com/releases/$ZF_RELEASE/$ZF_RELEASE-minimal.tar.gz"
tar zxvf "$ZF_RELEASE-minimal.tar.gz"
mv "$ZF_RELEASE-minimal" zend
rm "$ZF_RELEASE-minimal.tar.gz"

#no como submodulo porque el eclipse empaquetado en ubuntu 12.04 no los maneja apropiadamente
#php testmore - usado para probar el cliente php de openerp
git clone https://github.com/shiflett/testmore.git testmore-php

#c2c-geoengine - usado por ocs
bzr branch  http://bazaar.launchpad.net/~c2c/c2c-geoengine-addons/trunk/ c2c-geoengine-addons

#crear el archivo de openerp para desarrollo
CONFIG_FILE=$ADDONS_PATH/openerp-server.conf
echo "creando archivo de configuración de openerp-server en $CONFIG_FILE ..."
echo "[options]" > $CONFIG_FILE
echo "db_host = False" >> $CONFIG_FILE
echo "db_port = False" >> $CONFIG_FILE
echo "db_user = openerp" >> $CONFIG_FILE
echo "db_password = False" >> $CONFIG_FILE
echo "addons_path = /usr/share/pyshared/openerp/addons/,$ADDONS_PATH/src,$ADDONS_PATH/externals/c2c-geoengine-addons" >> $CONFIG_FILE
