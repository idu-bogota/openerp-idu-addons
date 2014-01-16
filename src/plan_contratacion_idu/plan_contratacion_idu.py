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
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv
from openerp import pooler
from openerp import SUPERUSER_ID

class plan_contratacion_idu_plan(osv.osv):
    _name = "plan_contratacion_idu.plan"
    def _total_pagos_plan(self, cr, uid, ids, name, args, context=None):
        res = {}
        if isinstance(ids, (list, tuple)) and not len(ids):
            return res
        if isinstance(ids, (long, int)):
            ids = [ids]
        records = self.browse(cr, uid, ids, context=context)
        res = {}
        for record in records:
            sumatoria = 0
            sumatoria_presupuesto = 0
            res[record['id']] = {}
            for pago in record.item_ids:
                sumatoria += pago.total_pagos_programados
                sumatoria_presupuesto += pago.presupuesto
            res[record['id']]['total_pagos_presupuestado_plan'] = sumatoria_presupuesto
            res[record['id']]['total_pagos_programados_plan'] = sumatoria
            res[record['id']]['total_rezago_plan'] = sumatoria_presupuesto - sumatoria
        return res

    _columns = {
        'name': fields.char('Nombre', size=255, required=True, select=True),
        'state':fields.selection([('draft', 'Draft'),('open', 'In Progress'),('cancel', 'Cancelled'),('done', 'Done'),('pending', 'Pending')],'State', required=True),
        'active':fields.boolean('Activo'),
        'item_ids': fields.one2many('plan_contratacion_idu.item', 'plan_id', 'Items Plan de Contratacion'),
        'name_items':fields.one2many('plan_contratacion_idu.item', 'name', 'Items Plan de Contratacion'),
        'total_pagos_presupuestado_plan': fields.function(_total_pagos_plan, type='float', multi="total_pagos_programados", string='Total Presupuestado', digits_compute=dp.get_precision('Account'),
             store={
             }),
        'total_pagos_programados_plan': fields.function(_total_pagos_plan, type='float', multi="total_pagos_programados", string='Total Pagos Programados', digits_compute=dp.get_precision('Account'),
             store={
             }),
        'total_rezago_plan': fields.function(_total_pagos_plan, type='float', multi="total_pagos_programados", string='Total Rezago', digits_compute=dp.get_precision('Account'),
             store={
             }),
    }
    _sql_constraints =[
        ('unique_name','unique(name)','El año del plan debe ser único')
    ]
     
    _defaults = {
        'active': True,
        'state': 'draft'
    }

plan_contratacion_idu_plan()

