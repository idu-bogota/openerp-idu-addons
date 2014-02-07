##############################################################################
#
#    Copyright (C) 2013 Instituto de Desarrollo Urbano (<http://www.idu.gov.co>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from suds.client import Client

url = 'http://172.16.2.233:9763/services/ws_stone_plan_contratacion?wsdl'
client = Client(url)
#===============================================================================
# print client
# client.set_options (port = 'SOAP11Endpoint')
# print client.service.obtener_centro_costo ().COD_CCOS
# print client.service.obtener_centro_costo ().NOM_CCOS
# print client.service.obtener_proyecto_punto_inversion(20202, )
# print client.service.obtener_proyecto_punto_inversion(20202, ).proyecto
# print len((client.service.obtener_centro_costo ().COD_CCOS))
#===============================================================================



class stone_erp_idu_centro_costo(osv.osv):
    _name = "stone_erp_idu.centro_costo"

    _columns = {
        'codigo': fields.char('Codigo', required=True, select=True),
        'nombre':fields.char('Nombre', size=255, required=True, select=True),
        'codigo_proyecto_obra': fields.integer ('Codigo', required=True, select=True),
        'nombre_proyecto_obra': fields.char('Nombre', size=255, required=True, select=True),
        'codigo_punto_inversion': fields.integer ('Codigo', required=True, select=True),
        'nombre_punto_inversion':fields.char('Nombre', size=255, required=True, select=True),
    }

stone_erp_idu_centro_costo()

def obtener_centro_costo():
    lista= {}
    total = len((client.service.obtener_centro_costo ().COD_CCOS))
    for a in total:
        lista[a] = client.service.obtener_centro_costo ().COD_CCOS[a]
    return lista
