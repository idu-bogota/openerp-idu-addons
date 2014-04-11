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
from suds.client import Client
from stone_erp_idu import stone_client_ws
from openerp import SUPERUSER_ID
from contrato_idu import siac_ws
from datetime import date

wsdl_url_orfeo='http://gesdocpru/desarrollo/webServices/orfeoIduWebServices.php?wsdl'
client = Client(wsdl_url_orfeo)
orfeo_existe_radicado = getattr(client.service, 'OrfeoWs.existeRadicado')
orfeo_fecha_radicado = getattr(client.service, 'OrfeoWs.fechaRadicado')

class plan_contratacion_idu_plan(osv.osv):
    _name = "plan_contratacion_idu.plan"

    def _get_name(self, cr, uid, ids, field, args, context=None):
        res = {}
        records = self.pool.get('plan_contratacion_idu.plan').read(cr, uid, ids, ['vigencia'])
        for record in records:
            res[record['id']] = "Plan Vigencia {0}".format(record['vigencia'])
        return res

    def _get_currency(self, cr, uid, ids, field, args, context=None):
        res = {}
        company_id = self.pool.get('res.company')._company_default_get(cr, SUPERUSER_ID, 'plan_contratacion_idu.plan', context=context)
        company = self.pool.get('res.company').read(cr, SUPERUSER_ID, company_id, ['currency_id'])
        currency_id = company['currency_id'][0]
        for plan_id in ids:
            res[plan_id] = currency_id
        return res

    def _total_pagos_plan(self, cr, uid, ids, name, args, context=None):
        res = {}
        if isinstance(ids, (list, tuple)) and not len(ids):
            return res
        if isinstance(ids, (long, int)):
            ids = [ids]
        plan_item_pool = self.pool.get('plan_contratacion_idu.item')
        item_ids = plan_item_pool.search(cr, SUPERUSER_ID,
              [('plan_id','in',ids),'!' ,('state','in',('solicitud_cambio','no_realizado'))],
              context=context,
        )
        for record in plan_item_pool.browse(cr, SUPERUSER_ID, item_ids, context=context):
            plan_id = record.plan_id.id
            if not plan_id in res:
                res[plan_id] = {'total_pagos_presupuestado_plan':0,
                                'total_pagos_programados_plan':0,
                                'total_rezago_plan':0}
            res[plan_id]['total_pagos_presupuestado_plan'] += record.presupuesto
            for pago in record.plan_pagos_item_ids:
                res[plan_id]['total_pagos_programados_plan'] += pago.valor
            res[plan_id]['total_rezago_plan'] = res[plan_id]['total_pagos_presupuestado_plan'] - res[plan_id]['total_pagos_programados_plan']
        return res

    def _get_plan_ids_from_items (self, cr, uid, ids, context=None):
        """
        Retorna IDs del plan_item modificados
        """
        records = self.pool.get('plan_contratacion_idu.item').browse(cr, SUPERUSER_ID, ids, context=context)
        plan_item_ids = [record.plan_id.id for record in records if record.id]
        return plan_item_ids

    _columns = {
        'name': fields.function(_get_name,
             type='char',
             string='Nombre',
             readonly=True,
             store= True,
        ),
        'vigencia': fields.char('Vigencia', required=True, select=True),
        'state':fields.selection([('inicial', 'Inicial'),('en_ejecucion', 'Ejecución'),
             ('finalizado', 'Finalizado')],
             'State',
             required=True
         ),
        'active':fields.boolean('Activo'),
        'open_close_plan':fields.boolean('Abierto', readonly=True),
        'item_ids': fields.one2many('plan_contratacion_idu.item', 'plan_id', 'Items Plan de Contratacion'),
        'version': fields.integer('Versión',
             help="Versión del archivo para exportar, conteo de versiones del plan",
             readonly=True),
        'currency_id': fields.function(_get_currency,
             type='many2one',
             relation="res.currency",
             method=True,
             string='Currency',
             readonly=True
         ),
        'total_pagos_presupuestado_plan': fields.function(_total_pagos_plan,
             type='float',
             multi="total_pagos_programados",
             string='Total Presupuestado',
             digits_compute=dp.get_precision('Account'),
             readonly = True,
             store= {
                'plan_contratacion_idu.plan': (lambda self, cr, SUPERUSER_ID, ids, ctx={}: ids, ['item_ids'], 10),
                'plan_contratacion_idu.item': (_get_plan_ids_from_items, ['presupuesto', 'plan_pagos_item_ids'], 20),
            }
         ),
        'total_pagos_programados_plan': fields.function(_total_pagos_plan,
             type='float',
             multi="total_pagos_programados",
             string='Total Pagos Programados',
             digits_compute=dp.get_precision('Account'),
             store= {
                'plan_contratacion_idu.plan': (lambda self, cr, SUPERUSER_ID, ids, ctx={}: ids, ['item_ids'], 10),
                'plan_contratacion_idu.item': (_get_plan_ids_from_items, ['presupuesto', 'plan_pagos_item_ids'], 20),
            }
         ),
        'total_rezago_plan': fields.function(_total_pagos_plan,
             type='float',
             multi="total_pagos_programados",
             string='Total Rezago',
             digits_compute=dp.get_precision('Account'),
             store= {
                'plan_contratacion_idu.plan': (lambda self, cr, SUPERUSER_ID, ids, ctx={}: ids, ['item_ids'], 10),
                'plan_contratacion_idu.item': (_get_plan_ids_from_items, ['presupuesto', 'plan_pagos_item_ids'], 20),
            }
         ),
    }
    _sql_constraints =[
        ('unique_name','unique(name)','El año del plan debe ser único')
    ]
     
    _defaults = {
        'active': True,
        'state': 'inicial',
        'open_close_plan': True,
        'version': 1
    }

    def onchange_open_close_plan(self, cr, uid, ids, numero_orfeo, context=None):
        self.pool.get('plan_contratacion_idu.item')._check_is_editable()

    def wkf_open(self, cr, uid, ids,context=None):
        records = self.read(cr, uid, ids, ['version'],context=context)
        for record in records:
            contador = record['version'] + 1
        self.write(cr, uid, ids, {"version": contador})
        self.write(cr, uid, ids, {"open_close_plan": True})

    def wkf_close(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {"open_close_plan": False})

plan_contratacion_idu_plan()

