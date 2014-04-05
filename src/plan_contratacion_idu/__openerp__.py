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


{
    'name': 'Gestión y seguimiento del plan de contratación del IDU',
    'version': '1.0',
    'category': 'Contract Management',
    'description': """
    Este módulo permite hacer el registro y seguimiento al plan de contratación del IDU


    1. INSTALACION DEL PAQUETE

     Configuración - Módulos - Módulos Locales
        Ubicar el módulo: Gestión y seguimiento del plan de contratación del IDU plan_contratacion_idu
        Instalar
        Seleccionar idioma


    2. CONFIGURACION DEL SERVIDOR

    *Formato separador
        Configuración - Traducciones - Idiomas
            Formato separador: [3,0]

    *Simbolo pesos
        Configuración - Compañias - Compañias
        Seleccionar la compañia y click en editar
        Seleccionar pestaña configuración
        Seleccionar editar moneda COP
        verificar simbolo y posición del simbolo

    *Acciones Planificadas
        Configuración - Técnico - Planificación - Acciones Planificadas
            Crear:

            - Nombre: obtener_datos_contrato_siac
              Activo: True
              Usuario: Administrator
              Prioridad: 1
              Información
                  Número de intervalos: 1
                  Unidad de intervalo: Minutos
                  Siguiente fecha de ejecución: Fecha y hora actual
                  Número de ejecuciones: -1
                  Repetir perdidos: False
              Datos Técnicos
                  Acción a activar Objeto: plan_contratacion_idu.item
                  Método: obtener_datos_contrato
                  Argumentos: ()

            - Nombre: obtener_pagos_realizados_stone
              Activo: True
              Usuario: Administrator
              Prioridad: 1
              Información
                  Número de intervalos: 1
                  Unidad de intervalo: Minutos
                  Siguiente fecha de ejecución: Fecha y hora actual
                  Número de ejecuciones: -1
                  Repetir perdidos: False
              Datos Técnicos
                  Acción a activar Objeto: plan_contratacion_idu.item
                  Método: obtener_pagos_realizados
                  Argumentos: ()

    *Parámetros del Sistema
        Configuración - Técnico - Parámetros - Parámetros del Sistema
            Crear:
            -  Clave: siac_idu.webservice.wsdl
               Valor: http://172.16.2.233:9763/services/ws_siac?wsdl

            -  Clave: stone_idu.webservice.wsdl
               Valor: http://172.16.2.233:9763/services/ws_stone?wsdl


    3. CARGAR DATOS

    * Importar datos objetos
        Los archivos para cargar los objetos están ubicados en /git/openerp-idu-addons/src/data_idu/plan_contratacion_idu/

        Departamentos:
            Recursos Humanos - Configuración - Departamentos
                importar archivo: hr.department.csv

        Vigencia:
            Crear vigencia para el Plan de Contratación
                Contratación - Plan de Contratación -Plan Contratación
                Crear: ingresar año, estado

        Clasificacion de proyectos
            Contratación - Plan de Contratación - item plan contratación
            Crear, ubicar el campo clasificación proyecto, crear y editar y crear un test de ejemplo
            Contratación - Plan de Contratación - Clasificacion de Proyectos
            Click en test, click en importar, importar archivo: plan_contratacion_idu_clasificador_proyectos.csv

         Fuente de Financiación:
            Contratación - Plan de Contratación - Fuente de Financiación
            importar archivo: plan_contratacion_idu_fuente.csv

         Tipo Proceso:
            Contratación - Plan de Contratación - Tipo Proceso del Item
            importar archivo: plan_contratacion_idu_plan_tipo_proceso_item.csv

         Tipo Proceso de Selección:
            Contratación - Plan de Contratación - Tipo Proceso de Selección
            importar archivo: plan_contratacion_idu_plan_tipo_proceso_seleccion_item.csv

    * Cargar datos Localidades
        seguir instrucciones indicadas en el archivo Instrucciones_cargue_localidates.txt
        ubicado en /git/openerp-idu-addons/src/data_idu/


    * Importar items al sistema desde el formato excel
        Parametrizar el fichero carga_plan_contratacion.py (lineas 25- 33)
        ubicado en /git/openerp-idu-addons/utils
            vigencia = año del plan de contratación ejemplo: "2014"
            openerp_server = nombre del servidor OpenERP ejemplo: "A-1502"
            pwd = password de ingreso al servidor, ejemplo: "passw"
            user = nombre del usuario para el ingreso al servidor, ejemplo: "user"
            dbname= nombre de la base de datos, ejemplo: "plan_contratacion"
            port = puerto de acceso al servidor OpenERP, ejemplo: "8069"
            path_excel = ruta de ubicación y nombre del archivo excel, ejemplo: "/home/clreyesb1/Escritorio/datos_plan/pc2014.xls"
            index_hoja = index de la hoja donde esta la información del plan, ejemplo: 9
            index_header = index de la fila donde esta la información del plan, ejemplo: 1
        Despues de parametrizado el fichero, debe asegurarse que esté en ejecución del Plan de Contratación
        y desde terminal ubicarse en la ruta /git/openerp-idu-addons/utils/ y desde este punto
        ejecutar en linea de comando: python carga_plan_contratacion.py
        Si se reporta algún error verificar los valores de parametrización el fichero o si es un
        error de la información del excel.

""",
    'author': 'Instituto De Desarrollo Urbano',
    'website': 'http://www.idu.gov.co',
    'depends': [
        'base','hr','contrato_idu','stone_erp_idu','base_map'
    ],
    'data': [
        'security/plan_contratacion_idu_security.xml',
        'plan_contratacion_idu_data.xml',
        'wizard/solicitar_cambio_view.xml',
        'wizard/obtener_crp_view.xml',
        'plan_contratacion_idu_view.xml',
        'wizard/reporte_excel_view.xml',
        'security/ir.model.access.csv',
        'report/plan_contratacion_idu_report_view.xml',
        'report/plan_contratacion_idu_report_presupuesto_view.xml'
    ],
    'test': [
        'test/000_datos_base.yml',
        'test/010_plan_contratacion.yml',
    ],

    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: