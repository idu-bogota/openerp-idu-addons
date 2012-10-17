#!/bin/bash
cd ~/git/openerp-idu-addons/externals/

#zend framework
#svn co http://framework.zend.com/svn/framework/standard/tags/release-1.12.0/library/ zend
ZF_RELEASE='ZendFramework-1.12.0'
wget "http://packages.zendframework.com/releases/$ZF_RELEASE/$ZF_RELEASE-minimal.tar.gz"
tar zxvf "$ZF_RELEASE-minimal.tar.gz"
mv "$ZF_RELEASE-minimal" zend
rm "$ZF_RELEASE-minimal.tar.gz"

#La version de eclipse que viene en ubuntu 12.04 no maneja apropiadamente los submodules,
#por lo tanto este script se va a usar para descargar las dependencias.

git clone https://github.com/shiflett/testmore.git testmore-php