class plan_contratacion_idu_item(osv.osv):
    _name = "plan_contratacion_idu.item"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Item Plan de Contratación"
    _track = {
        'state': {
            'plan_contratacion_idu.item.mt_radicado': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['radicado'],
            'plan_contratacion_idu.item.mt_suscrito': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['suscrito'],
            'plan_contratacion_idu.item.mt_ejecucion': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['ejecucion'],
            'plan_contratacion_idu.item.mt_ejecutado': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['ejecutado'],
        },
    }

    def _get_name(self, cr, uid, ids, field, args, context=None):
        res = {}
        records = self.pool.get('plan_contratacion_idu.item').browse(cr, uid, ids, context=context)
        for record in records:
            res[record['id']] = "[{4}-{0}-{1}] {2} / {3} ({5})".format(record.dependencia_id.abreviatura,
                 record.id,
                 record.tipo_proceso_id.name,
                 record.tipo_proceso_seleccion_id.name,
                 record.plan_id.vigencia,
                 record.state,
             )
        return res

    def _check_is_editable(self,cr,uid,ids,fieldname,arg,context=None):
        res = {}
        records = self.browse(cr, uid, ids, context=context)
        for record in records:
            plan_record = record.plan_id
            res[record.id] = False
            if plan_record.open_close_plan:
                if record.state == 'version_inicial':
                    res[record.id] = True
                elif(record.state == 'solicitud_cambio'
                    and len(record.solicitud_cambio_id)
                    and record.solicitud_cambio_id[0].state in ['borrador','radicado']
                ):
                    res[record.id] = True
            else:
                res[record.id] = False
        return  res

    def _total_pagos_programados(self, cr, uid, ids, name, args, context=None):
        res = {}
        if isinstance(ids, (list, tuple)) and not len(ids):
            return res
        if isinstance(ids, (long, int)):
            ids = [ids]
        records = self.browse(cr, uid, ids, context=context)
        for record in records:
            sumatoria = 0
            res[record['id']] = {}
            for pago in record.plan_pagos_item_ids:
                sumatoria += pago.valor
            res[record['id']]['total_pagos_programados'] = sumatoria
            res[record['id']]['presupuesto_rezago'] = record.presupuesto - sumatoria
        return res

    def _total_pagos_realizados(self, cr, uid, ids, name, args, context=None):
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
            for pago in record.plan_pagos_giro_ids:
                sumatoria += pago.valor
            res[record['id']]['total_pagos_realizados'] = sumatoria
        return res

    def _get_plan_item_from_pago_records(self, cr, uid, pago_ids, context=None):
        """
        Retorna los IDs del plan_item a ser recalculados cuando cambia un pago_item
        """
        records = self.pool.get('plan_contratacion_idu.plan_pagos_item').browse(cr, uid, pago_ids, context=context)
        plan_item_ids = [record.plan_contratacion_item_id.id for record in records if record.id]
        return plan_item_ids

    def _get_plan_item_from_pago_giro_records(self, cr, uid, pago_ids, context=None):
        """
        Retorna los IDs del plan_item a ser recalculados cuando cambia un pago_item
        """
        records = self.pool.get('plan_contratacion_idu.plan_pagos_giro').browse(cr, uid, pago_ids, context=context)
        plan_item_ids = [record.plan_contratacion_item_id.id for record in records if record.id]
        return plan_item_ids

    def _check_fechas_programadas(self,cr,uid,ids,context=None):
        """valida las fechas programadas"""
        res = {}
        if isinstance(ids, (list, tuple)) and not len(ids):
            return res
        if isinstance(ids, (long, int)):
            ids = [ids]
        records = self.browse(cr, uid, ids, context=context)
        for record in records:
            if (record.fecha_programada_crp and record.fecha_programada_radicacion and record.fecha_programada_crp < record.fecha_programada_radicacion):
                return False
            if (record.fecha_programada_crp and record.fecha_programada_acta_inicio and record.fecha_programada_acta_inicio < record.fecha_programada_crp):
                return False
        return True

    def _check_state_aprobado(self,cr,uid,ids,context=None):
        """valida el cambio de estado por los campos requeridos"""
        res = {}
        if isinstance(ids, (list, tuple)) and not len(ids):
            return res
        if isinstance(ids, (long, int)):
            ids = [ids]
        records = self.browse(cr, uid, ids, context=context)
        is_valid = True
        for record in records:
            if record.state == 'aprobado':
                if record.codigo_unspsc and record.centro_costo_id:
                    is_valid = True
                else:
                    is_valid = False
        return is_valid

    def _check_state_radicado(self,cr,uid,ids,context=None):
        """valida el cambio de estado y si existe el numero de radicado en orfeo"""
        res = {}
        if isinstance(ids, (list, tuple)) and not len(ids):
            return res
        if isinstance(ids, (long, int)):
            ids = [ids]
        records = self.browse(cr, uid, ids, context=context)
        is_valid = True
        for record in records:
            if record.state == 'radicado':
                if record.numero_orfeo:
                    try:
                        is_valid = orfeo_existe_radicado(record.numero_orfeo)
                    except Exception as e:
                        raise Exception.message('Error al consultar servicio web OFRFEO', str(e))
                else:
                    is_valid = False
        return is_valid

    def _check_state_suscrito(self,cr,uid,ids,context=None):
        """valida el cambio de estado"""
        res = {}
        if isinstance(ids, (list, tuple)) and not len(ids):
            return res
        if isinstance(ids, (long, int)):
            ids = [ids]
        records = self.browse(cr, uid, ids, context=context)
        is_valid = True
        for record in records:
            if record.state == 'suscrito':
                if record.numero_contrato and record.numero_crp:
                    is_valid = True
                else:
                    is_valid = False
        return is_valid

    def _check_state_ejecucion(self,cr,uid,ids,context=None):
        """valida el cambio de estado """
        res = {}
        if isinstance(ids, (list, tuple)) and not len(ids):
            return res
        if isinstance(ids, (long, int)):
            ids = [ids]
        records = self.browse(cr, uid, ids, context=context)
        is_valid = True
        for record in records:
            if record.state == 'ejecucion':
                if record.fecha_acta_inicio:
                    is_valid = True
                else:
                    is_valid = False
        return is_valid

    def _check_state_ejecutado(self,cr,uid,ids,context=None):
        """valida el cambio de estado"""
        res = {}
        if isinstance(ids, (list, tuple)) and not len(ids):
            return res
        if isinstance(ids, (long, int)):
            ids = [ids]
        records = self.browse(cr, uid, ids, context=context)
        res = {}
        is_valid = True
        for record in records:
            if record.state == 'ejecutado':
                if record.fecha_acta_liquidacion:
                    is_valid = True
                else:
                    is_valid = False
        return is_valid

    def _progress_rate(self, cr, uid, ids, field_names, args, context=None):
        res = {}
        if isinstance(ids, (list, tuple)) and not len(ids):
            return res
        if isinstance(ids, (long, int)):
            ids = [ids]
        records = self.browse(cr, uid, ids, context=context)
        for record in records:
            res[record['id']] = {}
            if record.state == 'version_inicial':
                res[record['id']]['progress_rate']=10
            if record.state == 'aprobado':
                res[record['id']]['progress_rate']=20
            if record.state == 'radicado':
                res[record['id']]['progress_rate']=30
            if record.state == 'suscrito':
                res[record['id']]['progress_rate']=50
            if record.state == 'ejecucion':
                res[record['id']]['progress_rate']=70
            if record.state == 'ejecutado':
                res[record['id']]['progress_rate']=100
            if record.state == 'no_realizado':
                res[record['id']]['progress_rate']=0
        return res

    _columns = {
        'name': fields.function(_get_name,
             type='char',
             string='Nombre',
             readonly=True,
             store=False,
        ),
        'is_editable':fields.function(_check_is_editable,
             type='boolean',
             string='Verifica si el item del plan es editable',
             method=True),
        'is_plan_open': fields.related(
            'plan_id','open_close_plan',
             type="boolean",
             string="Está el plan contractual esta abierto para edición?",
             store=False,
             readonly=True
        ),
        'codigo_unspsc': fields.char('Codigo UNSPSC',
             help='Codificación de bienes y servicios, Colombia compra eficiente',
             readonly=False,
             required=False,
             track_visibility='onchange'),
        'dependencia_id': fields.many2one('hr.department','Dependencia',
             select=True,
             ondelete='cascade',
             required=True,
             readonly=False,
             states={'solicitud_cambio':[('required',False)], 'borrador':[('required',False)]},
             track_visibility='onchange'
         ),
        'description': fields.text('Objeto Contractual',
             readonly=False,
             required=False,
             states={'version_inicial':[('required',True)]},
             track_visibility='onchange'),
        'centro_costo':fields.char('Centro de Costo',size=512,
             readonly=False,
             required=False,
             help="Ingrese el número del Centro de Costo para consultar la información",
             track_visibility='onchange'),
        'centro_costo_id': fields.many2one('stone_erp_idu.centro_costo','Codigo Centro de Costo',
             readonly=True,
             select=True,
             ondelete='cascade'),
        'centro_costo_nombre':fields.related('centro_costo_id','name',
             type="char",
             relation="stone_erp_idu.centro_costo",
             string="Nombre Centro de Costo",
             store=False,
             readonly=True),
        'cod_proyecto_idu':fields.related('centro_costo_id','cod_proyecto_idu',
             type="integer",
             relation="stone_erp_idu.centro_costo",
             string="Codigo Proyecto IDU",
             store=False,
             readonly=True),
        'nombre_proyecto_idu':fields.related('centro_costo_id','nombre_proyecto_idu',
             type="char",
             relation="stone_erp_idu.centro_costo",
             string="Nombre Proyecto IDU",
             store=False,
             readonly=True),
        'cod_punto_inversion':fields.related('centro_costo_id','cod_punto_inversion',
             type="integer",
             relation="stone_erp_idu.centro_costo",
             string="Codigo Punto Inversion",
             store=False,
             readonly=True),
        'nombre_punto_inversion':fields.related('centro_costo_id','nombre_punto_inversion',
             type="char",
             relation="stone_erp_idu.centro_costo",
             string="Nombre Punto Inversion",
             store=False,
             readonly=True),
        'cod_fase_intervencion':fields.related('centro_costo_id','cod_fase_intervencion',
             type="integer",
             relation="stone_erp_idu.centro_costo",
             string="Codigo Fase Intervención",
             store=False,
             readonly=True),
        'nombre_fase_intervencion':fields.related('centro_costo_id','nombre_fase_intervencion',
             type="char",
             relation="stone_erp_idu.centro_costo",
             string="Nombre Fase Intervencion",
             store=False,
             readonly=True),
        'fuente_id': fields.many2one('plan_contratacion_idu.fuente','Fuente de Financiación',
             select=True,
             ondelete='cascade',
             readonly=False,
             required=False,
             states={'version_inicial':[('required',True)]},
             track_visibility='onchange'),
        'state':fields.selection([('version_inicial', 'Versión Inicial'),('aprobado', 'Aprobado'),('radicado', 'Radicado'),
             ('suscrito', 'Contrato Suscrito'),('ejecucion', 'Ejecución'),('ejecutado', 'Ejecutado'),
             ('no_realizado', 'No realizado'), ('solicitud_cambio', 'Solicitud de Cambio')],'State',
             track_visibility='onchange',
             required=True,
             readonly=True,
             states={'solicitud_cambio':[('required',False)]}),
        'fecha_programada_radicacion': fields.date ('Fecha Radicacion en DTPS y/o DTGC',
             help="Fecha estimada de inicio de proceso de selección",
             required=False,
             select=True,
             readonly=False,
             track_visibility='onchange'),
        'fecha_programada_crp': fields.date ('Fecha Programada CRP',
             required=False,
             select=False,
             help="CRP es Certificado Registro Presupuestal",
             readonly=False,
             track_visibility='onchange'),
        'fecha_programada_acta_inicio': fields.date ('Fecha Aprobación Acta de Inicio',
             required=False,
             select=False,
             readonly=False,
             track_visibility='onchange'),
        'plan_id': fields.many2one('plan_contratacion_idu.plan','Plan contractual',
             select=True,
             ondelete='cascade',
             readonly=True,
             required=True,
             states={'version_inicial':[('readonly',False)]},
             track_visibility='onchange'),
        'clasificacion_id': fields.many2one('plan_contratacion_idu.clasificador_proyectos','Clasificación Proyecto',
             select=True,
             ondelete='cascade',
             readonly=False,
             required=False,
             states={'version_inicial':[('required',True)]},
             track_visibility='onchange',
             domain=[('tipo','=','proyecto_prioritario')],
         ),
        'presupuesto': fields.float ('Presupuesto',
             select=True,
             obj="res.currency",
             track_visibility='onchange',
             readonly=False,
             required=False,
             states={'version_inicial':[('required',True)]}),
        'plazo_de_ejecucion': fields.integer('Plazo de Ejecución (meses)',
             select=True,
             help="Tiempo estimado en meses",
             readonly=False,
             track_visibility='onchange'),
        'a_monto_agotable':fields.boolean('A monto agotable',
             help="plazo de ejecución a monto agotable",
             readonly=False,
             track_visibility='onchange'),
        'unidad_meta_fisica_id': fields.many2one('product.uom',
            'Unidad Meta Física',
             select=True,
             ondelete='cascade',
             readonly=False,
             track_visibility='onchange'),
        'no_aplica_unidad_mf':fields.boolean('No aplica unidad de meta física',
             help="Seleccionar cuando no aplica la unidad de meta física",
             readonly=False,
             track_visibility='onchange'),
        'cantidad_meta_fisica': fields.char ('Cantidad Metas Físicas',
             size=255,
             readonly=False,
             track_visibility='onchange'),
        'localizacion':fields.selection([('66', '66 - Entidad'),('77', '77 - Metropolitana'),('localidad', 'Localidad')],
             'Localizacion',
             select=True,
             help="Localización del item",
             readonly=False,
             required=False,
             states={'version_inicial':[('required',True)]},
             track_visibility='onchange'),
        'localidad_ids': fields.many2many('base_map.district','plan_contratacion_idu_localidad_item',
             'base_localidad_id',
             'plan_localidad_id',
             'localidades del item',
             select=True,
             ondelete='cascade',
             readonly=False,
             track_visibility='onchange'),
        'currency_id': fields.related('plan_id','currency_id',
             type='many2one',
             relation='res.currency',
             string='Company',
             store=True,
             readonly=True),
        'tipo_proceso_id': fields.many2one('plan_contratacion_idu.plan_tipo_proceso','Tipo Proceso',
             select=True,
             ondelete='cascade',
             readonly=False,
             required=False,
             states={'version_inicial':[('required',True)]},
             track_visibility='onchange'),
        'tipo_proceso_seleccion_id': fields.many2one('plan_contratacion_idu.plan_tipo_proceso_seleccion','Modalidad de Selección',
             select=True,
             ondelete='cascade',
             readonly=False,
             required=False,
             states={'version_inicial':[('required',True)]},
             track_visibility='onchange'),
        'plan_pagos_item_ids': fields.one2many('plan_contratacion_idu.plan_pagos_item','plan_contratacion_item_id',
             'Planificacion de Pagos',
             select=True,
             ondelete='cascade',
             readonly=False,
             required=False,
             states={'version_inicial':[('required',True)]},
             track_visibility='onchange'),
        'plan_pagos_giro_ids': fields.one2many('plan_contratacion_idu.plan_pagos_giro',
             'plan_contratacion_item_id',
             'Giros Realizados',
             select=True,
             ondelete='cascade',
             readonly=True),
        'total_pagos_programados': fields.function(_total_pagos_programados,
             type='float',
             multi="presupuesto",
             string='Total pagos programados',
             obj="res.currency",
             digits_compute=dp.get_precision('Account'),
             store={
                'plan_contratacion_idu.item': (lambda self, cr, uid, ids, c={}: ids, ['plan_pagos_item_ids', 'presupuesto'], 10),
                'plan_contratacion_idu.plan_pagos_item': (_get_plan_item_from_pago_records, ['valor', 'mes', 'plan_contratacion_item_id'], 20),
            }),
        'presupuesto_rezago': fields.function(_total_pagos_programados,
             type='float',
             multi="presupuesto",
             string='Rezago',
             obj="res.currency",
             digits_compute=dp.get_precision('Account'),
             store={
                'plan_contratacion_idu.item': (lambda self, cr, uid, ids, c={}: ids, ['plan_pagos_item_ids', 'presupuesto'], 10),
                'plan_contratacion_idu.plan_pagos_item': (_get_plan_item_from_pago_records, ['valor', 'mes', 'plan_contratacion_item_id'], 20),
                'plan_contratacion_idu.item': (lambda self, cr, uid, ids, c={}: ids, ['presupuesto', 'presupuesto'], 30),
            }),
        'total_pagos_realizados': fields.function(_total_pagos_realizados,
             type='float',
             multi="presupuesto",
             string='Total pagos realizados',
             obj="res.currency",
             digits_compute=dp.get_precision('Account'),
             store={
                'plan_contratacion_idu.item': (lambda self, cr, uid, ids, c={}: ids, ['plan_pagos_giro_ids', 'presupuesto'], 10),
                'plan_contratacion_idu.plan_pagos_giro': (_get_plan_item_from_pago_giro_records, ['valor', 'plan_contratacion_item_id'], 20),
            }),
        'numero_orfeo':fields.char('Número Radicado Orfeo',
             help='Validado desde Orfeo',
             states={'aprobado':[('readonly',False)]}, readonly=True,
             track_visibility='onchange'),
        'fecha_radicado_orfeo':fields.date('Fecha Radicado', readonly=True,
             help='Validado desde Orfeo',),
        'numero_crp':fields.char('Numero CRP',
             help ='Validado desde SIAC',
             readonly=True,
             track_visibility='onchange'),
        'numero_contrato': fields.char('Numero Contrato',
             help ='Validado desde SIAC',
             states={'radicado':[('readonly',False)]},
             readonly=True,
             track_visibility='onchange'),
        'nit_beneficiario':fields.float('Nit Beneficiario',
             help ='Validado desde SIAC',
             readonly=True),
        'fecha_acta_inicio':fields.date('Fecha Acta de Inicio',
             help = 'Validado desde SIAC',
             readonly=True),
        'fecha_acta_liquidacion':fields.date('Fecha acta de Liquidacion',
             help = 'Validado desde SIAC',
             readonly =True),
        'progress_rate': fields.function(_progress_rate, multi="progress",
             string='Progreso (%)',
             type='float',
             group_operator="avg",
             help="Porcentaje de avance del item.",
             store = True
        ),
        'solicitud_cambio_ids': fields.one2many('plan_contratacion_idu.item_solicitud_cambio',
            'plan_item_id',
            string='Solicitudes de cambio',#plan item a solicitud de cambio
        ),
        'solicitud_cambio_id': fields.one2many('plan_contratacion_idu.item_solicitud_cambio',
            'item_nuevo_id',
            string='Solicitud de cambio',#de solicitud de cambio a plan_item
        ),
        'cambios_propuestos_ids': fields.many2many('plan_contratacion_idu.item','plan_contr_item_solicitud_cambio',
             'plan_item_id',
             'item_nuevo_id',
             'Items con los cambios propuestos',
             readonly=True,
             track_visibility='onchange'
        ),
        'item_a_cambiar': fields.related('solicitud_cambio_id',
            'plan_item_id',
            type="many2one",
            relation="plan_contratacion_idu.item",
            string="Item del plan a ser cambiado",
            store=False
        ),
    }



    def _default_dependencia_id(self, cr, uid, context):
        department_ids = self.pool.get('res.users').browse(cr, uid, uid, context=context).department_ids
        if department_ids:
            return department_ids
        return None


    def _default_plan_id(self, cr, uid, context):
        if context and 'plan_id' in context:
            return context['plan_id']
        else:
            return self.pool.get('plan_contratacion_idu.plan').search(cr, uid,
                [('state','=','inicial')],
                limit=1,
                context=context
            )[0]

    _defaults = {
        'state': 'version_inicial',
        'progress_rate':0,
        'dependencia_id': _default_dependencia_id,
        #Asigna por defecto el plan contractual pasado en el contexto
        'plan_id' : _default_plan_id,
        'is_editable': True,
    }

    _constraints = [(_check_fechas_programadas,
                    "La fecha programada CRP debe ser posterior a la fecha programada de radicación y anterior a la fecha programada para la aprobación del acta de Inicio",
                    ['fecha_programada_crp','fecha_programada_acta_inicio']),
                    (_check_state_aprobado,
                    "Para cambiar el estado a Aprobado debe ingresar los campos requeridos",
                    ['state', 'codigo_unspsc', 'centro_costo_id']),
                    (_check_state_radicado,
                    "Para cambiar el estado a Radicado debe ingresar el un número válido de radicado Orfeo en Fechas de Ejecución",
                    ['state', 'numero_orfeo']),
                    (_check_state_suscrito,
                    "Para cambiar el estado a Contrato Suscrito debe ingresar el número CRP en Fechas de Ejecución",
                    ['state', 'numero_contrato','numero_crp']),
                    (_check_state_ejecucion,
                    "Para cambiar el estado a Ejecucion debe ingresar el número del contrato en Fechas de Ejecución",
                    ['state', 'fecha_acta_inicio']),
                    (_check_state_ejecutado,
                    "Para cambiar el estado a Ejecutado debe ingresar el número del contrato en Fechas de Ejecución",
                    ['state', 'fecha_acta_liquidacion']),
                    ]

