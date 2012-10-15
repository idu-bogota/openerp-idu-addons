#!/bin/bash
#zend framework
#svn co http://framework.zend.com/svn/framework/standard/tags/release-1.12.0/library/ zend
ZF_RELEASE='ZendFramework-1.12.0'
wget "http://packages.zendframework.com/releases/$ZF_RELEASE/$ZF_RELEASE-minimal.tar.gz"
tar zxvf "$ZF_RELEASE-minimal.tar.gz"
mv "$ZF_RELEASE-minimal" zend
rm "$ZF_RELEASE-minimal.tar.gz"