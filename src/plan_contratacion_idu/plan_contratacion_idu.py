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

class plan_contratacion_idu_plan(osv.osv):
    _name = "plan_contratacion_idu.plan"
    _columns = {
        'name': fields.char('Nombre', size=255, required=True, select=True),
        'state':fields.selection([('draft', 'Draft'),('open', 'In Progress'),('cancel', 'Cancelled'),('done', 'Done'),('pending', 'Pending')],'State', required=True),
        'active':fields.boolean('Activo'),
        'item_ids': fields.one2many('plan_contratacion_idu.item', 'plan_id', 'Items Plan de Contratacion'),
    }
    _defaults = {
        'active': True,
        'state': 'draft'
    }

plan_contratacion_idu_plan()

class plan_contratacion_idu_item(osv.osv):
    _name = "plan_contratacion_idu.item"
    _columns = {
        'dependencia': fields.many2one('hr.department','Dependencia', select=True, ondelete='cascade'),
        'description': fields.text('Objeto Contractual'),
        'name': fields.char('Nombre', size=255, required=True, select=True),
        'fuente': fields.many2one('plan_contratacion_idu.fuente','Fuente de Financiación', select=True, ondelete='cascade'),
        'state':fields.selection([('aprobado', 'Por radicar'),('radicado', 'Radicado'),('suscrito', 'Contrato suscrito'),('ejecucion', 'En ejecución'),('ejecutado', 'Ejecutado'), ('no_realizado', 'No realizado')],'State', required=True),
        'active':fields.boolean('Activo'),
        'date': fields.date ('Fecha Radicacion en DTPS y/o DTGC'),
        'plan_id': fields.many2one('plan_contratacion_idu.plan','Plan contractual', select=True, ondelete='cascade'),
        'clasificacion_id': fields.many2one('plan_contratacion_idu.clasificador_proyectos','Clasificación Proyecto', select=True, ondelete='cascade'),
        'presupuesto': fields.integer ('Presupuesto', required=True, select=True),
        'unidad_mf': fields.char ('Unidad Metas Físicas', size=255),
        'cantidad_mf': fields.integer ('Cantidad Metas Físicas'),
        'localidad': fields.char ('Localidad', size=255),
    }
    _defaults = {
        'active': True,
        'state': 'draft'
    }
plan_contratacion_idu_item()


class plan_contratacion_idu_clasificador_proyectos(osv.osv):
    _name = "plan_contratacion_idu.clasificador_proyectos"
    _description = "Clasificación de los proyectos"
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
    _columns = {
        'name': fields.char('Nombre', size=255, required=True, select=True),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Nombre'),
        'parent_id': fields.many2one('plan_contratacion_idu.clasificador_proyectos','Clasificación padre', select=True, ondelete='cascade'),
        'child_ids': fields.one2many('plan_contratacion_idu.clasificador_proyectos', 'parent_id', string='Clasificaciones hijas'),
        'sequence': fields.integer('Sequence', select=True, help="Secuencia para el ordenamiento en las listas"),
        'parent_left': fields.integer('Left Parent', select=1),
        'parent_right': fields.integer('Right Parent', select=1),
        'active':fields.boolean('Active',help='Activo/Inactivo'),
        'item_ids': fields.one2many('plan_contratacion_idu.item', 'clasificacion_id', 'Items Plan de Contratacion'),
    }
    _defaults = {
        'active': True,
    }
    def _check_recursion(self, cr, uid, ids, context=None):
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from plan_contratacion_idu_clasificador_proyectos where id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True
    _constraints = [
        (_check_recursion, 'Error ! No puede crear clasificaciones recursivas.', ['parent_id']),
    ]
plan_contratacion_idu_clasificador_proyectos()

class plan_contratacion_idu_fuente(osv.osv):
    _name = "plan_contratacion_idu.fuente"
    _columns = {
        'abreviado': fields.char  ('Abreviado', size=10, required=True, select=True),
        'name': fields.char('Nombre', size=255, required=True, select=True),
    }
plan_contratacion_idu_fuente()