class plan_contratacion_idu_item(osv.osv):
    _name = "plan_contratacion_idu.item"

    def _total_pagos_programados(self, cr, uid, ids, name, args, context=None):
        res = {}
        if isinstance(ids, (list, tuple)) and not len(ids):
            return res
        if isinstance(ids, (long, int)):
            ids = [ids]
        records = self.browse(cr, uid, ids, context=context)
        res = {}
        for record in records:
            sumatoria = 0
            res[record['id']] = {}
            for pago in record.plan_pagos_item_ids:
                sumatoria += pago.valor
            res[record['id']]['total_pagos_programados'] = sumatoria
            res[record['id']]['presupuesto_rezago'] = record.presupuesto - sumatoria
            res[record['id']]['total_programado_rezago'] = sumatoria + record.presupuesto_rezago
        return res

    def _get_plan_item_from_pago_records(self, cr, uid, pago_ids, context=None):
        """
        Retorna los IDs del plan_item a ser recalculados cuando cambia un pago_item
        """
        pago_records = self.pool.get('plan_contratacion_idu.plan_pagos_item').browse(cr, uid, pago_ids, context=context)
        plan_item_ids = [pago.plan_contratacion_item_id.id for pago in pago_records if pago.plan_contratacion_item_id]
        return plan_item_ids

    _columns = {
        'dependencia': fields.many2one('hr.department','Dependencia', select=True, ondelete='cascade'),
        'description': fields.text('Objeto Contractual', select=True),
        'name': fields.many2one('plan_contratacion_idu.plan','Plan contractual', select=True, ondelete='cascade'),
        'fuente': fields.many2one('plan_contratacion_idu.fuente','Fuente de Financiación', select=True, ondelete='cascade'),
        'state':fields.selection([('aprobado', 'Por radicar'),('radicado', 'Radicado'),('suscrito', 'Contrato suscrito'),('ejecucion', 'En ejecución'),
                                  ('ejecutado', 'Ejecutado'), ('no_realizado', 'No realizado')],'State', required=True),
        'fecha_radicacion': fields.date ('Fecha Radicacion en DTPS y/o DTGC', required=True, select=True),
        'fecha_crp': fields.date ('Fecha Programada CRP', required=True, select=True, help="CRP es Certificado Registro Presupuestal"),
        'fecha_acta_inicio': fields.date ('Fecha Aprobación Acta de Inicio', required=True, select=True),
        'plan_id': fields.many2one('plan_contratacion_idu.plan','Plan contractual', select=True, ondelete='cascade'),
        'clasificacion_id': fields.many2one('plan_contratacion_idu.clasificador_proyectos','Clasificación Proyecto', select=True, ondelete='cascade'),
        'presupuesto': fields.integer ('Presupuesto', required=True, select=True),
        'plazo_de_ejecucion': fields.integer ('Plazo de Ejecución', required=True, select=True, help="Tiempo estimado en meses"),
        'unidad_meta_fisica': fields.many2one('product.uom','Unidad Meta Física', select=True, ondelete='cascade'),
        'cantidad_meta_fisica': fields.integer ('Cantidad Metas Físicas'),
        'localidad': fields.char ('Localidad', size=255),
        'tipo_proceso': fields.selection([('nuevo', 'Contrato Nuevo'),('adicion', 'Adición'),('reconocimiento', 'Reconocimiento a Contrato'),
                                          ('sentencias', 'Sentencias'),('orden', 'Orden de Servicio'), ('psp', 'PSP'), ('comisiones', 'Comisiones y Gravamen Financiero'),
                                          ('compensacion', 'Compensación Social'),('adquisicion', 'Adquisición Predial')],'Proceso', required=True),
        'tipo_proceso_seleccion': fields.selection([('licitacion_publica', 'Licitación Pública'),('concurso_meritos_abierto', 'Concurso de Méritos Abierto'),
                                                    ('concurso_meritos_precalificacion', 'Concurso de Méritos con Precalificación'),
                                                    ('seleccion_abreviada_subasta_inversa', 'Selección Abreviada Susbasta Inversa'),
                                                    ('seleccion_abreviada_menor_cuantia', 'Selección Abreviada Menor Cuantia'), 
                                                    ('seleccion_abreviada_minima_cuantia', 'Selección Abreviada Mínima Cuantia'),
                                                    ('contratacion_directa', 'Contratación Directa'),('na', 'NA')],'Tipo de Proceso de Selección', required=True),
        'plan_pagos_item_ids': fields.one2many('plan_contratacion_idu.plan_pagos_item','plan_contratacion_item_id', 'Planificacion de Pagos', select=True, ondelete='cascade'),
        'total_pagos_programados': fields.function(_total_pagos_programados, type='float', multi="presupuesto", string='Total pagos programados', digits_compute=dp.get_precision('Account'),
             store={
                'plan_contratacion_idu.item': (lambda self, cr, uid, ids, c={}: ids, ['plan_pagos_item_ids', 'presupuesto'], 10),
                'plan_contratacion_idu.plan_pagos_item': (_get_plan_item_from_pago_records, ['valor', 'plan_contratacion_item_id'], 20),
            }),
        'presupuesto_rezago': fields.function(_total_pagos_programados, type='float', multi="presupuesto", string='Rezago', digits_compute=dp.get_precision('Account'),
             store={
                'plan_contratacion_idu.item': (lambda self, cr, uid, ids, c={}: ids, ['plan_pagos_item_ids', 'presupuesto'], 10),
                'plan_contratacion_idu.plan_pagos_item': (_get_plan_item_from_pago_records, ['valor', 'plan_contratacion_item_id'], 20),
            }),
        'total_programado_rezago': fields.function(_total_pagos_programados, type='float', multi="presupuesto", string='Total', digits_compute=dp.get_precision('Account'),
             store={
                'plan_contratacion_idu.item': (lambda self, cr, uid, ids, c={}: ids, ['plan_pagos_item_ids', 'presupuesto'], 10),
                'plan_contratacion_idu.plan_pagos_item': (_get_plan_item_from_pago_records, ['valor', 'plan_contratacion_item_id'], 20),
            }),
    }

    _defaults = {
        'state': 'aprobado'
    }

    def onchange_plan_pagos_item_ids(self, cr, uid, ids, pagos_ids, context=None):
        context = context or {}
        pagos_pool = self.pool.get('plan_contratacion_idu.plan_pagos_item')
        if not pagos_ids:
            pagos_ids = []
        sumatoria = 0
        res = {
                'total_pagos_programados': 0,
                'presupuesto_rezago': 0,
        }
        pagos_ids = resolve_o2m_operations(cr, uid, pagos_pool, pagos_ids, ['valor'], context)
        if ids:
            plan_item = self.read(cr, uid, ids[0], ['presupuesto'], context=context)
            for pago in pagos_ids:
                sumatoria += pago.get('valor',0.0)
            res = {
                'total_pagos_programados': sumatoria,
                'presupuesto_rezago': plan_item['presupuesto'] - sumatoria,
            }
        return {
            'value': res
        }

    def item_estudios_previos(self, cr, uid, ids, plan_items, context=None):
        self.write(cr, uid, ids, {"state": "aprobado"})

    def item_radicado(self, cr, uid, ids, plan_items, context=None):
        self.write(cr, uid, ids, {"state": "radicado"})

    def item_no_realizado(self, cr, uid, ids, plan_items, context=None):
        self.write(cr, uid, ids, {"state": "no_realizado"})
    
    def item_suscrito(self, cr, uid, ids, plan_items, context=None):
        self.write(cr, uid, ids, {"state": "suscrito"})

    def item_ejecucion(self, cr, uid, ids, plan_items, context=None):
        self.write(cr, uid, ids, {"state": "ejecucion"})
        
    def item_ejecutado(self, cr, uid, ids, plan_items, context=None):
        self.write(cr, uid, ids, {"state": "ejecutado"})

    def subscribe(self, cr, uid, ids, *args):
        obj_action = self.pool.get('ir.actions.act_window')
        obj_model = self.pool.get('plan_contratacion_idu.plan.data')
        #start Loop
        for thisrule in self.browse(cr, uid, ids):
            obj = self.pool.get(thisrule.plan_id.model)
            if not obj:
                """except_osv"""
                raise osv.osv(
                        _('WARNING: audittrail is not part of the pool'),
                        _('Change audittrail depends -- Setting rule as DRAFT'))
                self.write(cr, uid, [thisrule.id], {"state": "aprobado"})
            val = {
                 "name": 'View Log',
                 "res_model": 'audittrail.log',
                 "src_model": thisrule.plan_id.model,
                 "domain": "[('plan_id','=', " + str(thisrule.plan_id.id) + "), ('res_id', '=', active_id)]"
            }
            action_id = obj_action.create(cr, SUPERUSER_ID, val)
            self.write(cr, uid, [thisrule.id], {"state": "radicado", "action_id": action_id})
            keyword = 'client_action_relate'
            value = 'ir.actions.act_window,' + str(action_id)
            res = obj_model.ir_set(cr, SUPERUSER_ID, 'action', keyword, 'View_log_' + thisrule.plan_id.model, [thisrule.plan_id.model], value, replace=True, isobject=True, xml_id=False)
        return True

    def unsubscribe(self, cr, uid, ids, *args):
        obj_action = self.pool.get('ir.actions.act_window')
        ir_values_obj = self.pool.get('ir.values')
        value=''
        #start Loop
        for thisrule in self.browse(cr, uid, ids):
            if thisrule.id in self.__functions:
                for function in self.__functions[thisrule.id]:
                    setattr(function[0], function[1], function[2])
            w_id = obj_action.search(cr, uid, [('name', '=', 'View Log'), ('res_model', '=', 'audittrail.log'), ('src_model', '=', thisrule.plan_id.model)])
            if w_id:
                obj_action.unlink(cr, SUPERUSER_ID, w_id)
                value = "ir.actions.act_window" + ',' + str(w_id[0])
            val_id = ir_values_obj.search(cr, uid, [('model', '=', thisrule.plan_id.model), ('value', '=', value)])
            if val_id:
                ir_values_obj = pooler.get_pool(cr.dbname).get('ir.values')
                res = ir_values_obj.unlink(cr, uid, [val_id[0]])
            self.write(cr, uid, [thisrule.id], {"state": "aprobado"})
        #End Loop
        return True
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

