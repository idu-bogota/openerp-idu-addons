# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
#
#    Creado por Andres Ignacio Baez Alba
#
##############################################################################

from osv import osv, fields
import xlrd
import base64
class urban_bridge_wizard_import_elements(osv.osv_memory):
    """
    Wizard to load information from excel
    """ 
    _name="urban_bridge.wizard.import_elements"
    _columns={
        'srid':fields.integer('Source SRID','Source Data System Reference'),
        'element':fields.many2one('urban_bridge.structure_element_type','Element Type'),
        'file':fields.binary('File'),
    }
    
    def next (self,cr,uid,ids,context=None):
        dirs=[]
        for wizard in self.browse(cr,uid,ids,context=None):
            #fileobj = TemporaryFile('w+')
            #fileobj.write(base64.decodestring(wizard.file))
            workbook = xlrd.open_workbook(file_contents=base64.decodestring(wizard.file))
            worksheets = workbook.sheet_names()
            for worksheet_name in worksheets:
                dirs.append(str(worksheet_name))
            
            #1. Listar las hojas que se encuentran en el fichero y ponerlas en un combobox
        return {'type': 'ir.actions.act_window_close','work_sheets':dirs}
    
    
