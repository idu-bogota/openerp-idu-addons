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

from osv import osv, fields
import xml.etree.ElementTree as ET
import base64

class project_pmi_wbs_wizard_create_edt_from_file(osv.osv_memory):
    _name = 'project_pmi_wbs.wizard.create_edt_from_file'
    _description = 'Create a EDT for a project'

    _columns = {
        'name': fields.char('Name', size=128, required=False),
        'file':fields.binary('File'),
        'max_level_evaluate': fields.integer(string="Max level to evaluate", required=True),
        'min_level_task': fields.integer(string="Min level to generate task", required=True),
    }

    def action_create(self, cr, uid, ids, context=None):
        project_ids = context and context.get('active_ids', False)
        project_table = self.pool.get('project.project')    
        wbs_table = self.pool.get('project_pmi.wbs_item')            
        wizards = self.pool.get('project_pmi_wbs.wizard.create_edt_from_file').browse(cr,uid,ids,context=None)   
        for wizard in wizards:      
            tree = ET.XML(base64.decodestring(wizard.file))
            for task in tree.iter('{http://schemas.microsoft.com/project}Task'):
                outline_level = int(task.find('{http://schemas.microsoft.com/project}OutlineLevel').text)
                outline_number = task.find('{http://schemas.microsoft.com/project}OutlineNumber').text
                name = task.find('{http://schemas.microsoft.com/project}Name').text
                if outline_level <= wizard.max_level_evaluate:
                    print outline_number + ' - '  + name + ' level: ' 

        form_object_id = ids and ids[0] or False
        form_object = self.browse(cr, uid, form_object_id, context=context)

#         if(form_object.wbs_template_id):
#             context.update({'copy':True, 'reference_date':form_object.reference_date})
#             wbs_table.copy(cr, uid, form_object.wbs_template_id.id, default = None, context=context)
#         else:
#             wbs_table.create(cr, uid, None, context)

        return {'type': 'ir.actions.act_window_close'}

project_pmi_wbs_wizard_create_edt_from_file()
