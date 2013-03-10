openerp-idu-addons script de geocodificacion masiva
========================================================

El script resolve_geo_location.py esta concebido para hacer georreferenciación masiva de los datos. Esto debido a que el desarrollo de geocodificación asociado al módulo ocs_idu se desarrolló posteriormente a la puesta en producción.

El script hace un llamado REST a un geocodificador implementado con ArcGis Server para la capa de nomenclatura vial de bogotá.

Instrucciones de Uso:
=========================

1. Cree una variable de entorno PYTHONPATH que apunte hacia la carpeta en donde se encuentra el fichero geocoder.py:

export PYTHONPATH=/$PATH$/ocs_idu/geocoder

2. Ejecutar la aplicación:

Ejemplo:

python resolve_geo_location.py -H host:puerto -n nombre_bd -u usuarioBD -p passwordBD -c clases_a_georreferenciar


python resolve_geo_location.py -H localhost:5432 -n openerp-idu -u postgres -p ***** -c crm_claim,res_partner_address



