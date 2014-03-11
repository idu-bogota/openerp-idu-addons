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
        'min_level_task': fields.integer(string="Level to start generating tasks", required=True),
        'include_wbs_outline_number': fields.boolean("Include the wbs assigned code in the name?", required=False),
        'assign_task_to_current_user': fields.boolean("Assign new tasks to current user? otherwise they will be unassigned", required=False),
#         'take_leaves_as_tasks': fields.boolean("Take leaves as tasks", required=False),
        'take_leaves_as_tasks': fields.selection([('leaves_as_tasks', 'leaves as workpackage tasks'),('leaves_as_workpackages_unit', 'leaves as workpackages unit')],'Leaves as'),
        'uom_id': fields.many2one('product.uom', 'Unit of Measure', help="Default Unit of Measure used"),
        'quantity': fields.float('Quantity'),
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
    
    def put_tree_on_struct (self,tree):
        struct = {}
        for task in tree.iter('{http://schemas.microsoft.com/project}Task'):
            temp = task.find('{http://schemas.microsoft.com/project}OutlineNumber').text.split('.')
            father = ''
            if len(temp) == 1:
                father = '0'
            else:
                for cad in range(len(temp) - 1):
                    father += temp[cad] + '.'
                father = father[:-1]
            struct[task.find('{http://schemas.microsoft.com/project}OutlineNumber').text] = father
        return struct

    #flag must always be 1
    #return == 1 is Task
    #       == 0 is Package
    #       == -1 is Deliverable  
    def get_type(self,struct,id,flag):
        for key in struct:
            if struct[key] == id:
                if flag > -1:
                    return self.get_type(struct, key,flag -1)
        return flag

    def validate_type(self,type,struct,struct_type,outline_number):
        #un deliverable no tenga hijos task
        if type == 1:
            for key in struct:
                if key == outline_number:
                    for key1 in struct_type:
                        if struct_type[struct[key]] == -1:
                            return 0
        #un workpackage no tenga hijos deliverables
        elif type == -1:
            for key in struct:
                if key == outline_number:
                    for key1 in struct_type:
                        if struct_type[struct[key]] == 0:
                            return 0
        return type

    def save_info(self,struct,struct_type,outline_number ,data,task,add_days,name,parent_ids,outline_level,cr,uid,context,wizard,type):
        data_task_create = False
        if type != 0:
            type = self.validate_type(type, struct, struct_type, outline_number)
        if type == -1:
            data['type'] = 'deliverable'
        elif type == 0:
            date_start = self.get_date(task.find('{http://schemas.microsoft.com/project}Start').text) + timedelta(days=add_days)
            date_deadline = self.get_date(task.find('{http://schemas.microsoft.com/project}Finish').text) - timedelta(days=add_days)
            data['type'] = 'work_package'
            data['tracking_type'] = 'tasks'
            data['date_start'] = date_start.strftime('%Y-%m-%d')
            data['date_deadline'] = date_deadline.strftime('%Y-%m-%d')
        else:
            data_task = {'name':name,
                         'wbs_item_id':parent_ids[outline_level -1],
                         'state': 'draft',
                         }
            if not wizard.assign_task_to_current_user:
                data_task['user_id'] = None
            self.pool.get('project.task').create(cr, uid, data_task, context)
            data_task_create = True
        if not data_task_create:
            parent_ids.insert(outline_level, self.pool.get('project_pmi.wbs_item').create(cr, uid, data, context))
        struct_type[outline_number] = type

    def save_info_leave_workpackage(self,struct,struct_type,outline_number ,data,task,add_days,name,parent_ids,outline_level,cr,uid,context,wizard,type):
        if type != 0:
            type = self.validate_type(type, struct, struct_type, outline_number)
        if type != 1:
            data['type'] = 'deliverable'
        else:
            date_start = self.get_date(task.find('{http://schemas.microsoft.com/project}Start').text) + timedelta(days=add_days)
            date_deadline = self.get_date(task.find('{http://schemas.microsoft.com/project}Finish').text) - timedelta(days=add_days)
            data['type'] = 'work_package'
            data['tracking_type'] = 'units'
            data['quantity'] = wizard.quantity
            data['date_start'] = date_start.strftime('%Y-%m-%d')
            data['date_deadline'] = date_deadline.strftime('%Y-%m-%d')
            data['uom_id'] = wizard.uom_id.id
            if not wizard.assign_task_to_current_user:
                data['user_id'] = None
        parent_ids.insert(outline_level, self.pool.get('project_pmi.wbs_item').create(cr, uid, data, context))

    def take_leaves_as_tasks(self,struct,struct_type,outline_number,task,parent_ids,outline_level,context,data,name,cr,uid,add_days,wizard):
        type = self.get_type(struct, outline_number, 1)
        self.save_info(struct,struct_type, outline_number ,data, task, add_days, name, parent_ids, outline_level, cr, uid, context, wizard, type)

    def take_leaves_as_workpackage(self,struct,struct_type,outline_number,task,parent_ids,outline_level,context,data,name,cr,uid,add_days,wizard):
        type = self.get_type(struct, outline_number, 1)
        self.save_info_leave_workpackage(struct,struct_type, outline_number ,data, task, add_days, name, parent_ids, outline_level, cr, uid, context, wizard, type)

    def create_normal_tree(self,struct,outline_level,wizard,task,add_days,data,name,parent_ids,cr,uid,context):
        if outline_level < wizard.min_level_task -1:
            type = -1
        elif outline_level == wizard.min_level_task - 1:
            type = 0
        else:
            type = 1
        self.save_info(struct,struct,-1,data, task, add_days, name, parent_ids, outline_level, cr, uid, context, wizard, type)

    def action_create(self, cr, uid, ids, context=None):
        wizards = self.pool.get('project_pmi_wbs.wizard.create_wbs_from_file').browse(cr,uid,ids,context=None)
        struct = {}
        struct_type = {}
        try:
            for wizard in wizards:
                tree = ET.XML(base64.decodestring(wizard.file))
                date_project = tree.find('{http://schemas.microsoft.com/project}StartDate').text
                add_days = self.calculate_days(date_project)
                parent_ids = [0]
                if wizard.take_leaves_as_tasks:
                    struct = self.put_tree_on_struct(tree)
                for task in tree.iter('{http://schemas.microsoft.com/project}Task'):
                    outline_level = int(task.find('{http://schemas.microsoft.com/project}OutlineLevel').text)
                    outline_number = task.find('{http://schemas.microsoft.com/project}OutlineNumber').text
                    if task.find('{http://schemas.microsoft.com/project}Name') != None:
                        name = task.find('{http://schemas.microsoft.com/project}Name').text
                    else:
                        name = ''
                    if wizard.include_wbs_outline_number:
                        name = '{0} {1}'.format(outline_number, name)
                    if outline_level <= wizard.max_level_evaluate:
                        data = {'name':name,
                                'parent_id':parent_ids[outline_level -1],
                                'state': 'draft',
                                }
                        if wizard.take_leaves_as_tasks == 'leaves_as_tasks':
                            self.take_leaves_as_tasks(struct,struct_type, outline_number, task, parent_ids, outline_level, context, data, name, cr, uid, add_days,wizard)
                        elif wizard.take_leaves_as_tasks == 'leaves_as_workpackages_unit':
                            self.take_leaves_as_workpackage(struct, struct_type, outline_number, task, parent_ids, outline_level, context, data, name, cr, uid, add_days, wizard)
                        else :
                            self.create_normal_tree(struct,outline_level, wizard, task, add_days, data, name, parent_ids, cr, uid, context)

#                     print outline_number + ' - '  + name
        except Exception as e:
            raise osv.except_osv('Error loading the tree', str(e))
        return {'type': 'ir.actions.act_window_close'}

project_pmi_wbs_wizard_create_wbs_from_file()
