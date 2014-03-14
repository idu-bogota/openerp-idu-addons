# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2014 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
from openerp_tools import openerp_server_proxy
from xlrd import open_workbook

vigencia = "20132014"
openerp_server = "I1608"
pwd = "sigidu"
user = "admin"
dbname="plan-contratacion"
port ="8069"
path_excel = "/home/cabaezal1/proyectos/pc2014.xls"
index_hoja = 9
index_header = 1


def cargar_fichero_excel(_path_excel,_index_hoja,_row_index_header):
    """
    Crea un diccionario a partir del fichero excel de la forma
    [{'header_col1':value_col1_row1,'header_col2',value_col2_row1},{header_col1':value_col1_row2,'header_col2',value_col2__row2}]
    
    """ 
    wb = open_workbook(_path_excel)
    hoja_datos = wb.sheet_by_index(_index_hoja)
    print hoja_datos.name
    col_index = 0
    headers=[]
    
    while (col_index < hoja_datos.ncols):
        colname = hoja_datos.cell(_row_index_header,col_index).value
        headers.append(colname)
        col_index = col_index+1
    row_index = _row_index_header+1
    #print headers
    res = []
    res ['Fila_excel']=row_index+1
    while (row_index < hoja_datos.nrows):
        dic_row = {}
        col_index = 0
        while (col_index < hoja_datos.ncols):
            cell_val = hoja_datos.cell(row_index,col_index).value
            col_header = headers[col_index]
            dic_row[col_header]=cell_val
            col_index = col_index+1
        res.append(dic_row)
        row_index = row_index+1
    return res 




def exportar_datos_openerp(_plan_contratacion,_openerp_server,_port, _dbname,_user,_password,_vigencia):
    openerp = openerp_server_proxy.openerp_proxy(_openerp_server,_port,_user,_password,_dbname)
    #En cada registro se deben analizar las diferentes dependencias, crear los diccionarios y los key para que se puedan determinar los datos.
    
    #1. Clasificador- Se consulta el clasificador de acuerdo al codigo de proyecto
    #2. Id con codigo de localidad
    for item in _plan_contratacion:
        vals={}
        #Plan Contratacion
        vals['state']='version_inicial'
        plan_ids = openerp.search('plan_contratacion_idu.plan',[('vigencia','=',_vigencia)])
        if (plan_ids.__len__()==0):
            raise Exception("No se encuentra definina la vigencia del plan de contratacion, revisar excel fila " + str(item['Fila_excel']))
        vals["plan_id"]=plan_ids[0]
        #El clasificador de proyecto se obtiene del proyecto prioritario 
        #clasificacion_id = openerp.search('plan_contratacion_idu.clasificador_proyectos',[('codigo','=',proyecto_prioritario)])
        proyecto_inversion = "%i" % float(item['CÓD PROY INV '])
        proyecto_prioritario = "%i" % float(item['CÓD PROY PRIOR'])
        #Codigo UNPSC
        vals['codigo_unspsc']=item['CODIGO UNSPSC']
        clasificacion_ids = openerp.search('plan_contratacion_idu.clasificador_proyectos',[('codigo','=', proyecto_prioritario)])
        if clasificacion_ids.__len__()==0:
            raise Exception("No se encuentra el clasificador de proyectos parametrizado, por favor cargue el arbol de proyectos primero revisar filla" +str(item['Fila_excel']))
        vals['clasificacion_id'] = clasificacion_ids[0]
        #Dependencias
        dependencia = item['DEPENDENCIAS']
        dependencia_ids = openerp.search('hr.department',[('name','=like','%s%%' % dependencia)])
        if (dependencia_ids.__len__()==0):
            raise Exception("No se encuentra la dependencia "+dependencia+", item en fila "+str(item['Fila_excel']))
        vals['dependencia_id']=dependencia_ids[0]
        #Fuente de Financiacion
        codigo_fuente_fin = '%i' % float(item['CÓDIGO FUENTE DE FINANCIACIÓN'])
        codigo_fuente_ids = openerp.search('plan_contratacion_idu.fuente',[('codigo_fuente','=','%s' % codigo_fuente_fin)])
        if (codigo_fuente_ids.__len__()==0):
            raise Exception('La fuente de financiacion definida no se encuentra parametrizada en openerp, verificar excel fila '+str(item['Fila_excel']))
        vals['fuente_id']=codigo_fuente_ids[0]
        tipo_proceso = item['PROCESO']
        tipo_proceso_ids = openerp.search('plan_contratacion_idu.plan_tipo_proceso',[('name','=like','%s%%' % tipo_proceso)])
        if (tipo_proceso_ids.__len__()==0):
            raise Exception('El tipo de proceso no se encuentra parametrizado, revisar excel fila '+str(item['Fila_excel']))
        vals['tipo_proceso_id']=tipo_proceso_ids[0]
        tipo_proceso_seleccion = item['TIPO DE PROCESO DE SELECCIÓN']
        tipo_proceso_seleccion_ids = openerp.search('plan_contratacion_idu.plan_tipo_proceso_seleccion',[('name','=like','%s%%' % tipo_proceso_seleccion.rstrip())])
        if (tipo_proceso_seleccion_ids.__len__()==0):
            raise Exception('El tipo de proceso de seleccion no se encuentra parametrizado revisar excel fila '+str(item['Fila_excel']))
        vals['tipo_proceso_seleccion_id']=tipo_proceso_seleccion_ids[0]
        



        #Verificar si proyecto prioritario y proyecto de inversion en el clasificador
    print "Inicio de exportacion de datos a openerp"


