# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Instituto de Desarrollo Urbano (<http://www.idu.gov.co>).
#     All Rights Reserved
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
#    Realizado por: Andrés Ignacio Báez Alba andresignaciob@gmail.com
#
#
##############################################################################
from suds.client import Client
#WSDL = "http://172.16.2.233:9763/services/ws_stone_plan_contratacion?wsdl"

def completar_datos_centro_costo(wsdl_url,centro_costo):
    """
    Metodo que recibe como parámetro de entrada el wsdl del web service de conexión con
    stone y devuelve un diccionario con información de los centros de costo de la siguiente manera:    
    {'nombre_centro_costo':--value--, 
                        'nombre_proyecto':--value--, #Nombre del proyecto IDU
                        'nombre_punto':--value--,  #Nombre del punto de Inversion
                        'proyecto':--value-- #Código del proyecto IDU
                        'punto':--value-- #Código del punto de inversión    
    }    
    """
    try:
        client = Client(wsdl_url)
        res={}
        c_costo = int(centro_costo)
        punto_inversion = client.service.obtener_proyecto_punto_inversion(c_costo)
        res['centro_costo']=c_costo
        res['proyecto_idu']=punto_inversion["nombre_proyecto"]
        res['punto_inversion']=punto_inversion["nombre_punto"]
        res['proyecto_idu_id']=punto_inversion["proyecto"]
        res['punto_inversion_id']=punto_inversion["punto"]
        return res
    except Exception:
        return False


def obtener_centros_costo(wsdl_url):
    """
    Metodo que recibe como parámetro de entrada el wsdl del web service de conexión con
    stone y devuelve un diccionario con información de los centros de costo de la siguiente manera:    
    {
    codigo_centro_costo:nombre_centro_costo
    }
    
    """    
    try:
        client = Client(wsdl_url)
        planc = client.service.obtener_centro_costo()
        COD_CCOS=planc[0]
        NOM_CCOS=planc[1]
        index=0
        centros_costo = {}
        for num in COD_CCOS:
            centros_costo[num] = NOM_CCOS[index]
            index = index+1 
        return centros_costo
    except Exception as e:
        raise e