#FIXME: Aqui esta llamando al centro_costo.write y create, esto centralizarse solo en strone_erp_idu.
    def on_change_centro_costo(self, cr, uid, plan_item_ids, centro_costo, context=None):
        centro_costo_obj=self.pool.get('stone_erp_idu.centro_costo')
        #Verificacion que el centro de costo este guardado en la base de datos
        ids = centro_costo_obj.search(cr,uid,[('codigo','=',centro_costo)])
       
        id_cc = 0
        if (ids.__len__()==0):
            #No hay nada en base de datos entonces buscar en el stone
            wsdl = self.pool.get('ir.config_parameter').get_param(cr,uid,'stone_idu.webservice.wsdl',default=False,context=context)
            det_cc = stone_client_ws.completar_datos_centro_costo(wsdl, centro_costo)
            if (det_cc == False):
                raise osv.except_osv('Error','No existe el Centro de Costo')
            else :
                #Mejor guardar provisionalmente y despues se hace la actualizacion y se le pone el nombre jaja
                id_cc = centro_costo_obj.create(cr,1,{'codigo':det_cc['centro_costo'],'name':det_cc['centro_costo']})
                centro_costo_obj.actualizar_centros_costo(cr,uid,context)
        else :
            id_cc = ids[0]
        #Actualiza valores completo centro de costo -> No se hace por defecto para evitar ralentizar la aplicacion"
        vals = centro_costo_obj.completar_centro_costo(cr,1,{'codigo':centro_costo},context = context)
        centro_costo_obj.write(cr,1,id_cc,vals,context = context)
        centro_costo = centro_costo_obj.browse(cr,1,id_cc,context) 
        #Completar Diccionarionombre_punto_inversion
        
        res = {'value':{'centro_costo_id':id_cc,
                        'centro_costo_nombre':centro_costo.name,
                        'cod_punto_inversion':centro_costo.cod_punto_inversion,
                        'nombre_punto_inversion':centro_costo.nombre_punto_inversion,
                        'cod_proyecto_idu':centro_costo.cod_proyecto_idu,
                        'nombre_proyecto_idu':centro_costo.nombre_proyecto_idu,
                        'cod_fase_intervencion':centro_costo.cod_fase_intervencion,
                        'nombre_fase_intervencion':centro_costo.nombre_fase_intervencion}}
        return res

    def update_vals(self,cr,uid,vals,context=None):
        if 'centro_costo' in vals:
            centro_costo = vals["centro_costo"]
            centro_costo_obj=self.pool.get('stone_erp_idu.centro_costo')
            ids = centro_costo_obj.search(cr,uid,[('codigo','=',centro_costo)])
            if (ids.__len__() > 0):
                vals['centro_costo_id'] = ids[0]
            else:
                #No permite que el centro de costo se guarde con un valor no válido
                vals["centro_costo"] = False
        return vals

    def write (self,cr,uid, ids, vals, context = None):
        vals = self.update_vals(cr,uid,vals,context=None)
        write = super(plan_contratacion_idu_item,self).write(cr,uid,ids,vals,context=context)
        return write
    
    def create (self,cr,uid,vals,context=None):
        """
        Crea el item del plan de contratacion y hace persistencia en los valores calculados
        """
        vals = self.update_vals(cr,uid,vals,context=None)
        id_item = super(plan_contratacion_idu_item,self).create(cr,uid,vals,context=context)
        return id_item

    def onchange_plan_pagos_item_ids(self, cr, uid, ids, plan_pagos_item_ids, context=None):
        context = context or {}
        pagos_pool = self.pool.get('plan_contratacion_idu.plan_pagos_item')
        if not plan_pagos_item_ids:
            plan_pagos_item_ids = []
        sumatoria = 0
        res = {
                'total_pagos_programados': 0,
                #'presupuesto_rezago': 0,
        }
        plan_pagos_item_ids = resolve_o2m_operations(cr, uid, pagos_pool, plan_pagos_item_ids, ['valor'], context)
        if ids:
            plan_item = self.read(cr, uid, ids[0], ['presupuesto'], context=context)
            for pago in plan_pagos_item_ids:
                sumatoria += pago.get('valor',0.0)
            res = {
                'total_pagos_programados': sumatoria,
                'presupuesto_rezago': plan_item['presupuesto'] - sumatoria,
            }
        return {
            'value': res
        }

    def onchange_plan_pagos_giro_ids(self, cr, uid, ids, plan_pagos_giro_ids, context=None):
        self.pool.get('plan_contratacion_idu.item')._total_pagos_realizados()

    def onchange_presupuesto(self, cr, uid, ids, presupuesto, context=None):
        self.pool.get('plan_contratacion_idu.item')._total_pagos_programados()
        self.pool.get('plan_contratacion_idu.plan')._total_pagos_plan()

    def onchange_a_monto_agotable(self, cr, uid, ids, a_monto_agotable, context=None):
        return {'value': {'plazo_de_ejecucion': 0}}

    def onchange_no_aplica_unidad_mf(self, cr, uid, ids, no_aplica_unidad_mf, context=None):
        return {
            'value': {
                'unidad_meta_fisica_id': False,
                'cantidad_meta_fisica': False
            }
        }

    def onchange_numero_orfeo(self, cr, uid, ids, numero_orfeo, context=None):
        res={}
        if orfeo_existe_radicado(numero_orfeo):
            self.write(cr, uid, ids, {"state": "radicado",
                                      "numero_orfeo":numero_orfeo,
                                      "fecha_radicado_orfeo":orfeo_fecha_radicado(numero_orfeo).FECHA,
                       }
            )
            res = {'value': {
                       'fecha_radicado_orfeo': orfeo_fecha_radicado(numero_orfeo).FECHA,
                       'numero_orfeo': numero_orfeo,
                       'state': 'radicado',
                   },
                   'warning': {
                        'message': 'Número de radicado Orfeo encontrado'
                   }
           }
        else:
            res = {'value':{
                        'fecha_radicado_orfeo':False,
                        'numero_orfeo':False
                    },
                   'warning': {
                       'message': 'El número de radicado Orfeo ingresado no existe'
                    }
            }
        return res

    def onchange_numero_contrato(self, cr, uid, ids, numero_contrato, context=None):
        res = {}
        if not context:
            context = {}
        wsdl_url = self.pool.get('ir.config_parameter').get_param(cr,uid,'siac_idu.webservice.wsdl',default=False,context=context)
        datos_contrato = siac_ws.obtener_datos_contrato(wsdl_url,numero_contrato)
        if (datos_contrato):
            crp_list = datos_contrato['numero_crp']
            lista_crp = ()
            if isinstance(crp_list, int):
                lista_crp = [(crp_list, crp_list)]
                self.write(cr, uid, ids, {
                  'state': 'suscrito',
                  'numero_crp': datos_contrato['numero_crp'],
                  'numero_contrato': datos_contrato['codigo_contrato'],
                  'nit_beneficiario': datos_contrato['nit_contratista']
                })
                res = {
                   'value': {
                       'numero_crp':  datos_contrato['numero_crp'],
                       'numero_contrato':datos_contrato['codigo_contrato'],
                       'nit_beneficiario': datos_contrato['nit_contratista'],
                       'state': 'suscrito'
                    }
                }
            else:
                self.write(cr, uid, ids, {
                  "numero_contrato": datos_contrato['codigo_contrato'][0],
                  "nit_beneficiario": datos_contrato['nit_contratista'][0]
                })
                res = {
                   'value': {
                       'numero_contrato':datos_contrato['codigo_contrato'][0],
                       'nit_beneficiario': datos_contrato['nit_contratista'][0],
                    },
                    'warning': {
                        'message': 'Este contrato tiene mas de un número CRP relacionado, Seleccione el correspondiente al Item'
                    }
                 }
                for crp in crp_list:
                    lista_crp = lista_crp + ((crp, crp),)
                context['crp_list'] = lista_crp
                self.abrir_obtener_crp_wizard(cr, uid, ids, context=context)
        else :
            res = {
               'value':{
                   'numero_crp':"",
                   'numero_contrato':"",
                   'nit_beneficiario':False
               }
            }
            raise osv.except_osv('Error','No existe información para este número de contrato')
        return res

    def abrir_obtener_crp_wizard(self, cr, uid, ids, context=None):
        wizard_id = self.pool['plan_contratacion_idu.wizard.crp'].create(cr, uid, vals={}, context=context)
        return {
            'name': 'Seleccionar CRP',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'plan_contratacion_idu.wizard.crp',
            'res_id': wizard_id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }

    def obtener_datos_contrato(self, cr, uid, ids=None, context=None):
        wsdl_url = self.pool.get('ir.config_parameter').get_param(cr,uid,'siac_idu.webservice.wsdl',default=False,context=context)
        id_records = self.search(cr, uid,[('state', '=', 'suscrito')],context=context)
        for record in self.browse(cr, uid, id_records, context):
            datos_contrato = siac_ws.obtener_datos_contrato(wsdl_url, record.numero_contrato)
            if (datos_contrato):
                contrato_fecha_acta_inicio = datos_contrato['fecha_acta_inicio']
                if isinstance(contrato_fecha_acta_inicio, date):
                    self.write(cr, uid, record.id, {"fecha_acta_inicio": datos_contrato['fecha_acta_inicio']})
                    self.write(cr, uid, record.id, {"state": "ejecucion"})
                else:
                    self.write(cr, uid, record.id, {"fecha_acta_inicio": datos_contrato['fecha_acta_inicio'][0]})
                    self.write(cr, uid, record.id, {"state": "ejecucion"})
        id_records_ejecucion = self.search(cr, uid,[('state', '=', 'ejecucion')],context=context)
        for record in self.browse(cr, uid, id_records_ejecucion, context):
            datos_contrato = siac_ws.obtener_datos_contrato(wsdl_url, record.numero_contrato)
            if (datos_contrato):
                if datos_contrato['fecha_acta_liquidacion']:
                    if isinstance(datos_contrato['fecha_acta_liquidacion'], date):
                        self.write(cr, uid, record.id, {"fecha_acta_liquidacion": datos_contrato['fecha_acta_liquidacion']})
                        self.write(cr, uid, record.id, {"state": "ejecutado"})
                    else:
                        self.write(cr, uid, record.id, {"fecha_acta_liquidacion": datos_contrato['fecha_acta_liquidacion'][0]})
                        self.write(cr, uid, record.id, {"state": "ejecutado"})

    def obtener_pagos_realizados(self, cr, uid, ids=None, context=None):
        dato_giros={}
        if not ids:
            ids = self.search(cr, uid,[('state', '=', 'ejecucion')],context=context)
        records_plan_item = self.browse(cr, uid, ids, context=context)
        wsdl = self.pool.get('ir.config_parameter').get_param(cr,uid,'stone_idu.webservice.wsdl',default=False,context=context)
        pago_realizado_pool = self.pool.get('plan_contratacion_idu.plan_pagos_giro')
        for record_plan_item in records_plan_item:
            records_pago_realizado = pago_realizado_pool.search(cr, uid, [('plan_contratacion_item_id','=', record_plan_item.id)])
            pago_realizado_pool.unlink(cr, uid, records_pago_realizado, context=context)
            nit = record_plan_item.nit_beneficiario
            numero = record_plan_item.numero_contrato
            numero = numero.split('-')
            dato_giros = stone_client_ws.obtener_giros(wsdl,numero[0],numero[1],numero[2],nit)
            for k in dato_giros:
                if str(k['pre_crp_numero']) == record_plan_item.numero_crp:
                    vals = {
                        'plan_contratacion_item_id': record_plan_item.id,
                        'orden_pago': k['pre_op_numero'],
                        'date': k['pre_op_fecha'],
                        'valor': k['pre_crp_valor'],
                        'currency_id': record_plan_item.id
                    }
                    pago_realizado_pool.create(cr, uid, vals, context=context)

    def wkf_version_inicial(self, cr, uid, ids, plan_items, context=None):
        self.write(cr, uid, ids, {
                                  "state": "version_inicial",
                                  "numero_orfeo": None,
                                  "fecha_radicado_orfeo": None,
                                  "numero_crp": None,
                                  "numero_contrato": None,
                                  "nit_beneficiario": None,
                                  "fecha_acta_inicio": None,
                                  "fecha_acta_liquidacion": None
                    }
        )

    def wkf_aprobado(self, cr, uid, ids, plan_items, context=None):
        self.write(cr, uid, ids, {
                                  "state": "aprobado",
                                  "numero_orfeo": None,
                                  "fecha_radicado_orfeo": None,
                                  "numero_crp": None,
                                  "numero_contrato": None,
                                  "nit_beneficiario": None,
                                  "fecha_acta_inicio": None,
                                  "fecha_acta_liquidacion": None
                    }
        )

    def wkf_radicado(self, cr, uid, ids, plan_items, context=None):
        self.write(cr, uid, ids, {
                                  "state": "radicado",
                                  "numero_contrato": None,
                                  "numero_crp": None,
                                  "nit_beneficiario": None,
                                  "fecha_acta_inicio": None,
                                  "fecha_acta_liquidacion":None
                    }
        )

    def wkf_no_realizado(self, cr, uid, ids, plan_items, context=None):
        self.write(cr, uid, ids, {
                                  "state": "no_realizado"
                    }
        )

    def wkf_suscrito(self, cr, uid, ids, plan_items, context=None):
        self.write(cr, uid, ids, {
                                  "state": "suscrito",
                                  "fecha_acta_inicio": None,
                                  "fecha_acta_liquidacion": None
                    }
        )

    def wkf_ejecucion(self, cr, uid, ids, plan_items, context=None):
        self.write(cr, uid, ids, {
                                  "state": "ejecucion",
                                  "fecha_acta_liquidacion": None
                    }
        )

    def wkf_ejecutado(self, cr, uid, ids, plan_items, context=None):
        self.write(cr, uid, ids, {
                                  "state": "ejecutado"
                    }
        )

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
        'codigo': fields.integer ('Código', required=True, select=True),
        'name': fields.char('Nombre', size=255, required=True, select=True),
        'tipo': fields.selection([('proyecto_inversion', 'Proyecto de Inversión'),
             ('proyecto_prioritario', 'Proyecto Prioritario')],'Tipo',
             required=True),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Nombre'),
        'parent_id': fields.many2one('plan_contratacion_idu.clasificador_proyectos',
             'Clasificación padre',
             select=True,
             ondelete='cascade'),
        'child_ids': fields.one2many('plan_contratacion_idu.clasificador_proyectos',
             'parent_id',
             string='Clasificaciones hijas'),
        'sequence': fields.integer('Sequence', select=True,
             help="Secuencia para el ordenamiento en las listas"),
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
        'codigo_fuente':fields.char('Codigo Fuente',size=10,required=True, select=True),
        'name': fields.char('Nombre', size=50, required=True, select=True),
        'codigo_fuente_sdh': fields.char('Codigo Fuente Secretaria Distrital de Hacienda',
              size=10,
              required=True,
              select=True),
        'nombre_fuente_sdh': fields.char('Nombre Fuente Secretaria Distrital de Hacienda',
              size=50,
              required=True,
              select=True),
        'codigo_detalle_fuente_sdh': fields.char('Código detalle fuente Secretaria Distrital de Hacienda',
              size=10,
              required=True,
              select=True),
        'nombre_detalle_fuente_sdh': fields.char('Nombre detalle fuente Secretaria Distrital de Hacienda',
              size=50,
              select=True),
    }
