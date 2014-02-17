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
    _rec_name="codigo"
    _columns = {
        'codigo': fields.integer('Codigo', required=True, select=True),
        'name':fields.char('Nombre', size=255, required=True, select=True),
        #'proyecto_id':fields.many2one('plan_contratacion_idu.clasificador_proyectos','Proyecto'),
        'punto_inversion_id':fields.many2one('stone_erp_idu.punto_inversion','Punto de Inversion'),
    }
    _sql_constraints=[
        ('unique_codigu','unique(codigo)','El centro de costo qu8e intenta ingresar, ya se encuentra registrado'),
    ]

    def actualizar_centros_costo(self,cr,uid,context = None):
        wsdl = self.pool.get('ir.config_parameter').get_param(cr,uid,'stone_idu.webservice.wsdl',default=False,context=context)
        centro_costo_obj = self.pool.get('stone_erp_idu.centro_costo')
        c_costo_dict = stone_client_ws.obtener_centros_costo(wsdl)
        for c_costo in c_costo_dict:
            ids_centro_costo = self.pool.get('stone_erp_idu.centro_costo').search(cr,uid,[('codigo','=',c_costo)],context=context)
            vals = {'codigo':c_costo,'name':c_costo_dict[c_costo]}
            if (ids_centro_costo.__len__() == 0):
                #insertar
                centro_costo_obj.create(cr,uid,vals,context=None)
            else :
                #actualizar#
                centro_costo_obj.write(cr,uid,ids_centro_costo,vals)
        return {}
        
    
    
stone_erp_idu_centro_costo()


class stone_erp_punto_inversion (osv.osv):
    _name = "stone_erp_idu.punto_inversion"
    _columns = {
        'codigo':fields.integer('Codigo'),
        'name':fields.char('Nombre',size=1025)
    }
stone_erp_punto_inversion()