class plan_contratacion_idu_plan_pagos_item(osv.osv):
    _name = "plan_contratacion_idu.plan_pagos_item"
    _columns = {
        'mes': fields.selection([(1,'Enero'), (2,'Febrero'), (3,'Marzo'), (4,'Abril'),
            (5,'Mayo'), (6,'Junio'), (7,'Julio'), (8,'Agosto'), (9,'Septiembre'),
            (10,'Octubre'), (11,'Noviembre'), (12,'Diciembre')], 'Mes', required=True),
        'valor': fields.integer('Valor', required=True, select=True),
        'plan_contratacion_item_id': fields.many2one('plan_contratacion_idu.item','Item Plan de Contratacion', select=True, ondelete='cascade'),
    }

    _sql_constraints =[
        ('unique_mes','unique(mes,plan_contratacion_item_id)','El mes debe ser único')
    ]

plan_contratacion_idu_plan_pagos_item()

def resolve_o2m_operations(cr, uid, target_osv, operations, fields, context):
    results = []
    for operation in operations:
        result = None
        if not isinstance(operation, (list, tuple)):
            result = target_osv.read(cr, uid, operation, fields, context=context)
        elif operation[0] == 0:
            # may be necessary to check if all the fields are here and get the default values?
            result = operation[2]
        elif operation[0] == 1:
            result = target_osv.read(cr, uid, operation[1], fields, context=context)
            if not result: result = {}
            result.update(operation[2])
        elif operation[0] == 4:
            result = target_osv.read(cr, uid, operation[1], fields, context=context)
        if result != None:
            results.append(result)
    return results