# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2013 Instituto de Desarrollo Urbano (<http://www.idu.gov.co>). All Rights Reserved
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields

class project_pmi_wbs_wizard_create_wbs(osv.osv_memory):
    _name = 'project_pmi_wbs.wizard.create_wbs'
    _description = 'Create a WBS for a project'

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'project_id':fields.many2one('project.project', 'Project', required=True, domain="[('state', 'in', ['draft','open','pending'])]"),
        'parent_project_id': fields.integer(string="Parent Project ID", required=False),
        'parent_project_wbs_count': fields.integer(string="Parent Project WBS count", required=False),
        'parent_wbs_id': fields.many2one('project_pmi.wbs_item', 'WBS Parent', required=False),
        'wbs_template_id': fields.many2one('project_pmi.wbs_item', 'WBS template', required=False, domain="[('state', '=', 'template')]"),
        'reference_date': fields.date('WBS start date', help="Used as a reference to set the deadline"),
        'link_to_parent': fields.boolean("Link new WBS to parent's project WBS?"),
    }

    def default_get(self, cr, uid, fields, context=None):
        """
Get default values to fill the form
"""
        res = super(project_pmi_wbs_wizard_create_wbs, self).default_get(cr, uid, fields, context=context)
        if 'active_id' in context:
            project = self.pool.get('project.project').browse(cr, uid, context['active_id'], context)
            parent_id = project._get_project_and_parents()[0]
            parent = self.pool.get('project.project').browse(cr, uid, parent_id, context)
            res.update({'project_id': project.id, 'name': project.name, 'parent_project_id': parent_id, 'parent_project_wbs_count': len(parent.wbs_item_ids)})

        return res

    def action_create(self, cr, uid, ids, context=None):
        project_ids = context and context.get('active_ids', False)
        project_table = self.pool.get('project.project')
        wbs_table = self.pool.get('project_pmi.wbs_item')

        form_object_id = ids and ids[0] or False
        form_object = self.browse(cr, uid, form_object_id, context=context)

        for project in project_table.browse(cr, uid, project_ids, context=context):
            data = {
                'project_id': project.id,
                'name': form_object.name.strip(),
                'type': 'deliverable',
                'weight': 100,
                'active': True,
                'state': 'draft',
                'is_root_node': True,
            }
            if (form_object.link_to_parent):
                data['parent_id'] = form_object.parent_wbs_id.id

            if(form_object.wbs_template_id):
                context.update({'copy':True, 'reference_date':form_object.reference_date})
                wbs_table.copy(cr, uid, form_object.wbs_template_id.id, default = data, context=context)
            else:
                wbs_table.create(cr, uid, data, context)

        return {'type': 'ir.actions.act_window_close'}

project_pmi_wbs_wizard_create_wbs()