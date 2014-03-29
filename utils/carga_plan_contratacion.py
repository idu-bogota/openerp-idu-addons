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
from xlrd import open_workbook, xldate_as_tuple, XL_CELL_DATE
from datetime import date

vigencia = "2014"
openerp_server = "A-1502"
pwd = "admin"
user = "admin"
dbname="plan_contratacion"
port ="8069"
path_excel = "/home/clreyesb1/Escritorio/datos_plan/pc2014.xls"
index_hoja = 9
index_header = 1

print "SCRIPT DE CARGA DE DATOS A OPENERP PLAN CONTRATACION"
print "ANDRES DE EJECUTAR SCRIPT ASEGURESE DE QUE EL EXCEL ESTE EN FORMATO EXCEL 2003-2007, ya que la libreria"
print "XLRD solo soporta hasta Excel 2007"

print "openerp server :" + openerp_server
print "port :"+port
print "excel path :"+path_excel



def cargar_fichero_excel(_path_excel,_index_hoja,_row_index_header):
    """
    Crea un diccionario a partir del fichero excel de la forma
    [{'header_col1':value_col1_row1,'header_col2',value_col2_row1},{header_col1':value_col1_row2,'header_col2',value_col2__row2}]
    
    """
    print "Leyendo fichero excel" 
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
    
    while (row_index < hoja_datos.nrows):
        dic_row = {}
        dic_row ['Fila_excel']=row_index+1
        col_index = 0
        while (col_index < hoja_datos.ncols):
            celda = hoja_datos.cell(row_index,col_index)
            col_header = headers[col_index].encode('utf8')
            #Verificar que los datos de entrada tipo date time funcionen
            if (celda.ctype == XL_CELL_DATE):
                date_value = xldate_as_tuple(celda.value,wb.datemode)
                dic_row[col_header]=str(date_value)
            else :
                dic_row[col_header]=celda.value
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

        #Codigo UNPSC
        vals['codigo_unspsc']=str("%i" % float(item['CODIGO UNSPSC']))
        #El clasificador de proyecto se obtiene del proyecto prioritario 
        #clasificacion_id = openerp.search('plan_contratacion_idu.clasificador_proyectos',[('codigo','=',proyecto_prioritario)])
        
        proyecto_inversion = "%i" % float(item['CÓD PROY INV '])
        proyecto_prioritario = "%i" % float(item['CÓD PROY PRIOR'])
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
        tipo_proceso_ids = openerp.search('plan_contratacion_idu.plan_tipo_proceso',[('name','=ilike','%s%%' % tipo_proceso)])
        if (tipo_proceso_ids.__len__()==0):
            raise Exception('El tipo de proceso no se encuentra parametrizado, revisar excel fila '+str(item['Fila_excel']))
        vals['tipo_proceso_id']=tipo_proceso_ids[0]
        tipo_proceso_seleccion = item['TIPO DE PROCESO DE SELECCIÓN']
        tipo_proceso_seleccion_ids = openerp.search('plan_contratacion_idu.plan_tipo_proceso_seleccion',[('name','ilike','%s%%' % tipo_proceso_seleccion.rstrip())])
        if (tipo_proceso_seleccion_ids.__len__()==0):
            raise Exception('El tipo de proceso de seleccion no se encuentra parametrizado revisar excel fila '+str(item['Fila_excel']))
        vals['tipo_proceso_seleccion_id']=tipo_proceso_seleccion_ids[0]
        #presupuesto
        vals['presupuesto']=float(item['PRESUPUESTO '])
        #localizacion
        localizacion=str(item['CÓDIGO LOC'])
        _localizacion=False
        try:
            _localizacion = str("%i" % float(localizacion))
        except:
            pass
        if (str(_localizacion) =="66" or _localizacion == "77"):
                vals['localizacion']=_localizacion
        else:
            vals['localizacion']='localidad'
            localidades=localizacion.replace(" ", "").replace("y",",").split(",")
            localidad_ids = []
            for localidad in localidades:
                if not (localidad == "NA"):
                    i_localidad = str("%i" % float(localidad))
                    ids_localidad = openerp.search('base_map.district',[('code','=',i_localidad)])
                    if (ids_localidad.__len__()==0):
                        raise Exception ("La localidad no esta definida, revisar fila "+str(item['Fila_excel']))
                    localidad_ids.append(ids_localidad[0])
            vals['localidad_ids']=[[6,False,localidad_ids]]
        vals['description']=item['OBJETO CONTRACTUAL - ESTIMACIÓN DTD']
        #Plazo de ejecucion o monto agotable
        plazo_ejecucion = item['PLAZO DE EJECUCIÓN - ESTIMADO SEGÚN DTP']
        if (plazo_ejecucion == "N/A" or plazo_ejecucion==""):
            vals["a_monto_agotable"]=True
            #vals["no_aplica_unidad_mf"]=True
        elif(plazo_ejecucion == "A monto agotable"):
            vals["a_monto_agotable"]=True
        else:
            _plazo_ejecucion = plazo_ejecucion.split(" ")[0]
            vals["plazo_de_ejecucion"]=int(_plazo_ejecucion)
        unidad_metas_f = item['UNIDAD METAS FISICAS']
        if (unidad_metas_f == "N/A" or unidad_metas_f==""):
            vals["no_aplica_unidad_mf"]=True
        else:
            vals["no_aplica_unidad_mf"]=False
            cod_unidad_mf_ids = openerp.search('product.uom',[('name','ilike','%s%%' % unidad_metas_f)])
            if (cod_unidad_mf_ids.__len__()==0):
                umf = {'name':unidad_metas_f,'active':True,'rounding':1.0,'factor':1.0,'category_id':1,'uom_type':'reference'}
                id_unidad_mf = openerp.create('product.uom',umf)
                vals["unidad_meta_fisica_id"]=id_unidad_mf
            else :
                vals["unidad_meta_fisica_id"]=cod_unidad_mf_ids[0]
            cantidad_mf = item["CANTIDAD METAS FISICAS "]
            try:
                vals["cantidad_meta_fisica"]=float(cantidad_mf)
            except :
                pass
        #Centro de costo
        ccosto = "%i" % float(item['CENTRO DE COSTO'])
        ids_centro_costo = openerp.search('stone_erp_idu.centro_costo',[('codigo','=',ccosto)])
        if (ids_centro_costo.__len__()==0):
            raise Exception ('El centro de costo no existe , revisar excel línea' + str(item['Fila_excel']))
        vals['centro_costo_id']=ids_centro_costo[0]
        vals['centro_costo']= ccosto
        #Fecha de radicacion
        #Si la fecha esta mal definida simplemente no la coge
        try:
            fr = eval(item['FECHA RADICACIÓN EN DTPS SEGÚN DTD'])
            fecha_rad = date(*fr[:3])
            vals['fecha_programada_radicacion']=str(fecha_rad)
        except:
            pass
        #Fecha crp
        try:
            fr = eval(item['FECHA PROGRAMADA CRP - ESTIMACIÓN DTD'])
            fecha_crp = date(*fr[:3])
            vals['fecha_programada_crp']=str(fecha_crp)
        except:
            pass
        #Pagos y sale pa pintura.
        pagos = []
        meses=[]
        meses.append({'id':1,'vmes':item['ENERO']}) #id mes y valor mes
        meses.append({'id':2,'vmes':item['FEBRERO']})
        meses.append({'id':3,'vmes':item['MARZO']})
        meses.append({'id':4,'vmes':item['ABRIL']})
        meses.append({'id':5,'vmes':item['MAYO']})
        meses.append({'id':6,'vmes':item['JUNIO']})
        meses.append({'id':7,'vmes':item['JULIO']})
        meses.append({'id':8,'vmes':item['AGOSTO']})
        meses.append({'id':9,'vmes':item['SEPTIEMBRE']})
        meses.append({'id':10,'vmes':item['OCTUBRE']})
        meses.append({'id':11,'vmes':item['NOVIEMBRE']})
        meses.append({'id':12,'vmes':item['DICIEMBRE']})
        
        for _m in meses:
            vmes = _m['vmes']
            if (vmes != ""):
                __val = str(float(vmes))#Especie de validacion para garantizar que vengan numeros
                pagos.append([0,False,{'mes':_m['id'],'valor':__val}])#Clave con la que entran los pagos al openerp
        if (pagos.__len__()>0):
            vals["plan_pagos_item_ids"] = pagos


        print "Exportando a openerp item "+str(item['Fila_excel'])
        #Prueba de fuego, pa mostrarle al Cinxgler:
        openerp.create("plan_contratacion_idu.item",vals)
        #openerp.execute_method('plan_contratacion_idu.item','on_change_centro_costo',0,ccosto,{})


        #Verificar si proyecto prioritario y proyecto de inversion en el clasificador
    



