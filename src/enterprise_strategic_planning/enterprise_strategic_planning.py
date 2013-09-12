# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Instituto de Desarrollo Urbano (<http://www.idu.gov.co>). 
#    All Rights Reserved
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

class enterprise_strategic_planning_strategy(osv.osv):
    _name = "enterprise_strategic_planning.strategy"
    _inherit = ['mail.thread']
    _columns = {
        'name': fields.char('Name', size=255, required=True, select=True),
        'description': fields.text('Description'),
        'mission': fields.text('Mission',help="A Mission indicates the ongoing operational activity of the enterprise. The Mission describes what the business is or will be doing on a day-to-day basis. A Mission makes a Vision operative -- that is, it indicates the ongoing activity that makes the Vision a reality. A Mission is planned according to Strategies."),
        'vision': fields.text('Vision',help="A Vision describes the future state of the enterprise, without regard to how it is to be achieved."),
        'start_date': fields.date('Start Date', help="Date when the strategy start to be implemented in the organisation"),
        'end_date': fields.date('End Date', help="End Date when the strategy finishes in the organisation"),
        'active':fields.boolean('Active',help='Enable/Disable'),
        'state':fields.selection([('draft', 'Draft'),('open', 'In Progress'),('cancel', 'Cancelled'),('done', 'Done'),('pending', 'Pending')],'State'),
        'goal_ids': fields.one2many('enterprise_strategic_planning.goal','strategy_id','Objectives')
    }
    _defaults = {
        'active': True,
        'state': 'draft'
    }

enterprise_strategic_planning_strategy()

class enterprise_strategic_planning_goal(osv.osv):
    _name = "enterprise_strategic_planning.goal"
    _inherit = ['mail.thread']
    _columns = {
        'name': fields.char('Name', size=255, required=True, select=True),
        'description': fields.text('Description',help="A Goal is a statement about a state or condition of the enterprise to be brought about or sustained through appropriate Means. A Goal amplifies a Vision. That is, it indicates what must be satisfied continually to effectively attain the Vision."),
        'due_date': fields.date('Due Date', help="Due Date to achieve the goal"),
        'active':fields.boolean('Active',help='Enable/Disable'),
        'state':fields.selection([('draft', 'Draft'),('open', 'In Progress'),('cancel', 'Cancelled'),('done', 'Done'),('pending', 'Pending')],'State'),
        'strategy_id': fields.many2one('enterprise_strategic_planning.strategy','Strategy'),
        'objective_ids': fields.one2many('enterprise_strategic_planning.objective','goal_id','Objectives')
    }
    _defaults = {
        'active': True,
        'state': 'draft'
    }

enterprise_strategic_planning_goal()

class enterprise_strategic_planning_objective(osv.osv):
    _name = "enterprise_strategic_planning.objective"
    _inherit = ['mail.thread']
    _columns = {
        'name': fields.char('Name', size=255, required=True, select=True),
        'description': fields.text('Description',help="An Objective is a statement of an attainable, time-targeted, and measurable target that the enterprise seeks to meet in order to achieve its Goals."),
        'goal_id': fields.many2one('enterprise_strategic_planning.goal','Goal'),
        'due_date': fields.date('Due Date', help="Due Date to achieve the objective"),
        'active':fields.boolean('Active',help='Enable/Disable'),
        'state':fields.selection([('draft', 'Draft'),('open', 'In Progress'),('cancel', 'Cancelled'),('done', 'Done'),('pending', 'Pending')],'State'),
    }
    _defaults = {
        'active': True,
        'state': 'draft'
    }

enterprise_strategic_planning_objective()
