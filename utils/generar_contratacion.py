# -*- coding: utf-8 -*-
from openerp_tools.generador_xml import xml_datalayer,campo,registro
from xlrd import open_workbook


path = r"/home/cabaezal1/proyectos/pc2014.xls"
path_dep=r"/home/cabaezal1/proyectos/dependencias.xls"

def obtener_dependencias(path_excel):
    """
    Generar arbol de las areas (dependencias)
    """
    
    """
    Arma un diccionario con los valores
    """
    model = 'hr_department'
    index_hoja=0#indice de la hoja de excel donde viene el arbol de dependencia
    wb = open_workbook(path_excel)
    hoja_datos = wb.sheet_by_index(index_hoja)
    row_index=2 #hoja donde inician los datos
    index_parent = 0
    index_codigo = 1
    index_name = 2
    index_company_id =3
    res = {
        'model':model,
        'key':'codigo',
        'registros':[]
    }
    
    while (row_index < hoja_datos.nrows):
        dato = {}
        key_ref = hoja_datos.cell(row_index,index_parent).value
        dato['parent']= {'model':model,'key_ref':key_ref}
        dato['codigo']= hoja_datos.cell(row_index,index_codigo).value
        dato['name']= hoja_datos.cell(row_index,index_name).value
        dato['company_id/id']= hoja_datos.cell(row_index,index_company_id).value
        res['registros'].append(dato)
    return res




def generar_estructura_datos(excel_plan_c,excel_dependencia):
    """
    pc = plan contratacion = > Estructura de datos con toda la información de todo
    """
    pc = {
            'clasificador_proyecto':{},
            'dependencia':{},
            'fuente_financiacion':{},
            'tipo_proc_selec':{},
            'localizacion':{},
            'localidad':{},
            'item':{},
    }
    pc['dependencia']=obtener_dependencias(excel_dependencia)
    return pc


datos = generar_estructura_datos(path,path_dep)

print datos
