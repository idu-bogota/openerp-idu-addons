# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
# INSTITUTO DE DESARROLLO URBANO - BOGOTA (COLOMBIA)
#
# Customization developed by:
# ANGEL MARIA FONSECA CORREA - CIO
# ANDRES IGNACIO BAEZ ALBA - Engineer of Development
# CINXGLER MARIACA MINDA - Engineer of Development - Architect
#
###############################################################################

from osv import fields,osv
from crm import crm
from crm_claim import crm_claim

class crm_claim(osv.osv):
    _name = "crm.claim"
    _inherit = "crm.claim"

    _columns = {
        'orfeo_id': fields.char('Orfeo Number',size=20,help='Número de Radicado en el sistema Orfeo',readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'accion_juridica_id': fields.many2one('ocs_orfeo.accion_juridica','Acción Juridica'),
    }

    def _custom_new_from_data(self, cr, uid, data, context = None):
        """
        llamado desde crm_claim.new_from_data para adicionar lógica en clases hijas
        Retorna {data} o Exception
        """
        search_for_orfeo = {
            'medio_recepcion_id': {'class': 'crm.case.channel', 'ignore_not_found': False, 'crm_claim_field': 'channel', 'type': 'id'},
            'tipo_requerimiento_id': {'class': 'crm.case.categ', 'ignore_not_found': False, 'crm_claim_field': 'categ_id', 'type': 'id'},
            'subcriterio_id': {'class': 'ocs.claim_classification', 'ignore_not_found': False, 'crm_claim_field': 'sub_classification_id', 'type': 'id'},
            'nombre_localidad': {'class': 'ocs.district', 'ignore_not_found': True, 'operator': 'ilike', 'crm_claim_field': 'district_id', 'type': 'name'},
            'nombre_barrio': {'class': 'ocs.neighborhood', 'ignore_not_found': True, 'operator': 'ilike', 'crm_claim_field': 'neighborhood_id', 'type': 'name'},
        }
        data = self._search_details_for_orfeo(cr, uid, data, search_for_orfeo, context)

        search_for_orfeo_ctz = {
            'nombre_localidad': {'class': 'ocs.district', 'ignore_not_found': True, 'operator': 'ilike', 'crm_claim_field': 'district_id', 'type': 'name'},
            'nombre_barrio': {'class': 'ocs.neighborhood', 'ignore_not_found': True, 'operator': 'ilike', 'crm_claim_field': 'neighborhood_id', 'type': 'name'},
        }
        if 'partner_address_id' in data:
            data['partner_address_id'] = self._search_details_for_orfeo(cr, uid, data['partner_address_id'], search_for_orfeo_ctz, context)

        if 'orfeo_id' in data and data['orfeo_id'] > 0:
            solution = self.pool.get('ocs.claim_solution_classification').name_search(cr, uid, name='Redireccionado Internamente', args=None, operator='=', context=None)
            data['solution_classification_id'] = solution[0][0]
            data['resolution'] = 'Requerimiento creado en el sistema orfeo con el número: {0}'.format(data['orfeo_id'])
            data['state'] = 'done';
            data['priority'] = 'l';

        return data

    def _search_details_for_orfeo(self, cr, uid, data, search_for_orfeo, context = None):
        for f in search_for_orfeo.keys():
            if f in data:
                if search_for_orfeo[f]['type'] == 'id':
                    args = [('orfeo_id', '=', data[f])]
                    objs = self.pool.get(search_for_orfeo[f]['class']).search(cr, uid, args, context, limit=1)
                else:
                    objs = self.pool.get(search_for_orfeo[f]['class']).name_search(cr, uid, name=data[f], args=None, operator=search_for_orfeo[f]['operator'], context=None, limit=1)
                if(not len(objs)):
                    if search_for_orfeo[f]['ignore_not_found']:
                        del data[f] #remove not found value
                    else:
                        raise Exception('not found "{0}" for field "{1}"'.format(data[f], f))
                else:
                    if search_for_orfeo[f]['type'] == 'id':
                        data[search_for_orfeo[f]['crm_claim_field']] = objs[0] #assign found object's id
                    else:
                        data[search_for_orfeo[f]['crm_claim_field']] = objs[0][0] #assign found object's id

        return data


crm_claim()

class ocs_orfeo_dependencia(osv.osv):
    _name = "ocs_orfeo.dependencia"

    _columns = {
      'id':fields.integer('ID',readonly=True),
      'code':fields.char('Code',size=6),
      'name':fields.char('Name',size=128),
    }
ocs_orfeo_dependencia()

class ocs_orfeo_accion_juridica(osv.osv):
    _name = "ocs_orfeo.accion_juridica"

    _columns = {
      'id':fields.integer('ID',readonly=True),
      'name':fields.char('Name',size=128),
    }
ocs_orfeo_dependencia()

class ocs_claim_classification(osv.osv):
    _name="ocs.claim_classification"
    _inherit = "ocs.claim_classification"
    _columns={
      'orfeo_id':fields.integer('orfeo_id'),
    }
ocs_claim_classification()

class crm_case_channel(osv.osv):
    _name = "crm.case.channel"
    _inherit="crm.case.channel"
    _columns={
      'orfeo_id':fields.integer('orfeo_id'),
    }
crm_case_channel()

class crm_case_categ(osv.osv):
    _name="crm.case.categ"
    _inherit="crm.case.categ"
    _columns={
        'orfeo_id':fields.integer('orfeo_id'),
    }
crm_case_categ()