plan_contratacion_idu_fuente()

class plan_contratacion_idu_plan_pagos_item(osv.osv):
    _name = "plan_contratacion_idu.plan_pagos_item"

    def _check_pagos_programados(self,cr,uid,ids,context=None):
        """valida que el valor del pago sea mayor a $0"""
        res = {}
        if isinstance(ids, (list, tuple)) and not len(ids):
            return res
        if isinstance(ids, (long, int)):
            ids = [ids]
        records = self.browse(cr, uid, ids, context=context)
        is_valid = True
        for record in records:
            if record.valor > 0:
                is_valid = True
            else:
                is_valid = False
        return is_valid

    _columns = {
        'mes': fields.selection([(1,'Enero'), (2,'Febrero'), (3,'Marzo'), (4,'Abril'),
            (5,'Mayo'), (6,'Junio'), (7,'Julio'), (8,'Agosto'), (9,'Septiembre'),
            (10,'Octubre'), (11,'Noviembre'), (12,'Diciembre')],'Mes', required=True),
        'valor': fields.float('Valor', select=True, obj="res.currency", digits_compute=dp.get_precision('Account')),
        'plan_contratacion_item_id': fields.many2one('plan_contratacion_idu.item','Item Plan de Contratacion',
            select=True,
            ondelete='cascade'),
        'currency_id': fields.related('plan_contratacion_item_id','currency_id',
            type='many2one',
            relation='res.currency',
            string='Company',
            store=True,
            readonly=True),
    }

    _sql_constraints =[
        ('unique_mes','unique(mes,plan_contratacion_item_id)','El mes debe ser único'),
    ]
    _constraints = [
        (_check_pagos_programados, 'Error! Necesita adicionar un valor mayor que $0.', ['valor']),
    ]

    _defaults = {
        'mes': 1,
    }


    _order = 'mes'