#plan_values = cargar_fichero_excel(path_excel,index_hoja,index_header)

plan_prueba=[{'':'','FECHA PROGRAMADA CRP - ESTIMACIÓN DTD':'41760.0','Fila_excel':3,
              'VALIDACIÓN':'22057000.0','PPTO':'22057000.0','Fuente de Financiacion':'574.0','Grupo Valora':'2.0',
              'REZAGO':'10943001.0','NOMBRE PROYECTO INVERSIÓN':'Fortalecimiento Institucional para el mejoramiento de la gestión del IDU',
              'DEPENDENCIAS':'OAC','ABRIL':'','Nombre Sistema':'FORTALECIMIENTO INSTITUCIONAL','CENTRO DE COSTO':'30607.0','MAYO':'',
              'Nombre Pto Inversión':'PROGRAMA DE COMUNICACIONES','FECHA RADICACIÓN EN DTPS SEGÚN DTD':'41730.0',
              'llave':'232-115-30607-100-574-10','CUPO ':'','PROCESO':'Contrato Nuevo','Número Línea':'1.0','UNIDAD METAS FISICAS':'',
              'TIPO DE PROCESO DE SELECCIÓN':'Selección abreviada mínima cuantía ','Plan de Desarrollo':'232.0','CÓD PROY PRIOR':'238.0',
              'AGOSTO':'1833333.0','Nombre Fuente de Financiacion':'RB VAL  AC 523/13','TOTAL 2014':'11113999.0','CÓD PROY INV ':'232.0',
              'Nombre Componente':'PRESTACION DE SERVICIOS','PLAZO DE EJECUCIÓN - ESTIMADO SEGÚN DTP':'12 meses','CÓDIGO LOC':'66.0',
              'MARZO':'','Nombre Proyecto I.D.U':'PROGRAMA DE COMUNICACIONES','Rubro':'3.31140331023e+15','CODIGO UNSPSC':'83121704.0',
              'Dependencia Nueva':'565.0','FUENTE DE FINANCIACI+ON SEGPOAI':'RB VAL  AC 523/13','ENERO':'','CÓDIGO FUENTE DE FINANCIACIÓN':'574.0',
              'NOMBRE PROYECTO':'PROGRAMA DE COMUNICACIONES','OCTUBRE':'1833333.0','JULIO':'1947334.0','Código Sistema':'3.0',
              'Nombre Zona Influencia Val.':'ZONA 2','CÓDIGO FUENTE DE FINANCIACIÓN SEGPOAI':'574.0','NOMBRE DEL PUNTO DE INVERSIÓN':'PROGRAMA DE COMUNICACIONES',
              'Nombre Plan de Desarrollo':'BOGOTA HUMANA AL SERVICIO DE LA CIUDADANÍA','SEPTIEMBRE':'1833333.0','Nombre Grupo Valora':'GRUPO 2',
              'CRP':'may','PRESUPUESTO ':'22057000.0','Proyecto I.D.U':'115.0','OBSERVACIONES':'','FEBRERO':'','CÓDIGO PUNTO DE INVERSIÓN':'100.0',
              'NOMBRE PROYECTO PRIORITARIO':'Bogotá Humana al servicio de la ciudadanía','NOVIEMBRE':'1833333.0','CÓDIGO FASE DE INTEVENCIÓN':'10.0',
              'FUENTE SDH':'Recursos administrados','OBSERVACIONES DE MODIFICACIONES ':'','Nombre Fase Val':'FASE 2','Presupuesto Definitivo':'413057000.0',
              'Nombre SubSistema':'APOYO TECNICO Y LOGISTICO','Fase Val':'2.0','CANTIDAD METAS FISICAS ':'','Nombre Dependencia Anterior':'SIN DEPENDENCIA ANTERIOR',
              'FASE DE INTEVENCIÓN':'Bienes y servicios ','MODIFICACION':'Nuevo','Código Componente':'26.0','LOCALIDAD':'Entidad','Dependencia Anterior':'99.0',
              'Nombre Centro de Costo':'PROGRAMA DE COMUNICACIONES F2','CDP´S':'141000000.0','Punto Inversión':'100.0','N° CONTRATO':'',
              'Código Centro de Costo':'30607.0','LLAVE':'232-115-30607-100-574-10','Zona Influencia Val.':'2.0',
              'OBJETO CONTRACTUAL - ESTIMACIÓN DTD':'Se requiere contratar el servicio de monitoreo de la información que se publica en los diferentes medios de comunicación, respecto al AC.523/13 y en general del sector, con el fin de hacer el seguimiento continuo para la retroalimentación que genera unidad de criterio para el manejo de la comunicación del IDU.','JUNIO':'','Nombre Fase de Intervención':'BIENES Y SERVICIOS','Disponibilidad':'272057000.0','Nombre Dependencia Nueva':'DIRECCION TEC. DE APOYO A VALORIZACION',
              'Fase de Intervención':'10.0','Código SubSistema':'5.0','Reserva':'0.0','CODIGO PROYECTO ':'115.0','Ejecutado':'0.0',
              'FUENTE DE FINACIACION':'RB VL AC.523/13 ','SEGPOAI':'RB VAL  AC 523/13','DICIEMBRE':'1833333.0'}]

#item1=plan_values[0]
# x="[{"
# for val in item1:
#     x=x+"'"+val+"':'"+str(item1[val])+"',"
# x = x + "}]"
# print x

exportar_datos_openerp(plan_prueba,openerp_server,port,dbname,user,pwd,vigencia)
