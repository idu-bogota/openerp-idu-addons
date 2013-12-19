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
        'wbs_ids': fields.one2many('project_pmi.wbs_item', 'project_id', string='Work Breakdown Structure'),
        'wbs_items_count': fields.function(_wbs_item_count, type='integer', string="WBS items count", store=True),
    }

project()

#TODO: Adicionar vista Gantt a WBS
#TODO: Validar que un work package no tenga child_ids
#TODO: Validar work_package tiene unidad de medida
#TODO: Validar que los pesos de un mismo nivel den el 100%
#TODO: Adicionar vista kamban para los work_packages y adicionar link en la vista kanban de proyectos 
#TODO: Relacionar Tareas con Work Packages
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
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
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

    #FIXME: No hacer queries en loop para evitar problemas de rendimiento
    def _progress_rate(self, cr, uid, ids, names, arg, context=None):
        # compute progress rates
        res = {}
        for id in ids:
            res[id] = {}
            total_work = 0
            wbs_item = self.pool.get('project_pmi.wbs_item').browse(cr, uid, id, context=context)
            item_ids = self.pool.get('project_pmi.wbs_work_record').search(cr, uid, [('wbs_item_id', '=', id)], context=context)
            for item in self.pool.get('project_pmi.wbs_work_record').browse(cr, uid, item_ids, context):
                total_work += item.quantity
            if wbs_item.quantity:
                res[id]['progress_rate'] = round(100.0 * total_work / wbs_item.quantity, 2)

        return res

    _columns = {
        'project_id': fields.many2one('project.project','Project'),
        'is_root_node': fields.boolean('Is a root node for the project WBS',help='Any project with a WBS can have several WBS Items, but one active WBS item as root node'),
        'code': fields.char('Code', size=20, required=True, select=True),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Name'),
        'name': fields.char('Name', size=255, required=True, select=True),
        'type': fields.selection([('work_package', 'Work Package'),('deliverable', 'Deliverable')],'Deliverable Type', required=True),
        'weight': fields.float('Weight'),
        'description': fields.text('Description'),
        'active':fields.boolean('Active',help='Enable/Disable'),
        'state':fields.selection([('draft', 'Draft'),('open', 'In Progress'),('cancel', 'Cancelled'),('done', 'Done'),('pending', 'Pending'),('template', 'Template')],'State'),
        'quantity': fields.float('Quantity'),
        'uom_id': fields.many2one('product.uom', 'Unit of Measure', help="Default Unit of Measure used"),
        'parent_id': fields.many2one('project_pmi.wbs_item','Parent Deliverable', select=True, ondelete='cascade'),
        'child_ids': fields.one2many('project_pmi.wbs_item', 'parent_id', string='Child Deliverables'),
        'sequence': fields.integer('Sequence', select=True, help="Gives the sequence order when displaying a list."),
        'parent_left': fields.integer('Left Parent', select=1),
        'parent_right': fields.integer('Right Parent', select=1),
        'color': fields.integer('Color Index'),
        'date_deadline': fields.date('Deadline',select=True),
        'date_start': fields.date('Starting Date',select=True),
        'date_end': fields.date('Ending Date',select=True),
        'progress_rate': fields.function(_progress_rate, multi="progress", string='Progress', type='float', group_operator="avg", 
             help="Percent of progress according to the total of work recorded.", store=True),
        'work_record_ids': fields.one2many('project_pmi.wbs_work_record', 'wbs_item_id', 'Work done'),
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

    _constraints = [
        (_check_recursion, 'Error ! You cannot create recursive deliverable.', ['parent_id'])
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