plan_contratacion_idu_plan_pagos_item()

class plan_contratacion_idu_plan_pagos_giro(osv.osv):
    _name = "plan_contratacion_idu.plan_pagos_giro"
    _columns = {
        'orden_pago': fields.char('Orden de Pago'),
        'date':fields.datetime("Fecha"),
        'valor':fields.integer("Valor", obj="res.currency", digits_compute=dp.get_precision('Account')),
        'plan_contratacion_item_id': fields.many2one('plan_contratacion_idu.item',
              'Item Plan de Contratacion',
              select=True,
              ondelete='cascade'),
        'currency_id': fields.related('plan_contratacion_item_id',
              'currency_id',
              type='many2one',
              relation='res.currency',
              string='Company',
              store=True,
              readonly=True),
    }

    _order = 'date'

plan_contratacion_idu_plan_pagos_giro()


class plan_contratacion_idu_plan_tipo_proceso(osv.osv):
    _name = "plan_contratacion_idu.plan_tipo_proceso"
    _columns = {
        'name':fields.char('Nombre', size=255, required=True, select=True),
    }

    _sql_constraints =[
        ('unique_name','unique(name)','El tipo de proceso debe ser único')
    ]

plan_contratacion_idu_plan_tipo_proceso()

class plan_contratacion_idu_plan_tipo_proceso_seleccion(osv.osv):
    _name = "plan_contratacion_idu.plan_tipo_proceso_seleccion"
    _columns = {
        'name':fields.char('Nombre', size=255, required=True, select=True),
    }

    _sql_constraints =[
        ('unique_name','unique(name)','El tipo de proceso debe ser único')
    ]

