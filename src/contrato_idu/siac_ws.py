# -*- encoding: utf-8 -*-#
#############################################################################
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
#    Autor: Andres Ignacio Baez Alba
#    Arquitecto: Cinxgler Mariaca Minda
#    CIO: Gustavo Adolfo Velez Achury
#
##############################################################################
from suds.client import Client

def obtener_datos_contrato(wsdl_url,numero_contrato):
    """
    Médodo que consulta información del Sistema de Integrado de Apoyo Contractual (SIAC) 
    sobre los contratos:
    
    Entradas:  wsdl, ejemplo: http://172.16.2.233:9763/services/ws_siac?wsdl 
               numero_contrato, ejemplo: IDU-375-2012 
    
    Salidas:
            diccionario de la siguiente forma
            {
            'codigo_contrato':"IDU-365-2012",
            'numero_crp':111,
            'fechar-crp':2001 datetime.datetime(2013, 12, 2, 0, 0),
            'nit_contratista':118822112
            'fecha_acta_inicio':datetime.datetime(2013, 21, 2, 0, 0),
            'fecha_acta_liquidacion':datetime.datetime(2013, 21, 2, 0, 0),
            }
    """
    client = Client(wsdl_url)
    contrato = client.service.obtener_datos_contrato(numero_contrato)
    res={}
    if (len(contrato)):
        res["codigo_contrato"]=contrato["CODIGO"]
        res["numero_crp"]=contrato["CRP_NUM"]
        res["fechar_crp"]=contrato["FECHA_CRP"]
        res["nit_contratista"]=contrato["NIT_CONTRATISTA"]
        res["nombre_contratista"]=contrato["NOMBRE_CONTRATISTA"]
        res["fecha_acta_inicio"]=contrato["FECHA_ACTA_INICIO"]
        res["fecha_acta_liquidación"]=contrato["FECHA_ACTA_LIQUIDACION"]
    return res
    
