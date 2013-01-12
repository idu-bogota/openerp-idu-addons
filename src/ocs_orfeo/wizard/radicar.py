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

from osv import osv, fields
from suds.client import Client

class ocs_orfeo_wizard_radicar(osv.osv_memory):
    _name = 'ocs_orfeo.wizard.radicar'
    _description = 'Radica la PQR como en el sistema de gestión documental Orfeo'

    _columns = {
        'description': fields.text('Description', help='Texto a ser radicado', readonly=True),
        'dependencia_id':fields.many2one('ocs_orfeo.dependencia', 'Dependencia', required=True),
    }

    def default_get(self, cr, uid, fields, context=None):
        """
        """
        claim = self.pool.get('crm.claim').browse(cr, uid, context['active_id'], context=None);
        res = super(ocs_orfeo_wizard_radicar, self).default_get(cr, uid, fields, context=context)
        res.update({'description': claim.description })
        return res

    def radicar(self, cr, uid, ids, context=None):
        current_user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        claim = self.pool.get('crm.claim').browse(cr, uid, context['active_id'], context=None);
        url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'orfeo.ws.url', default='', context=context)
        destino =  claim.partner_address_id
        client = Client(url)
        usuarioLogin = current_user.login
        tipoRadicacion = 2 #Radicados de entrada
        tipoTercero = 1 #ciudadano 1 y empresas 2
        destinoRemiteNombre = destino.name
        apellidos = destino.last_name.split(' ')
        destinoRemiteApellido1 = apellidos[0]
        destinoRemiteApellido2 = apellidos[1]
        destinoRemiteDireccion = destino.street
        destinoRemiteTelefono = destino.phone
        destinoRemiteEmail = destino.email
        destinoRemiteDocumento = destino.document_number
        municipio = 1 # Bogotá
        departamento = 11 # Distrito Capital
        pais = 170 # Colomba
        continente = 1 # América
        asunto = claim.description

        data_id = ids and ids[0] or False
        data = self.browse(cr, uid, data_id, context=context)
        dependenciaDestino = data.dependencia_id.code

        orfeo_radicar = getattr(client.service, 'OrfeoWs.radicar')
        result = orfeo_radicar(usuarioLogin, tipoRadicacion, tipoTercero, destinoRemiteNombre, destinoRemiteApellido1, destinoRemiteApellido2, destinoRemiteDireccion, destinoRemiteTelefono, destinoRemiteEmail, destinoRemiteDocumento, municipio, departamento, pais, continente, dependenciaDestino, asunto)
        self.pool.get('crm.claim').write(cr, uid, context['active_id'], {'orfeo_id': result['RADICADO']}, context=None)
        return {'type': 'ir.actions.act_window_close'}



ocs_orfeo_wizard_radicar()