def resolve_o2m_operations(cr, SUPERUSER_ID, target_osv, operations, fields, context):
    results = []
    for operation in operations:
        result = None
        if not isinstance(operation, (list, tuple)):
            result = target_osv.read(cr, SUPERUSER_ID, operation, fields, context=context)
        elif operation[0] == 0:
            # may be necessary to check if all the fields are here and get the default values?
            result = operation[2]
        elif operation[0] == 1:
            result = target_osv.read(cr, SUPERUSER_ID, operation[1], fields, context=context)
            if not result: result = {}
            result.update(operation[2])
        elif operation[0] == 4:
            result = target_osv.read(cr, SUPERUSER_ID, operation[1], fields, context=context)
        if result != None:
            results.append(result)
    return results

class res_users(osv.osv):
    _name = 'res.users'
    _inherit = 'res.users'

    def _deparment_ids(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}
        for user in self.browse(cr, uid, ids, context=context):
            for employee in user.employee_ids:
                res[user['id']] = employee.department_id.id
                break;
        return res

    _columns = {
        'department_ids': fields.function(_deparment_ids, type="int", string='Dependencias'),
    }

res_users()

class hr_department(osv.osv):
    _name = "hr.department"
    _inherit = ['hr.department']

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name','abreviatura'], context=context)
        res = []
        for record in reads:
            name = record['abreviatura']
            res.append((record['id'], name))
        return res

    def _dept_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['abreviatura']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return dict(res)

    _columns = {
        'codigo': fields.integer('Código Dependencia', required=True),
        'abreviatura': fields.char('Abreviatura', size=20, required=True),
    }

