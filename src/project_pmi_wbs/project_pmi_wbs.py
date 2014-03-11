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

from openerp.osv import fields, osv
import time
from datetime import datetime,date,timedelta
from osv import osv

class project(osv.osv):
    _name = "project.project"
    _inherit = "project.project"

    def _wbs_item_count(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        res = dict.fromkeys(ids, 0)
        ctx = context.copy()
        ctx['active_test'] = False
        item_ids = self.pool.get('project_pmi.wbs_item').search(cr, uid, [('project_id', 'in', ids)], context=ctx)
        for item in self.pool.get('project_pmi.wbs_item').browse(cr, uid, item_ids, context):
            res[item.project_id.id] += 1
        return res

    _columns = {
        'wbs_item_ids': fields.one2many('project_pmi.wbs_item', 'project_id', string='Work Breakdown Structure'),
        'wbs_items_count': fields.function(_wbs_item_count, type='integer', string="WBS items count"),
    }

project()

class task(osv.osv):
    _name = "project.task"
    _inherit = "project.task"

    _columns = {
        'wbs_item_id': fields.many2one('project_pmi.wbs_item', 'Work Breakdown Structure', domain="[('project_id','=',project_id),('type','=','work_package')]"),
    }
    _defaults = {
        'phase_id' : lambda self, cr, uid, context : context['phase_id'] if context and 'phase_id' in context else None,
    }

task()

class project_pmi_wbs_item(osv.osv):
    _name = "project_pmi.wbs_item"
    _inherit = ['mail.thread']
    _description = "WBS item"

    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'sequence, name'
    _order = 'parent_right DESC'

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','parent_id','type'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    def _listing_name(self, cr, uid, ids, prop, unknow_none, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','parent_id','type'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name_parts = record['parent_id'][1].split(' / ')
                parts = ['--' for i in name_parts]
                name = ' '.join(parts) + ' ' + name
            res.append((record['id'], name))
        return dict(res)


    def _progress_rate(self, cr, uid, ids, names, arg, context=None):
        child_parent = self._get_wbs_item_and_children(cr, uid, ids, context)
        # compute planned_hours, total_hours, effective_hours specific to each project
        cr.execute("""
            SELECT
                wbs_item.id, COALESCE(wbs_item.quantity, 0.0), COALESCE(SUM(wr.quantity), 0.0), wbs_item.type,wbs_item.weight, wbs_item.tracking_type, COUNT(t.id), SUM(t.progress),wbs_item.state
            FROM
                project_pmi_wbs_item wbs_item
                LEFT JOIN project_pmi_wbs_work_record wr ON wr.wbs_item_id = wbs_item.id
                LEFT JOIN project_task t ON t.wbs_item_id = wbs_item.id AND t.state <> 'cancelled'
            WHERE
                wbs_item.id IN %s AND wbs_item.state <> 'cancelled' AND wbs_item.state <> 'template'
            GROUP BY wbs_item.id
         """, (tuple(child_parent.keys()),))
        # aggregate results into res
        res = dict([(id, {'progress_rate':0.0,'planned_quantity':0.0,'effective_quantity':0.0,'excess_progress':0.0}) for id in child_parent])
        all_records = cr.fetchall()

        for id, planned, effective, type, weight, tracking_type, task_count, task_progress, state in all_records:
            res[id]['type'] = type
            res[id]['state'] = state
            res[id]['progress_rate'] = 0
            task_progress = task_progress or 0
            # add the values specific to id to all parent wbs_items of id in the result
            if weight:
                res[id]['weight'] = (weight/100)
            else:
                res[id]['weight'] = 0
            if res[id]['type'] == 'work_package' and tracking_type == 'tasks':
                planned += task_count * 100
                effective += task_progress
            res[id]['planned_quantity'] += planned
            res[id]['effective_quantity'] += effective
        # compute progress rates
        for id in sorted(child_parent.keys(), reverse=True):
            progress = 0.0
            records = {}
            if child_parent[id]:
                records = self.read(cr, uid, child_parent[id], ['use_weight'], context=context)
            else:
                records['use_weight'] = False
            if records['use_weight']:
                if self._get_values_dictionary(child_parent,id) == 0:
                    if res[id]['planned_quantity'] and res[id]['type'] == 'work_package':
                        progress = round(100.0 * res[id]['effective_quantity'] / res[id]['planned_quantity'], 2)
                        if progress > 99.99:
                            res[id]['excess_progress'] = progress - 99.99
                            progress = 99.99
                            if res[id]['state'] == 'done':
                                res[id]['progress_rate'] = 100.0
                            else:
                                res[id]['progress_rate'] = progress
                        else:
                            if (progress):
                                res[id]['progress_rate'] = progress
                        while id:
                            id_parent = child_parent[id]
                            if id_parent:
                                if ('progress_rate' in res[id_parent]):
                                    if(progress):
                                        res[id_parent]['progress_rate'] += round(progress * res[id]['weight'], 2)
                                        progress = 0
                                    else:
                                        res[id_parent]['progress_rate'] += round(res[id]['progress_rate'] * res[id]['weight'], 2)
                            id = child_parent[id]
            else:
                value = 1
                while id:
                    if res[id]['planned_quantity'] and res[id]['type'] == 'work_package':
                        progress = round(100.0 * res[id]['effective_quantity'] / res[id]['planned_quantity'], 2)
                        if progress > 99.99:
                            res[id]['excess_progress'] = progress - 99.99
                            progress = 99.99
                            if res[id]['state'] == 'done':
                                res[id]['progress_rate'] = 100.0
                            else:
                                res[id]['progress_rate'] = progress
                        else:
                            res[id]['progress_rate'] = progress
                    else:
                        number = self._get_values_dictionary(child_parent,id)
                        if number > 0:
                            value *= number
                        res[id]['progress_rate'] += progress / value
                    id = child_parent[id]
        if len(res) == 1:
            if len(child_parent) == 1:
                for val in res:
                    if (not 'state' in res[val]):
                        if res[val]['state'] == 'done':#
                            task_id = self.pool.get('project.task').search(cr, uid, [('wbs_item_id','=',val)], context=context)
                            if res[val]['type'] == 'work_package' and len(task_id) == 0:
                                res[val]['progress_rate'] = 100.0
                                res[val]['planned_quantity'] = 100.0
                                res[val]['effective_quantity'] = 100.0
        return res

    def _get_values_dictionary(self,my_dictionary,my_value):
        number = 0
        for key,value in my_dictionary.items():
            if value == my_value:
                number +=1
        return number

    def _get_wbs_item_and_children(self, cr, uid, ids, context=None):
        """ retrieve all children wbs items of wbs_item ids;
            return a dictionary mapping each wbs_item to its parent wbs_item (or None)
        """
        res = dict.fromkeys(ids, None)
        while ids:
            cr.execute("""
                SELECT wbs_item.id, parent.id
                FROM project_pmi_wbs_item wbs_item
                LEFT JOIN project_pmi_wbs_item parent ON wbs_item.parent_id = parent.id
                WHERE wbs_item.parent_id IN %s
                """, (tuple(ids),))
            dic = dict(cr.fetchall())
            res.update(dic)
            ids = dic.keys()
        return res

    def _get_wbs_item_from_work_records(self, cr, uid, work_record_ids, context=None):
        """
        Returns IDs of current and parent wbs_item, to be used to update the progres_rate using updated work_records
        """
        work_records = self.pool.get('project_pmi.wbs_work_record').browse(cr, uid, work_record_ids, context=context)
        wbs_item_ids = [wr.wbs_item_id.id for wr in work_records if wr.wbs_item_id]
        return self.pool.get('project_pmi.wbs_item')._get_wbs_item_and_parents(cr, uid, wbs_item_ids, context)

    def _get_wbs_item_from_tasks(self, cr, uid, task_ids, context=None):
        """
        Returns IDs of current and parent wbs_item, to be used to update the progres_rate using updated tasks
        """
        tasks = self.pool.get('project.task').browse(cr, uid, task_ids, context=context)
        wbs_item_ids = [wr.wbs_item_id.id for wr in tasks if wr.wbs_item_id]
        return self.pool.get('project_pmi.wbs_item')._get_wbs_item_and_parents(cr, uid, wbs_item_ids, context)

    def _get_wbs_item_and_parents(self, cr, uid, ids, context=None):
        """
        Returns IDs of current and parent wbs_item, to be used to update the progres_rate
        """
        res = set(ids)
        while ids:
            cr.execute("""
                SELECT DISTINCT parent.id
                FROM project_pmi_wbs_item wbs_item
                LEFT JOIN project_pmi_wbs_item parent ON wbs_item.parent_id = parent.id
                WHERE wbs_item.id IN %s
                """, (tuple(ids),))
            ids = [t[0] for t in cr.fetchall()]
            res.update(ids)
        return list(res)

    _columns = {
        'project_id': fields.many2one('project.project','Project'),
        'phase_id': fields.many2one('project.phase','Phase', domain="[('project_id','=',project_id)]"),
        'is_root_node': fields.boolean('Is a root node for the project WBS',help='Any project with a WBS can have several WBS Items, but one active WBS item as root node'),
        'code': fields.char('Code', size=20, required=True, select=True),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Name'),
        'listing_name': fields.function(_listing_name, type="char", string='Name'),
        'name': fields.char('Name', size=255, required=True, select=True),
        'type': fields.selection([('work_package', 'Work Package'),('deliverable', 'Deliverable')],'Deliverable Type', required=True),
        'tracking_type': fields.selection([('tasks', 'Tasks'),('units', 'Units')],'Tracking Type', required=False),
        'description': fields.text('Description'),
        'active':fields.boolean('Active',help='Enable/Disable'),
        'state':fields.selection([('draft', 'Draft'),('open', 'In Progress'),('cancelled', 'Cancelled'),('done', 'Done'),('pending', 'Pending'),('template', 'Template')],'State'),
        'quantity': fields.float('Quantity'),
        'uom_id': fields.many2one('product.uom', 'Unit of Measure', help="Default Unit of Measure used"),
        'parent_id': fields.many2one('project_pmi.wbs_item','Parent Deliverable', select=True, ondelete='cascade'),
        'child_ids': fields.one2many('project_pmi.wbs_item', 'parent_id', string='Child Deliverables'),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list."),
        'parent_left': fields.integer('Left Parent', select=1),
        'parent_right': fields.integer('Right Parent', select=1),
        'color': fields.integer('Color Index'),
        'date_deadline': fields.date('Deadline', help="For template items, this date will be copied using current context reference_date provided"),
        'date_start': fields.date('Starting Date'),
        'date_end': fields.date('Ending Date'),
        'excess_progress': fields.function(_progress_rate, multi="progress", string='Excess Progress', type='float', group_operator="avg",
             help="Total work quantity planned", store = {
                'project_pmi.wbs_item': (_get_wbs_item_and_parents, ['parent_id', 'child_ids','quantity','state','weight','use_weight'], 10),
                'project_pmi.wbs_work_record': (_get_wbs_item_from_work_records, ['wbs_item_id', 'quantity'], 20),
                'project.task': (_get_wbs_item_from_tasks, ['wbs_item_id', 'work_ids', 'remaining_hours', 'planned_hours','state'], 30),
            }
         ),
        'planned_quantity': fields.function(_progress_rate, multi="progress", string='Planned Quantity', type='float', group_operator="avg",
             help="Total work quantity planned", store = {
                'project_pmi.wbs_item': (_get_wbs_item_and_parents, ['parent_id', 'child_ids','quantity','state','weight','use_weight'], 10),
                'project_pmi.wbs_work_record': (_get_wbs_item_from_work_records, ['wbs_item_id', 'quantity'], 20),
                'project.task': (_get_wbs_item_from_tasks, ['wbs_item_id', 'work_ids', 'remaining_hours', 'planned_hours','state'], 30),
            }
         ),
        'effective_quantity': fields.function(_progress_rate, multi="progress", string='Effective Quantity', type='float', group_operator="avg",
             help="Percent of progress according to the total of work recorded.", store = {
                'project_pmi.wbs_item': (_get_wbs_item_and_parents, ['parent_id', 'child_ids','quantity','state','weight','use_weight'], 10),
                'project_pmi.wbs_work_record': (_get_wbs_item_from_work_records, ['wbs_item_id', 'quantity'], 20),
                'project.task': (_get_wbs_item_from_tasks, ['wbs_item_id', 'work_ids', 'remaining_hours', 'planned_hours','state'], 30),
            }
         ),
        'progress_rate': fields.function(_progress_rate, multi="progress", string='Progress', type='float', group_operator="avg",
             help="Percent of progress according to the total of work recorded.", store = {
                'project_pmi.wbs_item': (_get_wbs_item_and_parents, ['parent_id', 'child_ids','quantity','state','weight','use_weight'], 10),
                'project_pmi.wbs_work_record': (_get_wbs_item_from_work_records, ['wbs_item_id', 'quantity'], 20),
                'project.task': (_get_wbs_item_from_tasks, ['wbs_item_id', 'work_ids', 'remaining_hours', 'planned_hours','state'], 30),
            }
         ),
        'work_record_ids': fields.one2many('project_pmi.wbs_work_record', 'wbs_item_id', 'Work done'),
        'task_ids': fields.one2many('project.task', 'wbs_item_id', 'Tasks'),
        'weight': fields.float('Weight'),
        'use_weight': fields.boolean('Uses weight?',help='If active, weight is used to calculate progress rate'),
    }
    _defaults = {
        'active': True,
        'state': 'draft',
        'use_weight': False,
        'code': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'project_pmi.wbs'),
        'project_id' : lambda self, cr, uid, context : context['project_id'] if context and 'project_id' in context else None, #Set by default the project given in the context
        'phase_id' : lambda self, cr, uid, context : context['phase_id'] if context and 'phase_id' in context else None,
    }

    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from project_pmi_wbs_item where id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    def _check_no_childs(self,cr,uid,ids,context=None):
        res = {}
        records = self.read(cr, uid, ids, ['type','tracking_type','progress','child_ids','task_ids','work_record_ids'], context=context)
        for record in records:
            res[record['id']] = True
            if record['type'] == 'work_package' and len(record['child_ids']):
                res[record['id']] = False
        return reduce(lambda x, y: x and y, res.values())

    def _check_no_work_or_taks(self,cr,uid,ids,context=None):
        res = {}
        records = self.read(cr, uid, ids, ['type','tracking_type','progress','child_ids','task_ids','work_record_ids'], context=context)
        for record in records:
            res[record['id']] = True
            if record['type'] == 'deliverable' and (len(record['task_ids']) or len(record['work_record_ids'])):
                res[record['id']] = False
        return reduce(lambda x, y: x and y, res.values())

    def _check_unit_measure_work_package(self,cr,uid,ids,context=None):
        res = {}
        records = self.read(cr, uid, ids, ['id','type','tracking_type','uom_id'], context=context)
        for record in records:
            res[record['id']] = True
            if record['type'] == 'work_package' and record['tracking_type'] == 'units' and not record['uom_id']:
                res[record['id']] = False

        return reduce(lambda x, y: x and y, res.values())

    def _check_work_unit_no_task(self,cr,uid,ids,context=None):
        res = {}
        records = self.read(cr, uid, ids, ['type','tracking_type','progress','task_ids','work_record_ids'], context=context)
        for record in records:
            res[record['id']] = True
            if record['type'] == 'work_package' and record['tracking_type'] == 'units' and len(record['task_ids']):
                res[record['id']] = False
            if record['type'] == 'work_package' and record['tracking_type'] == 'tasks' and len(record['work_record_ids']):
                res[record['id']] = False
        return reduce(lambda x, y: x and y, res.values())

    def _check_no_task_finished(self,cr,uid,ids,context=None):
        task_ids = self.pool.get('project.task').search(cr, uid, [('wbs_item_id','=',ids)], context=context)
        records = self.read(cr, uid, ids, ['type','state','tracking_type','progress','task_ids','work_record_ids'], context=context)
        for record in records:
            if record['state'] == 'done':
                for task in self.pool.get('project.task').browse(cr, uid, task_ids, context):
                    if task['state'] != 'done':
                        return False
        return True

    def _check_weight_sibling(self, cr, uid, ids, context=None):
        is_valid_data = True
        for obj in self.browse(cr,uid,ids,context=None):
            if obj.parent_id and obj.state in ['open','done','pending']:#Checks siblings weight doesn't add up more than 100
                weight = 0
                for sibling in obj.parent_id.child_ids:
                    if obj.state != 'cancelled':
                        weight += sibling.weight
                if weight != 100:
                    is_valid_data = False
            elif obj.weight != 100 and obj.state != 'draft':
                is_valid_data = False
        return is_valid_data

    def _check_weight(self, cr, uid, ids, context=None):
        is_valid_data = True
        for obj in self.browse(cr,uid,ids,context=None):
            if obj.state == 'draft' and (obj.weight < 0 or obj.weight > 100):#Checks positive numbers from 0 to 100
                is_valid_data = False
            if obj.state != 'draft' and (obj.weight <= 0 or obj.weight > 100):#Checks positive numbers from 1 to 100
                is_valid_data = False
        return is_valid_data

    _constraints = [
        (_check_recursion, 'Error ! You cannot create recursive wbs items.', ['parent_id']),
        (_check_no_childs, 'Error ! A work package cannot have children.', ['type']),
        (_check_no_work_or_taks, 'Error ! a Deliverable cannot have neither unit tracking, tasks nor work_records.', ['type']),
        (_check_unit_measure_work_package, 'Error ! Please select unit of measure.', ['tracking_type']),
        (_check_work_unit_no_task, 'Error ! You cannot change tracking type.', ['tracking_type']),
        (_check_no_task_finished, 'Error ! You finish first the children tasks.', ['state']),
        (_check_weight, 'Error ! Weight must be between 1 and 100, 0 is valid in a draft', ['weight']),
        (_check_weight_sibling, 'Error ! Mine and my sibling\'s weight must add up to 100, also my children\'s weight must add up to 100', ['weight','state']),
    ]

    def child_get(self, cr, uid, ids):
        return [ids]

    def copy_data(self, cr, uid, id, default=None, context=None):
        if context is None:
            context = {}
        if default is None:
            default = {}

        record = self.read(cr,uid,id,['date_deadline','date_start'])
        deadline = False
        date_start = False

        if(record['date_deadline'] or record['date_start']) and 'reference_date' in context:
            reference_date = datetime.strptime(context['reference_date'], '%Y-%m-%d')
            if record['date_deadline']:
                template_deadline = datetime.strptime(record['date_deadline'], '%Y-%m-%d')
                template_reference_date = datetime(template_deadline.year, 1, 1)
                delta = template_deadline - template_reference_date
                deadline = reference_date + delta

            if record['date_start']:
                template_date_start = datetime.strptime(record['date_start'], '%Y-%m-%d')
                template_reference_date = datetime(template_date_start.year, 1, 1)
                delta = template_date_start - template_reference_date
                date_start = reference_date + delta

        context['active_test'] = False
        context['copy'] = True #Tasks doesn't add the (copy) text
        default.update({
            'message_ids':[],
            'date_start': date_start,
            'date_end': False,
            'date_deadline': deadline,
            'work_record_ids': []
        })
        return super(project_pmi_wbs_item, self).copy_data(cr, uid, id, default, context)

    def set_template(self, cr, uid, ids, context=None):
        item_ids = self.search(cr, uid, [('child_ids','child_of',ids)], context=context)
        return self.write(cr, uid, item_ids, {'state': 'template'}, context)

    def calculate_days(self,date1,date2):
        date_start = date(int(date1[0:4]), int(date1[5:7]), int(date1[8:10]))
        date_end = date(int(date2[0:4]), int(date2[5:7]), int(date2[8:10]))
        days = date_end - date_start
        return days.days

    def weight_assigned_by_duration(self, cr, uid, ids, context=None):
        for obj in self.browse(cr,uid,ids,context=None):
            weight_sum = 0.0
            weight = 0.0
            #realiza la sumatoria
            try:
                if obj.parent_id and obj.state in ['open','done','pending','draft']:
                    for sibling in obj.parent_id.child_ids:
                        if sibling.state != 'cancelled':
                            is_date = isinstance(sibling.date_start,date) and isinstance(sibling.date_end,date)
                            if is_date:
                                weight_sum += self.calculate_days(sibling.date_start, sibling.date_end)
                            else:
                                raise osv.except_osv('Error','Wrong data type')
                #calcula el %
                if obj.parent_id and obj.state in ['open','done','pending','draft']:
                    for sibling in obj.parent_id.child_ids:
                        if sibling.state != 'cancelled':
                            weight = (self.calculate_days(sibling.date_start, sibling.date_end) / weight_sum) * 100
                            self.write(cr, uid,sibling.id, {'weight': weight} , context)
            except Exception as e:
                raise osv.except_osv('Error calculating weight', str(e))

    def set_bulk_project(self, cr, uid, ids, context=None):
        item_ids = self.search(cr, uid, [('child_ids','child_of',ids)], context=context)
        reads = self.read(cr, uid, ids, ['phase_id','project_id'], context=context)
        for read in reads:
            if read['project_id']:
                if read['phase_id']:
                    self.write(cr, uid, item_ids, {'phase_id': read['phase_id'][0],'project_id': read['project_id'][0]}, context)
                else: 
                    self.write(cr, uid, item_ids, {'project_id': read['project_id'][0]}, context)
                for item in item_ids:
                    task_ids = self.pool.get('project.task').search(cr, uid, [('wbs_item_id','=',item)], context=context)
                    if read['phase_id']:
                        self.pool.get('project.task').write(cr, uid, task_ids, {'phase_id': read['phase_id'][0],'project_id': read['project_id'][0]}, context)
                    else:
                        self.pool.get('project.task').write(cr, uid, task_ids, {'project_id': read['project_id'][0]}, context)
            else:
                raise osv.except_osv('You must set a project first','Error')
        return True

    def set_draft(self, cr, uid, ids, context=None):
        item_ids = self.search(cr, uid, [('child_ids','child_of',ids)], context=context)
        return self.write(cr, uid, item_ids, {'state': 'draft'}, context)

    def set_open(self, cr, uid, ids, context=None):
        item_ids = self.search(cr, uid, [('child_ids','child_of',ids)], context=context)
        return self.write(cr, uid, item_ids, {'state': 'open'}, context)

    def set_pending(self, cr, uid, ids, context=None):
        item_ids = self.search(cr, uid, [('child_ids','child_of',ids)], context=context)
        return self.write(cr, uid, item_ids, {'state': 'pending'}, context)

    def set_done(self, cr, uid, ids, context=None):
        item_ids = self.search(cr, uid, [('child_ids','child_of',ids)], context=context)
        return self.write(cr, uid, item_ids, {'state': 'done'}, context)

    def set_weight_on(self, cr, uid, ids, context=None):
        item_ids = self.search(cr, uid, [('child_ids','child_of',ids)], context=context)
        return self.write(cr, uid, item_ids, {'use_weight': True}, context)

    def set_weight_off(self, cr, uid, ids, context=None):
        item_ids = self.search(cr, uid, [('child_ids','child_of',ids)], context=context)
        return self.write(cr, uid, item_ids, {'use_weight': False}, context)


