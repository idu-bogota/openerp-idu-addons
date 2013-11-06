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

5. El módulo urban_bridge requiere las coordenadas geográficas cartesianas para Bogotá, por tanto se agrega la línea correspondiente en el
postgis
En PGAdmin ejecutar la siguiente consulta:

INSERT into spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) values ( 96873, 'sr-org', 6873, '+proj=tmerc +lat_0=4.680486111 
+lon_0=-74.14659167000001 +k=1 +x_0=92334.879 +y_0=109320.965 +a=6380687 +b=6359293.764473119 +units=m +no_defs ', 'PROJCS["PCS_CarMAGBOG",
GEOGCS["GCS_CarMAGBOG",DATUM["CGS_CarMAGBOG",SPHEROID["GRS80 Mod",6380687.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",
0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",92334.879],PARAMETER["False_Northing",109320.965],
PARAMETER["Central_Meridian",-74.14659167],PARAMETER["Scale_Factor",1.0],PARAMETER["Latitude_Of_Origin",4.680486111],UNIT["Meter",1.0]]');

5. Parametrizar
