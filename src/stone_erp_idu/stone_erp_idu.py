# -*- encoding: utf-8 -*-
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
        'name':fields.char('Nombre', size=255, readonly=True, select=True),
        'proyecto_idu_id':fields.many2one('stone_erp_idu.proyecto_idu','Proyecto',readonly=True),
        'punto_inversion_id':fields.many2one('stone_erp_idu.punto_inversion','Punto de Inversion',readonly=True),
        'punto_inversion_nombre':fields.related('punto_inversion_id','name',type="char",relation="stone_erp_idu.punto_inversion",string="Nombre Proyecto IDU", store=False,readonly=True),
        'punto_inversion_codigo':fields.related('punto_inversion_id','codigo',type="integer",relation="stone_erp_idu.punto_inversion",string="Codigo Proyecto IDU", store=False,readonly=True),
        'proyecto_idu_nombre':fields.related('proyecto_idu_id','name',type="char",relation="stone_erp_idu.proyecto_idu",string="Nombre Proyecto IDU", store=False,readonly=True),
        'proyecto_idu_codigo':fields.related('proyecto_idu_id','codigo',type="integer",relation="stone_erp_idu.proyecto_idu",string="Nombre Proyecto IDU", store=False,readonly=True),
        
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
        return True

    def completar_centro_costo(self,cr,uid,vals,context=None):
        wsdl = self.pool.get('ir.config_parameter').get_param(cr,uid,'stone_idu.webservice.wsdl',default=False,context=context)
        try:
            det_cc = stone_client_ws.completar_datos_centro_costo(wsdl, vals['codigo'])
            #Actualizar proyecto IDU Relacionado
            proyecto_idu_obj = self.pool.get('stone_erp_idu.proyecto_idu')
            ids_proy_idu = proyecto_idu_obj.search(cr,uid,[('codigo','=',det_cc['proyecto_idu_id'])],context=context)
            vals_proyecto_idu = {'codigo':det_cc['proyecto_idu_id'],'name':det_cc['proyecto_idu']}
            id_proy_idu = 0
            if (ids_proy_idu.__len__()==0):
                #insertar
                id_proy_idu = proyecto_idu_obj.create(cr,uid,vals_proyecto_idu,context)
            else:
                #actualizar
                id_proy_idu=ids_proy_idu[0]
                proyecto_idu_obj.write(cr,uid,id_proy_idu,vals_proyecto_idu,context)
            #Actualizar Punto de Inversion relacionado
            punto_inversion_obj=self.pool.get('stone_erp_idu.punto_inversion')
            ids_punto_inversion=punto_inversion_obj.search(cr,uid,[('codigo','=',det_cc['punto_inversion_id'])],context=context) 
            id_punto_inv = 0
            vals_punto_inversion = {'codigo':det_cc['punto_inversion_id'],'name':det_cc['punto_inversion']}
            if (ids_punto_inversion.__len__()==0):
                #insertar nuevo valor
                id_punto_inv = punto_inversion_obj.create(cr,uid,vals_punto_inversion,context)
            else : 
                #actualizar nuevo valor
                id_punto_inv = ids_punto_inversion[0]
                punto_inversion_obj.write(cr,uid,id_punto_inv,vals_punto_inversion,context)
            vals['proyecto_idu_id']=id_proy_idu
            vals['punto_inversion_id']=id_punto_inv
        except Exception as e:
            raise osv.except_osv('Error',str(e))
        return vals

stone_erp_idu_centro_costo()

class stone_erp_idu_punto_inversion (osv.osv):
    _name = "stone_erp_idu.punto_inversion"
    _rec_name="codigo"
    _columns = {
        'codigo':fields.integer('Codigo'),
        'name':fields.char('Nombre',size=1025)
    }
    
    _sql_constraints=[
        ('unique_punto_inversion_codigo','unique(codigo)','El punto de Inversion que intenta ingresar, ya se encuentra registrado'),
    ]
stone_erp_idu_punto_inversion()

class stone_erp_proyecto_idu (osv.osv):
    _name = "stone_erp_idu.proyecto_idu"
    _rec_name="codigo"
    _columns = {
        'codigo':fields.integer('Codigo'),
        'name':fields.char('Nombre',size=1025)
    }
    
    _sql_constraints=[
        ('unique_proyecto_idu_codigo','unique(codigo)','El Proyecto IDU que intenta ingresar, ya se encuentra registrado'),
    ]
stone_erp_proyecto_idu()
