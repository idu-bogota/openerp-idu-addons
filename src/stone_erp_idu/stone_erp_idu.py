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
import stone_client_ws
#===============================================================================

class stone_erp_idu_centro_costo(osv.osv):
    _name = "stone_erp_idu.centro_costo"    

    _columns = {
        'codigo': fields.char('Codigo', required=True, select=True),
        'name':fields.char('Nombre', size=255, required=True, select=True),
        #'proyecto_id':fields.many2one('plan_contratacion_idu.clasificador_proyectos','Proyecto'),
        'punto_inversion_id':fields.many2one('stone_erp_idu.punto_inversion','Punto de Inversion'),
                
    }
stone_erp_idu_centro_costo()


class stone_erp_punto_inversion (osv.osv):
    _name = "stone_erp_idu.punto_inversion"
    _columns = {
        'codigo':fields.integer('Codigo'),
        'name':fields.char('Nombre',size=1025)
    }
stone_erp_punto_inversion()


