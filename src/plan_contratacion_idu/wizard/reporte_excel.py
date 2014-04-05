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
########t#####################################################################
from osv import fields, osv
import cStringIO as StringIO
import xlwt
from base64 import encodestring

class plan_contratacion_idu_wizard_reporte(osv.osv_memory):

    def get_headers(self):
        "Define los encabezados del fichero de excel"
        headers = ['CODIGO UNPSC',
                   'LLAVE',
                   'ESTADO',
                   'PROCESO',
                   'COD PROY INV',
                   'NOMBRE PROY INVERSION',
                   'COD PROYECTO PRIORITARIO',
                   'NOMBRE PROYECTO PRIORITARIO',
                   'CODIGO PROYECTO',
                   'NOMBRE PROYECTO',
                   'CENTRO COSTO',
                   'CODIGO PUNTO INVERSION',
                   'NOMBRE PUNTO INVERSION',
                   'DEPENDENCIA',#12
                   'PRESUPUESTO',#13
                   'CODIGO FUENTE FINANCIACION',#16
                   'FUENTE FINANCIACION',#17
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
                   'No CONTRATO',#33
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
                   ]
        return headers

    _name="plan_contratacion_idu.wizard.reporte"
    _description="Crea un reporte con el plan de contratacion"
    _columns={
              'plan_contratacion':fields.many2one('plan_contratacion_idu.plan','Plan de Contratacion',required=True),
              'data':fields.binary('Archivo',readonly=True,filters="xls"),
              #'filename':fields.char('Nombre de Archivo',size=40,readonly=True),
              'filename':fields.char('Nombre de Archivo', size=255)
    }

    _defaults = {
                 'filename': 'report.xls',
    }


    def _format_item (self,item):
        res = "" if (type(item) == bool and item == False) else str(item).decode('utf8')#Cuando vienen tildes entonces para que no afecte al excel
        return res


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
        wizard_obj=self.browse(cr, uid, ids[0], context)
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
        
        xlsfile=StringIO.StringIO()
        wb = xlwt.Workbook()
        header_style = xlwt.easyxf('pattern:pattern solid,fore_colour blue;')
        date_style = xlwt.XFStyle()
        date_style.num_format_str="DD-MM-YYYY"
        headers = self.get_headers()
        ws = wb.add_sheet('Plan Contratacion')
        column_index = 0
        #Se ponen los títulos
        while (column_index < headers.__len__()):
            row_index=1
            ws.write(row_index,column_index,headers[column_index],header_style)
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
                ws.write(row_index,headers.index("CODIGO UNPSC"),self._format_item(item.codigo_unspsc))
                
                estado = ""
             
                for val in item._model._columns["state"].selection:
                    if val[0] == item.state :
                        estado = val[1]

                ws.write(row_index,headers.index("ESTADO"),self._format_item(estado))
                ws.write(row_index,headers.index("PROCESO"),self._format_item(item.tipo_proceso_id.name))
                # proyecto_inversion
                ws.write(row_index,headers.index('LLAVE'),self._format_item(str(item.clasificacion_id.parent_id.codigo) + "-" +
                                                                    str(item.cod_proyecto_idu) + "-" +
                                                                    str(item.centro_costo) + "-" +
                                                                    str(item.cod_punto_inversion) + "-" +
                                                                    str(item.fuente_id.codigo_fuente) + "-" +
                                                                    str(item.cod_fase_intervencion))
                )
                ws.write(row_index,headers.index('COD PROYECTO PRIORITARIO'),self._format_item(item.clasificacion_id.codigo))
                ws.write(row_index,headers.index('NOMBRE PROYECTO PRIORITARIO'),self._format_item(item.clasificacion_id.name))
                ws.write(row_index,headers.index('COD PROY INV'),self._format_item(item.clasificacion_id.parent_id.codigo))
                ws.write(row_index,headers.index('NOMBRE PROY INVERSION'),self._format_item(item.clasificacion_id.parent_id.name))
                ws.write(row_index,headers.index('CODIGO PROYECTO'),self._format_item(item.cod_proyecto_idu))
                ws.write(row_index,headers.index('NOMBRE PROYECTO'),self._format_item(item.nombre_proyecto_idu))
                ws.write(row_index,headers.index('CENTRO COSTO'),self._format_item(item.centro_costo))
                ws.write(row_index,headers.index('CODIGO PUNTO INVERSION'),self._format_item(item.cod_punto_inversion))
                ws.write(row_index,headers.index('NOMBRE PUNTO INVERSION'),self._format_item(item.nombre_punto_inversion))
                ws.write(row_index,headers.index('DEPENDENCIA'),self._format_item(item.dependencia_id.name))
                ws.write(row_index,headers.index('PRESUPUESTO'),self._format_item(item.presupuesto))
                ws.write(row_index,headers.index('CODIGO FUENTE FINANCIACION'),self._format_item(item.fuente_id.codigo_fuente))
                ws.write(row_index,headers.index('FUENTE FINANCIACION'),self._format_item(item.fuente_id.name))
                ws.write(row_index,headers.index('CODIGO FUENTE FINANCIACION SEGPOAI'),self._format_item(item.fuente_id.codigo_fuente_sdh))
                ws.write(row_index,headers.index('FUENTE FINANCIACION SEGPOAI'),self._format_item(item.fuente_id.nombre_fuente_sdh))
                ws.write(row_index,headers.index('FUENTE SDH'),self._format_item(item.fuente_id.nombre_detalle_fuente_sdh))
                if (item.a_monto_agotable):
                    ws.write(row_index,headers.index('PLAZO EJECUCION ESTIMADO SEGUN DTP'),"A monto agotable")
                else:
                    ws.write(row_index,headers.index('PLAZO EJECUCION ESTIMADO SEGUN DTP'),self._format_item(item.plazo_de_ejecucion))

                ws.write(row_index,headers.index('CODIGO FASE DE INTERVENCION'),self._format_item(item.cod_fase_intervencion))
                ws.write(row_index,headers.index('FASE DE INTERVENCION'),self._format_item(item.nombre_fase_intervencion))
                #Meta física 
                if not (item.no_aplica_unidad_mf):
                    ws.write(row_index,headers.index('UNIDAD METAS FISICAS'),self._format_item(item.unidad_meta_fisica_id.name))
                    ws.write(row_index,headers.index('CANTIDAD METAS FISICAS'),self._format_item(item.cantidad_meta_fisica))
                #Localidad 
                localizacion = ""
                for val in item._model._columns["localizacion"].selection:
                    if val[0] == item.localizacion :
                        localizacion = val[1]
                #Todo cuando se actualice el codigo quitar la comparacion con entidad o metropolitana
                if ((item.localizacion=='entidad' or item.localizacion == 'metropolitana') or (item.localizacion=='66' or item.localizacion == '77')):
                    #Si localizacion localidad = entidad o metropolitana, entonces la celda localidad = entidad o metropolitana
                    ws.write(row_index,headers.index('CODIGO LOC'),self._format_item(item.localizacion))
                    ws.write(row_index,headers.index('LOCALIDAD'),self._format_item(localizacion))
                elif (item.localizacion=="localidad"):
                    #Si localizacion = localidad, listar cada una de las localidades.
                    str_loc = ""
                    cod_loc = ""
                    for localidad in item.localidad_ids:
                        cod_loc = cod_loc + str(localidad.code) + ","
                        str_loc = str_loc + localidad.name + ","
                    ws.write(row_index,headers.index('CODIGO LOC'),cod_loc)
                    ws.write(row_index,headers.index('LOCALIDAD'),str_loc)
                #Fecha de Radicacion en Segun DTS, Fecha CRP, Tipo proceso seleccion
                ws.write(row_index,headers.index('FECHA RADICACION DTPS SEGUN DTD'),self._format_item(item.fecha_programada_radicacion),date_style)
                ws.write(row_index,headers.index('FECHA PROGRAMADA CRP ESTIMACION DTD'),self._format_item(item.fecha_programada_crp),date_style)
                ws.write(row_index,headers.index('CRP'),self._format_item(item.numero_crp))
                ws.write(row_index,headers.index('TIPO DE PROCESO DE SELECCION'),self._format_item(item.tipo_proceso_seleccion_id.name))
                ws.write(row_index,headers.index('No CONTRATO'),self._format_item(item.numero_contrato))
                for pago in item.plan_pagos_item_ids:
                    ws.write(row_index,headers.index('ENERO')+(pago.mes-1),self._format_item(pago.valor))
                ws.write(row_index,headers.index('TOTAL'),self._format_item(item.total_pagos_programados))
                ws.write(row_index,headers.index('REZAGO'),self._format_item(item.presupuesto_rezago))
                row_index = row_index+1
        wb.save(xlsfile)
        out = encodestring(xlsfile.getvalue())
        return out

    def generar(self,cr,uid,ids,context=None):
        wizard_obj = self.browse(cr, uid, ids[0], context)
        file_data = self.crear_reporte(cr, uid, ids, context)
        filename = "{0}_version_{1}.xls".format(wizard_obj.plan_contratacion.vigencia, wizard_obj.plan_contratacion.version)
        self.write(cr, uid, ids[0], {'data':file_data, 'filename': filename}, context)
        view_ids = self.pool.get('ir.ui.view').search(cr,uid,[('model','=','plan_contratacion_idu.wizard.reporte'),
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

