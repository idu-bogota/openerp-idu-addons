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
#     developed by: Julian Andres Fernandez
#
##############################################################################

from osv import osv, fields
import xml.etree.ElementTree as ET
import base64
from datetime import date,timedelta

class project_pmi_wbs_wizard_create_wbs_from_file(osv.osv_memory):
    _name = 'project_pmi_wbs.wizard.create_wbs_from_file'
    _description = 'Create a WBS for a project'

    _columns = {
        'file':fields.binary('File'),
        'max_level_evaluate': fields.integer(string="Maximum level to evaluate", required=True),
        'min_level_task': fields.integer(string="Level to generate tasks", required=True),
        'include_wbs_outline_number': fields.boolean("Include the wbs assigned code in the name?", required=True),
    }

    def calculate_days(self,date1):
        today = date.today()
        date_project = date(int(date1[0:4]), int(date1[5:7]), int(date1[8:10]))
        actual_date = date(today.year,01,01)
        days = actual_date - date_project
        return int(days.days)
    
    def get_date(self,date_project):
        date_temp = date(int(date_project[0:4]),
                          int(date_project[5:7]),
                          int(date_project[8:10]))
        return date_temp 

    def action_create(self, cr, uid, ids, context=None):
        wizards = self.pool.get('project_pmi_wbs.wizard.create_wbs_from_file').browse(cr,uid,ids,context=None)
        for wizard in wizards:
            tree = ET.XML(base64.decodestring(wizard.file))
            date_project = tree.find('{http://schemas.microsoft.com/project}StartDate').text
            add_days = self.calculate_days(date_project)
            parent_ids = [0]
            for task in tree.iter('{http://schemas.microsoft.com/project}Task'):
                data_task_create = False
                outline_level = int(task.find('{http://schemas.microsoft.com/project}OutlineLevel').text)
                name = task.find('{http://schemas.microsoft.com/project}Name').text
                if wizard.include_wbs_outline_number:
                    outline_number = task.find('{http://schemas.microsoft.com/project}OutlineNumber').text
                    name = '{0} {1}'.format(outline_number, name)
                if outline_level <= wizard.max_level_evaluate:
                    data = {'name':name,
                            'parent_id':parent_ids[outline_level -1],
                            }
                    if outline_level < wizard.min_level_task:
                        data['type'] = 'deliverable'
                    elif outline_level == wizard.min_level_task:
                        date_start = self.get_date(task.find('{http://schemas.microsoft.com/project}Start').text) + timedelta(days=add_days)
                        date_deadline = self.get_date(task.find('{http://schemas.microsoft.com/project}Finish').text) - timedelta(days=add_days)
                        data['type'] = 'work_package'
                        data['tracking_type'] = 'tasks'
                        data['date_start'] = date_start.strftime('%Y-%m-%d')
                        data['date_deadline'] = date_deadline.strftime('%Y-%m-%d')
                    else:
                        data_task = {'name':name,
                                    'wbs_item_id':parent_ids[outline_level -1],
                                    }
                        self.pool.get('project.task').create(cr, uid, data_task, context)
                        data_task_create = True
                    if not data_task_create:
                        parent_ids.insert(outline_level, self.pool.get('project_pmi.wbs_item').create(cr, uid, data, context))
#                     print outline_number + ' - '  + name
        return {'type': 'ir.actions.act_window_close'}

project_pmi_wbs_wizard_create_wbs_from_file()