def prueba_exportar_datos_openerp(_plan_contratacion,_openerp_server,_port, _dbname,_user,_password,_vigencia):
    openerp = openerp_server_proxy.openerp_proxy(_openerp_server,_port,_user,_password,_dbname)
    id_item = 26
    vals = {}
    vals["presupuesto"]=1000000
    vals["localizacion"]="localidad"
    vals["localidad_id"]=[[6,False,[1,2,3,4,5,6,7,8,9]]]
    openerp.write('plan_contratacion_idu.item',id_item,vals)


plan_values = cargar_fichero_excel(path_excel,index_hoja,index_header)

plan_prueba=[{'':'','FECHA PROGRAMADA CRP - ESTIMACIÓN DTD':'(2014, 5, 1, 0, 0, 0)','Fila_excel':3,
              'VALIDACIÓN':'22057000.0','PPTO':'22057000.0','Fuente de Financiacion':'574.0','Grupo Valora':'2.0',
              'REZAGO':'10943001.0','NOMBRE PROYECTO INVERSIÓN':'Fortalecimiento Institucional para el mejoramiento de la gestión del IDU',
              'DEPENDENCIAS':'OAC','ABRIL':'','Nombre Sistema':'FORTALECIMIENTO INSTITUCIONAL','CENTRO DE COSTO':'30607.0','MAYO':'',
              'Nombre Pto Inversión':'PROGRAMA DE COMUNICACIONES','FECHA RADICACIÓN EN DTPS SEGÚN DTD':'(2014, 4, 1, 0, 0, 0)',
              'llave':'232-115-30607-100-574-10','CUPO ':'','PROCESO':'Contrato Nuevo','Número Línea':'1.0','UNIDAD METAS FISICAS':'',
              'TIPO DE PROCESO DE SELECCIÓN':'Selección abreviada mínima cuantía ','Plan de Desarrollo':'232.0','CÓD PROY PRIOR':'238.0',
              'AGOSTO':'1833333.0','Nombre Fuente de Financiacion':'RB VAL  AC 523/13','TOTAL 2014':'11113999.0','CÓD PROY INV ':'232.0',
              'Nombre Componente':'PRESTACION DE SERVICIOS','PLAZO DE EJECUCIÓN - ESTIMADO SEGÚN DTP':'12 meses','CÓDIGO LOC':'3,4,5 y 8',
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

# item1=plan_values[0]
# x="[{"
# for val in item1:
#     x=x+"'"+val+"':'"+str(item1[val])+"',"
# x = x + "}]"
# print x

exportar_datos_openerp(plan_values,openerp_server,port,dbname,user,pwd,vigencia)
#prueba_exportar_datos_openerp(plan_prueba,openerp_server,port,dbname,user,pwd,vigencia)
