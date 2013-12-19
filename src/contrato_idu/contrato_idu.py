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

class contrato_idu(osv.osv):
    _name = "contrato_idu.contrato"

    def _get_name(self,cr,uid,ids,fieldname,arg,context=None):
        """Get Name """
        res = {}
        for contrato in self.browse(cr, uid, ids, context = context):
                res[contrato.id] = ''
                if(contrato.code):
                    res[contrato.id] = "{0} - ".format(contrato.code)
                res[contrato.id] = "{0}{1}".format(res[contrato.id], contrato.type)
        return  res

    _columns = {
        'name':fields.function(_get_name,type='char',string='Contrato',method=True),
        'code': fields.char('Número de contrato en SIAC', size=255, select=True),
        'type':fields.selection([('interventoria', 'Interventoria'),('obra', 'Obra')],'Tipo', required=True, ),
        'description': fields.text('Descripción'),
        'state':fields.selection([('draft', 'Draft'),('open', 'In Progress'),('cancel', 'Cancelled'),('done', 'Done'),('pending', 'Pending')],'State', required=True),
        'state_siac':fields.selection([('ninguno', 'No Creado')],'Estado SIAC'),
        'active':fields.boolean('Activo'),
        #TODO: Solo projects_ids y que sea funcional indicando los proyectos, o colocar relacion many2many con proyectos
        'project_ids': fields.one2many('project.project', 'contrato_id', string='Proyectos'),
        'project_interventoria_ids': fields.one2many('project.project', 'contrato_interventoria_id', string='Proyectos'),
    }

    _defaults = {
        'active': True,
        'state': 'draft'
    }
