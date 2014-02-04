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

class project(osv.osv):
    _name = "project.project"
    _inherit = "project.project"
    
    _columns = {
        'portfolio_ids': fields.many2many(
            'project_pmi.portfolio',
            'project_pmi_portfolio_project_rel',
            'project_id',
            'portfolio_id',
            'Portfolios'),
        'program_ids': fields.many2many(
            'project_pmi.program',
            'project_pmi_program_project_rel',
            'project_id',
            'program_id',
            'Programs'),
        # TODO: Hacer que se restrinjan el listado de objetivos al goal del portafolio
        'strategic_objective_id': fields.many2one('enterprise_strategic_planning.objective','Strategic Objective'),
    }

project()

class project_pmi_portfolio(osv.osv):
    _name = "project_pmi.portfolio"
    _inherit = ['mail.thread']
    _description = "Handles a portfolio tree"

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

    def _project_count(self, cr, uid, ids, prop, unknow_none, context=None):
        records = self.browse(cr, uid, ids, context=context)
        res = []
        for record in records:
            res.append((record.id, len(record.project_ids)))
        return dict(res)

    _columns = {
        'name': fields.char('Name', size=255, required=True, select=True),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Name'),
        'description': fields.text('Description',help="Description about this portfolio"),
        'parent_id': fields.many2one('project_pmi.portfolio','Parent portfolio', select=True, ondelete='cascade'),
        'child_id': fields.one2many('project_pmi.portfolio', 'parent_id', string='Child Portfolios'),
        'sequence': fields.integer('Sequence', select=True, help="Gives the sequence order when displaying a list."),
        'parent_left': fields.integer('Left Parent', select=1),
        'parent_right': fields.integer('Right Parent', select=1),
        'project_ids': fields.many2many(
            'project.project',
            'project_pmi_portfolio_project_rel',
            'portfolio_id',
            'project_id',
            'Projects'),
        'strategic_goal_id': fields.many2one('enterprise_strategic_planning.goal','Strategic Goal'),
        'active':fields.boolean('Active',help='Enable/Disable'),
        'state':fields.selection([('draft', 'Draft'),('open', 'In Progress'),('cancel', 'Cancelled'),('done', 'Done'),('pending', 'Pending')],'State'),
        'project_count': fields.function(_project_count, type="integer", string='Project Count'),
    }
    _defaults = {
        'active': True,
        'state': 'draft'
    }
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'sequence, name'
    _order = 'parent_right DESC'

    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from project_pmi_portfolio where id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error ! You cannot create recursive portfolios.', ['parent_id'])
    ]
    def child_get(self, cr, uid, ids):
        return [ids]

project_pmi_portfolio()

class project_pmi_program(osv.osv):
    _name = "project_pmi.program"
    _inherit = ['mail.thread']
    _description = "Handles a program tree"

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

    def _project_count(self, cr, uid, ids, prop, unknow_none, context=None):
        records = self.browse(cr, uid, ids, context=context)
        res = []
        for record in records:
            res.append((record.id, len(record.project_ids)))
        return dict(res)

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _columns = {
        'name': fields.char('Name', size=255, required=True, select=True),
        'description': fields.text('Description',help="Description about this program"),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Name'),
        'parent_id': fields.many2one('project_pmi.program','Parent Program', select=True, ondelete='cascade'),
        'child_id': fields.one2many('project_pmi.program', 'parent_id', string='Child programs'),
        'sequence': fields.integer('Sequence', select=True, help="Gives the sequence order when displaying a list."),
        'parent_left': fields.integer('Left Parent', select=1),
        'parent_right': fields.integer('Right Parent', select=1),
        'project_ids': fields.many2many(
            'project.project',
            'project_pmi_program_project_rel',
            'program_id',
            'project_id',
            'Projects'),
        'project_count': fields.function(_project_count, type="integer", string='Project Count'),
        'active':fields.boolean('Active',help='Enable/Disable'),
        'state':fields.selection([('draft', 'Draft'),('open', 'In Progress'),('cancel', 'Cancelled'),('done', 'Done'),('pending', 'Pending')],'State'),
    }
    _defaults = {
        'active': True,
        'state': 'draft'
    }
    _parent_name = "parent_id"
    _parent_store = True
    _parent_order = 'sequence, name'
    _order = 'parent_right DESC'

    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from project_pmi_program where id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error ! You cannot create recursive programs.', ['parent_id'])
    ]
    def child_get(self, cr, uid, ids):
        return [ids]

project_pmi_program()

class enterprise_strategic_planning_goal(osv.osv):
    _name = "enterprise_strategic_planning.goal"
    _inherit = ['enterprise_strategic_planning.goal']
    _columns = {
        'portfolio_ids': fields.one2many('project_pmi.portfolio', 'strategic_goal_id', string='Related Portfolios'),
    }

enterprise_strategic_planning_goal()

class enterprise_strategic_planning_objective(osv.osv):
    _name = "enterprise_strategic_planning.objective"
    _inherit = ['enterprise_strategic_planning.objective']
    _columns = {
        'project_ids': fields.one2many('project.project', 'strategic_objective_id', string='Related Projects'),
    }