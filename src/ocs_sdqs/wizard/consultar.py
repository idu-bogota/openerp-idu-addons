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
# GUSTAVO ADOLFO VELEZ - CIO
# JULIAN ANDRES FERNANDEZ - Engineer of Development
# CINXGLER MARIACA MINDA - Engineer of Development - Architect
#
###############################################################################

from osv import osv, fields
from ocs_sdqs.wsclient.wsclient import SdqsClient

class ocs_sdqs_wizard_consultar(osv.osv_memory):
    _name = 'ocs_sdqs.wizard.consultar'
    _description = 'consulta la PQR EN (SDQS)'    

    _columns = {
        'request_number': fields.integer('Number', help='Numero del requerimiento SDQS', required=True),
    }

    def consultar(self, cr, uid, ids, context=None):
        wsdl_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'sdqs.ws.url', default='', context=context)
        client = SdqsClient(wsdl_url,1)
        form_object_id = ids and ids[0] or False
        form_object = self.browse(cr, uid, form_object_id, context=context)
        claim_table = self.pool.get('crm.claim')
        try:
            consulta = client.consultarRequerimiento(form_object.request_number)
            print consulta
            if consulta['codigoError'] > 0:
                raise osv.except_osv('Error!', 'Error del servicio SDQS:')
            else:
                consulta_fields = ('nombres','apellidos','asunto','codigoCiudad','codigoDepartamento',
                                   'codigoPais','codigoTipoRequerimiento','entidadQueIngresaRequerimiento',
                                   'numeroDocumento','numeroFolios','numeroRadicado','observaciones', 'prioridad'
                                   )
                for f in consulta_fields:
                    claim_table.write(cr, uid, claim_table.id, {f: "test"}, context=context)
        except Exception as e:
            raise osv.except_osv('Error al consultar servicio web SDQS', str(e))

        return {'type': 'ir.actions.act_window_close'}



ocs_sdqs_wizard_consultar()