hr_department()


class plan_contratacion_idu_item_solicitud_cambio(osv.osv):
    _name = "plan_contratacion_idu.item_solicitud_cambio"
    _table = 'plan_contr_item_solicitud_cambio'
    _inherit = ['mail.thread']
    _track = {
        'state': {
            'plan_contratacion_idu.item_solicitud_cambio_borrador': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['borrador'],
            'plan_contratacion_idu.item_solicitud_cambio_radicado': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['radicado'],
            'plan_contratacion_idu.item_solicitud_cambio_rechazado': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['rechazado'],
            'plan_contratacion_idu.item_solicitud_cambio_aprobado': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['aprobado'],
        },
    }

    _rec_name = 'tipo'
    #===========================================================================
    # Despues de instalar el módulo se requiere ejecutar:
    # ALTER TABLE plan_contr_item_solicitud_cambio ADD COLUMN id serial;
    # ALTER TABLE plan_contr_item_solicitud_cambio ADD PRIMARY KEY (id);
    # Ya que al utilizarse la tabla en una relacion m2m en plan_item, el id no se genera y es necesario para manejar este objeto de negocio.
    #===========================================================================
    def _auto_init(self, cr, context=None):
        res = super(plan_contratacion_idu_item_solicitud_cambio, self)._auto_init(cr, context=context)
        pk_sql = """
            DO $$
                BEGIN
                    BEGIN
                        ALTER TABLE plan_contr_item_solicitud_cambio ADD COLUMN id serial;
                        ALTER TABLE plan_contr_item_solicitud_cambio ADD PRIMARY KEY (id);
                    EXCEPTION
                        WHEN duplicate_column THEN RAISE NOTICE 'column id already exists in plan_contr_item_solicitud_cambio';
                    END;
                END;
            $$
        """
        cr.execute(pk_sql)
        return res

    _columns = {
        'tipo':fields.selection([
                ('modificar', 'Modificar el item'),
                ('eliminar', 'Eliminar el item'),
                ('adicionar', 'Crear un nuevo item'),
            ],
            'Tipo de cambio',
            track_visibility='onchange',
            readonly= True
        ),
        'state':fields.selection([
                ('borrador', 'Inicial'),
                ('radicado', 'Radicado y pendiente de revisión'),
                ('rechazado', 'Rechazado'),
                ('aprobado', 'Aprobado')
            ],
            'Estado',
             required=True,
             track_visibility='onchange',
             readonly= True
         ),
        'plan_id': fields.many2one('plan_contratacion_idu.plan','Plan en el que se radica la solicitud de cambio',
             select=True,
             required=True,
             readonly= True
         ),
        'plan_item_id': fields.many2one('plan_contratacion_idu.item','Item a cambiar',
             select=True,
             required=False,
             readonly= True
         ),
        'item_nuevo_id': fields.many2one('plan_contratacion_idu.item','Item con los cambios solicitados',
             select=True,
             required=False,
             readonly= True
        ),
    }

    def aplicar_cambio(self, cr, uid, ids, context=None):
        records = self.browse(cr, uid, ids, context=context)
        plan_item_pool = self.pool.get('plan_contratacion_idu.item')
        for record in records:
            if record.tipo == 'modificar':
                self._aplicar_modificacion(cr, uid, record, context=context)
            elif record.tipo == 'eliminar':
                plan_item_pool.write(cr, uid, [record.plan_item_id.id], {'state': 'no_realizado'}, context=context)
                plan_item_pool.message_post(cr, uid, [record.plan_item_id.id], 
                    'Eliminado', 'Eliminado de acuerdo a la solicitud de cambio id:{0}'.format(record.id), context=context)
            elif record.tipo == 'adicionar':
                plan_item_pool.write(cr, uid, [record.plan_item_id.id], {'state': 'aprobado'}, context=context)
                plan_item_pool.message_post(cr, uid, [record.plan_item_id.id], 
                    'Aprobado', 'Aprobado de acuerdo a la solicitud de cambio id:{0}'.format(record.id), context=context)

        return {
            'type': 'ir.actions.act_window_close',
         }

    def rechazar_cambio(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {
                                  "state": "rechazado",
                }
        )

    def _aplicar_modificacion(self, cr, uid, solicitud, context=None):
        plain_fields = [
            'a_monto_agotable',
            'cantidad_meta_fisica',
            'codigo_unspsc',
            'description',
            'fecha_programada_acta_inicio',
            'fecha_programada_crp',
            'fecha_programada_radicacion',
            'localizacion',
            'no_aplica_unidad_mf',
            'plazo_de_ejecucion',
            'presupuesto',
        ]
        o2m_fields = [
            'centro_costo_id',
            'fuente_id',
            'tipo_proceso_id',
            'tipo_proceso_seleccion_id',
            'unidad_meta_fisica_id',
        ]
        m2o_fields = [
            'plan_pagos_item_ids',
        ]
        m2m_fields = [
            'localidad_ids'
        ]
        values = {}
        plan_pagos_pool = self.pool.get('plan_contratacion_idu.plan_pagos_item')
        plan_item_pool = self.pool.get('plan_contratacion_idu.item')
        item = solicitud.plan_item_id
        cambio = solicitud.item_nuevo_id
        for field in plain_fields:
            if getattr(item, field) != getattr(cambio, field):
                values[field] = getattr(cambio, field)
        for field in o2m_fields:
            if getattr(item, field).id != getattr(cambio, field).id:
                values[field] = getattr(cambio, field).id
        for field in m2o_fields:
            m2o_origen_ids = [ i.id for i in getattr(item, field)]
            m2o_cambio_ids = [ i.id for i in getattr(cambio, field)]
            plan_pagos_pool.unlink(cr, uid, m2o_origen_ids, context=context)
            for i in m2o_cambio_ids:
                plan_pagos_pool.copy(cr, uid, i, default={
                    'plan_contratacion_item_id':item.id,
                }, context=context)
        for field in m2m_fields:
            m2m_origen_ids = [ i.id for i in getattr(item, field)]
            m2m_cambio_ids = [ i.id for i in getattr(cambio, field)]
            if set(m2m_origen_ids) != set(m2m_cambio_ids):
                values[field] = [(6, 0, m2m_cambio_ids)]#http://stackoverflow.com/a/9387447
        plan_item_pool.write(cr, uid, [item.id], values, context=context)
        self.write(cr, uid, [solicitud.id], {'state': 'aprobado'}, context=context)

plan_contratacion_idu_item_solicitud_cambio()
