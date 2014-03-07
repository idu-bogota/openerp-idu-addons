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
#
#
#
#    Autor Andres Ignacio Báez Alba
#
#
#########t#####################################################################
from osv import fields, osv
import cStringIO as StringIO
import xlwt
from base64 import encodestring

class plan_contratacion_idu_wizard_reporte(osv.osv_memory):
    """
    """
    _name="plan_contratacion_idu.wizard.reporte"
    _description="Crea un reporte con el plan de contratacion"
    _columns={
              'plan_contratacion':fields.many2one('plan_contratacion_idu.plan','Plan de Contratacion',required=True),
              'dependencia':fields.many2one('hr.department','Dependencia'),
              'data':fields.binary('Archivo',readonly=True,filters="xls"),
              'filename':fields.char('Nombre de Archivo',size=40,readonly=True)
    }
    _defaults = {
              'filename': 'report.xls',
    }
    
    def crear_reporte(self,cr,uid,ids,context):
        """
        Genera el reporte de excel
        Si area es vacio, retorna todo el plan de contratacion seleccionado
        """
        ##############################################################################
        # TO DO:
        # Se debería poder crear un wizard o etl o lo que sea para que cualquier módulo se pueda
        # exportar a excel componentizando este fragmento de codigo
        ##############################################################################
        wizard_obj=self.browse(cr,uid,ids[0],context)
        plan_contratacion_idu_item_obj = self.pool.get('plan_contratacion_idu.item')
        user = self.pool.get('res.users').browse(cr,uid,uid,context=context)
        is_admin = False
        is_user = False
        #1. verificar si es un administrador o es un usuario razo
        for grp in user.groups_id:
            grp_id=grp.get_external_id()[grp.id]
            if ((grp_id == 'plan_contratacion_idu.group_plan_contratacion_idu_manager') or (grp_id == 'plan_contratacion_idu.group_plan_contratacion_idu_analyst')):
                is_admin = True
            elif (grp_id == 'plan_contratacion_idu.group_plan_contratacion_idu_user'):
                is_user = True
        headers = ['Codigo UNPSC',#0
                   'LLAVE',#1
                   'ESTADO',#2
                   'PROCESO',#3
                   'COD PROY INV',#4
                   'NOMBRE PROY INVERSION',#5
                   'COD_PROYECTO_PRIORITARIO',#6
                   'CODIGO_PROYECTO',#7
                   'NOMBRE_PROYECTO',#8
                   'CENTRO_COSTO',#9
                   'CODIGO_PUNTO_INVERSION',#10
                   'NOMBRE_PUNTO_INVERSION',#11
                   'DEPENDENCIA',#12
                   'PRESUPUESTO',#13
                   'CODIGO FUENTE FINANCIACION',#16
                   'FUENTE_FINANCIACION',#17
                   'CODIGO FUENTE FINANCIACION SEGPOAI',#18
                   'FUENTE FINANCIACION SEGPOAI',#19
                   'FUENTE SDH',#20
                   'PLAZO EJECUCION ESTIMADO SEGUN DTP',#21
                   'UNIDAD METAS FISICAS',#22
                   'CANTIDAD METAS FISICAS',#23
                   'CODIGO LOC',#24
                   'LOCALIDAD',#25
                   'FECHA RADICACION DTPS SEGUN DTD',#26
                   'FECHA PROGRAMADA CRP ESTIMACION DTD',#27
                   'CRP',#28
                   'TIPO DE PROCESO DE SELECCION',#29
                   'CODIGO FASE DE INTERVENCION',#30
                   'FASE DE INTERVENCION',#31
                   'CUPO',#32
                   'NO CONTRATO',#33
                   'OBSERVACIONES DE MODIFICACIONES',#34
                   'ENERO',#35
                   'FEBRERO',#36
                   'MARZO',#37
                   'ABRIL',#38
                   'MAYO',#39
                   'JUNIO',#40
                   'JULIO',#41
                   'AGOSTO',#42
                   'SEPTIEMBRE',#43,
                   'OCTUBRE',#44
                   'NOVIEMBRE',#45
                   'DICIEMBRE',#46
                   'TOTAL',#47
                   'REZAGO',#48
                   'OBSERVACIONES',#49
                   'PPTO',#50
                   ]
        xlsfile=StringIO.StringIO()
        wb = xlwt.Workbook()
        
        ws = wb.add_sheet('Plan Contratacion')
        column_index = 0
        #Se ponen los títulos
        while (column_index < headers.__len__()):
            row_index=1
            ws.write(row_index,column_index,headers[column_index])
            column_index = column_index+1
        #Llenado del excel
        id_items = False
        pl_contratacion_ids = wizard_obj.plan_contratacion.id
        if (is_admin):
            #Si es admin trae todos los items de un plan de contratacion 
            #Esa logica no es necesaria si se definen los grupos de dominio en el script de seguridad, mientras para probar deje así
            id_items = plan_contratacion_idu_item_obj.search(cr,uid,[('plan_id','=',pl_contratacion_ids)])
        elif(is_user):
            #Si es user limita la busqueda a los departamentos del area ('Esto haría innecesario el combo del wizard, ojo -> mejorar' 
            #
            department_ids = self.pool.get('res.users').browse(cr, uid, uid, context=context).department_ids
            if department_ids:
                id_items = plan_contratacion_idu_item_obj.search(cr,uid,[('plan_id','=',pl_contratacion_ids),('dependencia_id','=',department_ids)])
        if (id_items):
            items_plan = plan_contratacion_idu_item_obj.browse(cr,uid,id_items,context)
            row_index = 2
            for item in items_plan:
                ws.write(row_index,0,item.codigo_unspsc)
                ws.write(row_index,2,item.state)
                ws.write(row_index,3,item.tipo_proceso_id.name)
                # proyecto_inversion
                # proyecto prioritario
                # codigo proyecto prioritario
                ws.write(row_index,7,item.cod_proyecto_idu)
                ws.write(row_index,8,item.nombre_proyecto_idu)
                ws.write(row_index,9,item.centro_costo)
                ws.write(row_index,10,item.cod_punto_inversion)
                ws.write(row_index,11,item.nombre_punto_inversion)
                ws.write(row_index,12,item.dependencia_id.name)
                ws.write(row_index,13,item.presupuesto)
                ws.write(row_index,14,item.fuente_id.codigo_fuente)
                ws.write(row_index,15,item.fuente_id.name)
                ws.write(row_index,16,item.fuente_id.codigo_fuente_sdh)
                ws.write(row_index,17,item.fuente_id.nombre_fuente_sdh)
                ws.write(row_index,18,item.fuente_id.nombre_detalle_fuente_sdh)
                if (item.a_monto_agotable):
                    ws.write(row_index,19,"A monto agotable")
                else:
                    ws.write(row_index,19,item.plazo_de_ejecucion)

                ws.write(row_index,28,item.cod_fase_intervencion)
                ws.write(row_index,29,item.nombre_fase_intervencion)
                
                
                for pago in item.plan_pagos_item_ids:
                    ws.write(row_index,32+pago.mes,pago.valor)
                
                row_index = row_index+1
        wb.save(xlsfile)
        out = encodestring(xlsfile.getvalue())
        return out

    def generar(self,cr,uid,ids,context=None):
        file_data = self.crear_reporte(cr,uid,ids,context)
        self.write(cr,uid,ids[0],{'data':file_data},context)
        view_ids = self.pool.get('ir.ui.view').search(cr,uid,[('model','=','plan_contratacion_idu.wizard.reporte'),\
                                                              ('name','=','Descargar Plan Contratacion a Excel')])
        context["current_ids"]=ids[0]
        return {
                'view_type':'form',
                'view_mode':'form',
                'res_model':'plan_contratacion_idu.wizard.reporte',
                'target':'new',
                'type':'ir.actions.act_window',
                'view_id':view_ids[0]
        }
    
    def default_get(self,cr,uid,fields,context=None):
        res = super(plan_contratacion_idu_wizard_reporte,self).default_get(cr,uid,fields,context=context)
        if 'active_id' in context:
            if 'data' in fields:
                wizard = self.browse(cr, uid, context['active_id'])
                res['data']=wizard.data
                res['filename']=wizard.filename
        return res
    
    
plan_contratacion_idu_wizard_reporte()
    
    
    
    
