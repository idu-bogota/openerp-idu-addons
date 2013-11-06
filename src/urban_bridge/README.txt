URBAN BRIDGE
==================

Urban Bridge es un módulo que implementa la conceptualización de un BMS (Bridge Manamgement System). 
Comprende hasta el momento inventario y diagnóstico, sin embargo se pretende llegar a cerrar todo el ciclo de negocio integrado con el erp.

=================================
Instrucciones de Instalación
=================================


1. Instalar la libreria xlrd que lee ficheros de excel 2007 en adelante

wget --no-check-certificate https://pypi.python.org/packages/source/x/xlrd/xlrd-0.9.2.tar.gz#md5=91a81ee76233e9f3115acaaa1b251b0e
tar -xvzf xlrd-0.9.2.tar.gz
cd xlrd-0.9.2
sudo python setup.py build
sudo python setup.py install

2. Instalar la libreria Shapely que servirá para recibir datos geográficos en formato geojson por el webservice de openerp

sudo easy_install shapely

3. Instalar el módulo base_map (necesario para hacer geoprocesamiento con capas base de geografía existente)

4. Instalar el módulo urban_bridge

5. Parametrizar
