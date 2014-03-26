# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2004-2014 Tiny SPRL (<http://tiny.be>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp_tools import openerp_server_proxy
from xlrd import open_workbook, xldate_as_tuple, XL_CELL_DATE
from datetime import date

openerp_server = "localhost"
pwd = "admin"
user = "admin"
dbname="open_erp_6"
port ="8069"
path_excel = "/home/juanfedo/proyectos/PQRS_Puntos_CREA.xls"
index_hoja = 0
index_header = 2
error = {}

print "SCRIPT DE CARGA DE DATOS A OPENERP PLAN CONTRATACION"
print "ANDRES DE EJECUTAR SCRIPT ASEGURESE DE QUE EL EXCEL ESTE EN FORMATO EXCEL 2003-2007, ya que la libreria"
print "XLRD solo soporta hasta Excel 2007"

print "openerp server :" + openerp_server
print "port :"+port
print "excel path :"+path_excel


def cargar_fichero_excel(_path_excel,_index_hoja,_row_index_header):
# """
# Crea un diccionario a partir del fichero excel de la forma
# [{'header_col1':value_col1_row1,'header_col2',value_col2_row1},{header_col1':value_col1_row2,'header_col2',value_col2__row2}]
# """
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

def exportar_datos_openerp(_plan_contratacion,_openerp_server,_port, _dbname,_user,_password,):
    openerp = openerp_server_proxy.openerp_proxy(_openerp_server,_port,_user,_password,_dbname)

    cont = 0
    for item in _plan_contratacion:
        vals={}
        vals_partner={}
        
        #crm.claim
        fr = eval(item['Fecha de atención (a-m-d)'])
        vals['date_deadline']= str(date(*fr[:3]))
        vals['claim_address'] = str(item['Dirección del asunto'])

        barrio_id = openerp.search('ocs.neighborhood',[('name','=',str(item['Barrio']))])
        vals['neighborhood_id'] = barrio_id[0]

        localidad_id = openerp.search('ocs.district',[('name','=',str(item['Localidad']))])
        vals['district_id'] = localidad_id[0]

        criterio_id = openerp.search('ocs.claim_classification',[('name','=',str(item['Criterio (Tipificación)']))])
        vals['classification_id'] = criterio_id[0]

        sub_criterio_id = openerp.search('ocs.claim_classification',[('name','=',str(item['Sub Criterio']))])
        vals['sub_classification_id'] = sub_criterio_id[0]

        requerimiento_id = openerp.search('crm.case.categ',[('name','=',str(item['Tipo requerimiento']))])
        vals['categ_id'] = requerimiento_id[0]

        vals['description'] = str(item['Asunto'])
        vals_partner['resolution'] = str(item['Solución'])
        
        canal_id = openerp.search('crm.case.channel',[('name','=',str(item['Canal de atención']))])
        vals['channel'] = canal_id[0]

        usuario_id = openerp.search('res.users',[('name','=',str(item['Funcionario que atendió']))])
        vals['user_id'] = usuario_id[0]
        
        punto_id = openerp.search('ocs.citizen_service_point',[('name','=',str(item['Punto de Atención']))])
        vals['csp_id'] = punto_id[0]

        if not str(item['Entidad']) == "":
            dependencia_id = openerp.search('res.partner',[('name','=',str(item['Entidad']))])
            vals['partner_forwarded_id'] = dependencia_id[0]

        #res.partner.address
        
        if not str(item['Número documento de identidad'])=="":
            vals_partner['document_number'] = str("%i" % float(item['Número documento de identidad']))
        vals_partner['name'] = str(item['Nombres'])
        vals_partner['last_name'] = str(item['Apellidos'])

        if 'M' == str(item['Genero'])[0]:
            vals_partner['gender'] = 'm'
        else:
            vals_partner['gender'] = 'f'

        if 'udada' in str(item['Tipo de documento']):
            vals_partner['document_type'] = 'CC'
        elif 'denti' in str(item['Tipo de documento']):
            vals_partner['document_type'] = 'TI'
        elif 'saporte' in str(item['Tipo de documento']):
            vals_partner['document_type'] = 'Pasaporte'
        elif 'xtranj' in str(item['Tipo de documento']):
            vals_partner['document_type'] = 'CE'

        if '@' in str(item['Datos de contacto']):
            vals_partner['email'] = str(item['Datos de contacto'])
        else:
            vals_partner['mobile'] = str(item['Datos de contacto'])
        vals_partner['street'] = str(item['Dirección correspondencia'])

        barrio_id = openerp.search('ocs.neighborhood',[('name','=',str(item['Barrio Correspondencia']))])
        if barrio_id:
            vals_partner['neighborhood_id'] = barrio_id[0]

        localidad_id = openerp.search('ocs.district',[('name','=',str(item['Localidad Correspondencia']))])
        vals_partner['district_id'] = localidad_id[0]
        user_id = {}
        user_id = openerp.search('res.partner.address',[('email','=',str(item['Datos de contacto']))])
        
        if not str(item['Número documento de identidad'])=="":
            user_id = openerp.search('res.partner.address',[('document_number','=', str("%i" % float(item['Número documento de identidad'])))])
        
        try:
            if not user_id:
                vals['partner_address_id'] = openerp.create("res.partner.address",vals_partner)
            else: 
                vals['partner_address_id'] = user_id[0]
            claim_id = openerp.create("crm.claim",vals)
            print "Exportando a openerp item "+str(item['Fila_excel'])
        except Exception as e:
            print 'Error en la fila:' + str(item['Fila_excel']) + ' ' + str(e)
            error[cont] = 'Error en la fila:' + str(item['Fila_excel']) + ' ' + str(e)
            cont+=1
            pass

plan_values = cargar_fichero_excel(path_excel,index_hoja,index_header)
exportar_datos_openerp(plan_values,openerp_server,port,dbname,user,pwd)
print 'Errores encontrados durante el proceso:'
print error