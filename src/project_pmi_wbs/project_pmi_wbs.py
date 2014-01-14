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

task()

class project_pmi_wbs_item(osv.osv):
    _name = "project_pmi.wbs_item"
    _inherit = ['mail.thread']
    _description = "WBS item part of WBS tree"

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

    def _progress_rate(self, cr, uid, ids, names, arg, context=None):
        child_parent = self._get_wbs_item_and_children(cr, uid, ids, context)
        # compute planned_hours, total_hours, effective_hours specific to each project
        cr.execute("""
            SELECT
                wbs_item.id, COALESCE(wbs_item.quantity, 0.0), COALESCE(SUM(wr.quantity), 0.0), wbs_item.type, wbs_item.tracking_type, COUNT(t.id), SUM(t.progress),wbs_item.state
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

        for id, planned, effective, type, tracking_type, task_count, task_progress, state in all_records:
            res[id]['type'] = type
            res[id]['state'] = state
            task_progress = task_progress or 0
            # add the values specific to id to all parent wbs_items of id in the result
            if res[id]['type'] == 'work_package' and tracking_type == 'tasks':
                planned += task_count * 100
                effective += task_progress
            res[id]['planned_quantity'] += planned
            res[id]['effective_quantity'] += effective

        # compute progress rates
        for id in sorted(child_parent.keys(), reverse=True):
            progress = 0.0
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
                    number = self._get_Values_Dictionary(child_parent,id)
                    if number > 0:
                        value *= number
                    res[id]['progress_rate'] += progress / value
                id = child_parent[id]
        return res

    def _get_Values_Dictionary(self,my_dictionary,my_value):
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
        'is_root_node': fields.boolean('Is a root node for the project WBS',help='Any project with a WBS can have several WBS Items, but one active WBS item as root node'),
        'code': fields.char('Code', size=20, required=True, select=True),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Name'),
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
        'date_deadline': fields.date('Deadline'),
        'date_start': fields.date('Starting Date'),
        'date_end': fields.date('Ending Date'),
        'excess_progress': fields.function(_progress_rate, multi="progress", string='Excess Progress', type='float', group_operator="avg",
             help="Total work quantity planned", store = {
                'project_pmi.wbs_item': (_get_wbs_item_and_parents, ['parent_id', 'child_ids','quantity','state'], 10),
                'project_pmi.wbs_work_record': (_get_wbs_item_from_work_records, ['wbs_item_id', 'quantity'], 20),
                'project.task': (_get_wbs_item_from_tasks, ['wbs_item_id', 'work_ids', 'remaining_hours', 'planned_hours','state'], 30),
            }
         ),
        'planned_quantity': fields.function(_progress_rate, multi="progress", string='Planned Quantity', type='float', group_operator="avg",
             help="Total work quantity planned", store = {
                'project_pmi.wbs_item': (_get_wbs_item_and_parents, ['parent_id', 'child_ids','quantity','state'], 10),
                'project_pmi.wbs_work_record': (_get_wbs_item_from_work_records, ['wbs_item_id', 'quantity'], 20),
                'project.task': (_get_wbs_item_from_tasks, ['wbs_item_id', 'work_ids', 'remaining_hours', 'planned_hours','state'], 30),
            }
         ),
        'effective_quantity': fields.function(_progress_rate, multi="progress", string='Effective Quantity', type='float', group_operator="avg",
             help="Percent of progress according to the total of work recorded.", store = {
                'project_pmi.wbs_item': (_get_wbs_item_and_parents, ['parent_id', 'child_ids','quantity','state'], 10),
                'project_pmi.wbs_work_record': (_get_wbs_item_from_work_records, ['wbs_item_id', 'quantity'], 20),
                'project.task': (_get_wbs_item_from_tasks, ['wbs_item_id', 'work_ids', 'remaining_hours', 'planned_hours','state'], 30),
            }
         ),
        'progress_rate': fields.function(_progress_rate, multi="progress", string='Progress', type='float', group_operator="avg",
             help="Percent of progress according to the total of work recorded.", store = {
                'project_pmi.wbs_item': (_get_wbs_item_and_parents, ['parent_id', 'child_ids','quantity','state'], 10),
                'project_pmi.wbs_work_record': (_get_wbs_item_from_work_records, ['wbs_item_id', 'quantity'], 20),
                'project.task': (_get_wbs_item_from_tasks, ['wbs_item_id', 'work_ids', 'remaining_hours', 'planned_hours','state'], 30),
            }
         ),
        'work_record_ids': fields.one2many('project_pmi.wbs_work_record', 'wbs_item_id', 'Work done'),
        'task_ids': fields.one2many('project.task', 'wbs_item_id', 'Tasks'),
    }
    _defaults = {
        'active': True,
        'state': 'draft',
        'code': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'project_pmi.wbs'),
        'project_id' : lambda self, cr, uid, context : context['project_id'] if context and 'project_id' in context else None #Set by default the project given in the context
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
        isValid = True
        type = self.read(cr, uid, ids, ['type'], context=context)
        child_parent = self._get_wbs_item_and_children(cr, uid, ids, context)
        if self._get_Values_Dictionary(child_parent, ids[0]) > 0:
            for record in type:
                if record['type'] == 'work_package':
                    isValid = False
        return isValid

    def _check_unit_measure_work_package(self,cr,uid,ids,context=None):
        type = self.read(cr, uid, ids, ['type','tracking_type','uom_id','progress'], context=context)
        for record in type:
            if record['type'] == 'work_package':
                if record['tracking_type'] == 'units':
                    if not record['uom_id']:
                        return False
        return True
  
    def _check_work_unit_no_task(self,cr,uid,ids,context=None):
        type = self.read(cr, uid, ids, ['type','tracking_type','uom_id','progress'], context=context)
        for record in type:
            if record['type'] == 'work_package':
                if record['tracking_type'] == 'units':
                    cr.execute('select count(*) from project_task where wbs_item_id IN %s',(tuple(ids),))
                    for row in cr.fetchall():
                        if (row[0] > 0):
                            return False
                if record['tracking_type'] == 'tasks':
                    cr.execute('select count(*) from project_pmi_wbs_work_record where wbs_item_id IN %s',(tuple(ids),))
                    for row in cr.fetchall():
                        if row[0] > 0:
                            return False
        return True

    _constraints = [
        (_check_recursion, 'Error ! You cannot create recursive deliverable.', ['parent_id']),
        (_check_no_childs, 'Error ! You cannot have childs.', ['type']),
        (_check_unit_measure_work_package, 'Error ! Please select unit of measure.', ['tracking_type']),
        (_check_work_unit_no_task, 'Error ! You cannot change tracking type.', ['tracking_type']),
    ]

    def child_get(self, cr, uid, ids):
        return [ids]

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
