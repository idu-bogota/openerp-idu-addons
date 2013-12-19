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
        'etapa_id': fields.many2one('project_idu.etapa','Etapa', select=True),
        #Punto de inversion
        #Centro de costo
        #Fuente de Financiacion
    }

project()

class task(osv.osv):
    _name = "project.task"
    _inherit = "project.task"

    _columns = {
        'etapa_id': fields.related(
            'project_id',
            'etapa_id',
            type="many2one",
            relation="project_idu.etapa",
            string="Etapa del Proyecto",
            store=True)
    }

task()

class project_idu_etapa(osv.osv):
    _name = "project_idu.etapa"

    _columns = {
        'name': fields.char('Name', size=255, required=True, select=True),
    }

project_idu_etapa()