project_pmi_wbs_item()

class project_pmi_wbs_work_record(osv.osv):
    _name = "project_pmi.wbs_work_record"
    _description = "WBS Item Work Record"
    _columns = {
        'name': fields.char('Work summary', size=128),
        'date': fields.datetime('Date', select="1"),
        'wbs_item_id': fields.many2one('project_pmi.wbs_item', 'Task', ondelete='cascade', required=True, select="1"),
        'quantity': fields.float('Quantity'),
        'user_id': fields.many2one('res.users', 'Done by', required=True, select="1"),
    }

    _defaults = {
        'user_id': lambda obj, cr, uid, context: uid,
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S')
    }

    _order = "date desc"
    def create(self, cr, uid, vals, *args, **kwargs):
        if 'quantity' in vals and (not vals['quantity']):
            vals['quantity'] = 0.00
        #TODO: Aplicar calculo de trabajo pendiente en el wbs item
        #if 'wbs_item_id' in vals:
        #    cr.execute('update project_task set remaining_hours=remaining_hours - %s where id=%s', (vals.get('hours',0.0), vals['task_id']))
        return super(project_pmi_wbs_work_record,self).create(cr, uid, vals, *args, **kwargs)

    def write(self, cr, uid, ids, vals, context=None):
        if 'quantity' in vals and (not vals['quantity']):
            vals['quantity'] = 0.00
        #TODO: Aplicar calculo de trabajo pendiente en el wbs item
        #if 'wbs_item_id' in vals:
        #    cr.execute('update project_task set remaining_hours=remaining_hours - %s where id=%s', (vals.get('hours',0.0), vals['task_id']))
        return super(project_pmi_wbs_work_record,self).write(cr, uid, ids, vals, context)

    def unlink(self, cr, uid, ids, *args, **kwargs):
        #TODO: Aplicar calculo de trabajo pendiente en el wbs item
        #for work in self.browse(cr, uid, ids):
        #    cr.execute('update project_task set remaining_hours=remaining_hours + %s where id=%s', (work.hours, work.task_id.id))
        return super(project_pmi_wbs_work_record,self).unlink(cr, uid, ids,*args, **kwargs)
