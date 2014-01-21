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
import mimetypes
from mimetypes import guess_type

class ocs_sdqs_wizard_radicar(osv.osv_memory):
    _name = 'ocs_sdqs.wizard.radicar'
    _description = 'Radica la PQR EN (SDQS)'

    _columns = {
        'description': fields.text('Description', help='Texto a ser radicado', required=True),
        'folios':fields.integer('folios', help='Numero de folios', required=True),
        'partner_forwarded_id': fields.many2one('res.partner', 'Partner Forwarded',domain="[('supplier','=',True)]",),
    }

    def default_get(self, cr, uid, fields, context=None):
        claim = self.pool.get('crm.claim').browse(cr, uid, context['active_id'], context=None);
        res = super(ocs_sdqs_wizard_radicar, self).default_get(cr, uid, fields, context=context)
        res.update({'description': claim.description })
        res.update({'partner_forwarded_id': claim.partner_forwarded_id.id })
        return res

    def radicar(self, cr, uid, ids, context=None):
        wsdl_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'sdqs.ws.url', default='', context=context)
        sdqs_token = self.pool.get('ir.config_parameter').get_param(cr, uid, 'sdqs.token', default='', context=context)
        attach_pool = self.pool.get('ir.attachment')
        attach_id = attach_pool.search(cr, uid,[('res_id', '=', context['active_id'])])
        client = SdqsClient(wsdl_url,sdqs_token)

        current_user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        claim_ids = context and context.get('active_ids', False)
        claim_table = self.pool.get('crm.claim')
        citizen = self.pool.get('res.partner.address').browse(cr, uid, uid)
        form_object_id = ids and ids[0] or False
        form_object = self.browse(cr, uid, form_object_id, context=context)
        asunto = form_object.description.strip()
        if(len(asunto) > 300):
            raise osv.except_osv('Error de validación','El texto a ser radicado es demasiado largo, por favor resumalo')

        for claim in claim_table.browse(cr, uid, claim_ids, context=context):
            if claim.sdqs_id != u'0' and claim.sdqs_id != False:
                raise osv.except_osv('Error!', 'La PQR ya tiene un número de rádicado')
            
            ciudadano = claim.partner_address_id
            categoria = claim.categ_id

            if ciudadano:
                if ciudadano.document_number:
                    numero_documento = ciudadano.document_number
                else:
                    numero_documento = 1
                if ciudadano.name:
                    nombre_ciudadano = ciudadano.name
                else:
                    nombre_ciudadano = ""
                if ciudadano.last_name:
                    apellido_ciudadano = ciudadano.last_name
                else:
                    apellido_ciudadano = ""
                if ciudadano.email:
                    correo_ciudadano = ciudadano.email
                else:
                    correo_ciudadano = ""
                if ciudadano.phone:
                    telefono_ciudadano = ciudadano.phone
                else:
                    telefono_ciudadano = ""
            if form_object:
                if form_object.folios:
                    foliosSDQS = form_object.folios
                else:
                    foliosSDQS = 1
                if form_object.description:
                    descripcion_sdqs = form_object.description
                else:
                    descripcion_sdqs = "Sin descripcion"

            if claim:
                if claim.claim_address:
                    direccion_reclamo = claim.claim_address
                else:
                    direccion_reclamo = "Sin direccion"
                if claim.id:
                    numero_radicado = claim.id
                else:
                    numero_radicado = 0

            if categoria:
                codigo_tipo_requerimiento = categoria.sdqs_req_type 
            else:
                codigo_tipo_requerimiento = 1

            params = {
            "numeroRadicado": numero_radicado,
            "numeroFolios": foliosSDQS,        
    
            "asunto": descripcion_sdqs.strip(),
            "numeroDocumento": numero_documento,
            "nombres": nombre_ciudadano,
            "apellidos": apellido_ciudadano,
            "email": correo_ciudadano,
            "telefonoCasa": telefono_ciudadano,
            "telefonoOficina": "000000000",
            "telefonoCelular": "000000000",
            "direccion": direccion_reclamo,
            "codigoCiudad": "11001",
            "codigoDepartamento": "250",
            "codigoPais": "1",
            "codigoTipoRequerimiento": codigo_tipo_requerimiento,
            #===================================================================
            # "clasificacionRequerimiento": {
            # "codigoSector": [11],
            # "codigoEntidad": [143],
            # "codigoSubtema": [4],
            # },
            #===================================================================
            "observaciones": descripcion_sdqs,
            "prioridad": "2",
            "entidadQueIngresaRequerimiento": 2972,
            }

            try:
                result = client.registrarRequerimiento(params)
                if result['codigoRequerimiento'] > 0:                    
                    mimetypes.init()
                    for id in attach_id:
                        file = attach_pool.browse(cr, uid, id, context=None);
                        resultado = client.adjuntarArchivoEnRequerimiento(result['codigoRequerimiento'], file.datas, file.name,guess_type(file.name)[0])
                        if resultado['codigoError'] > 0:
                            raise osv.except_osv('Error retornado por el sistema SDQS al adjuntar el archivo:' + file.name, result['codigoError'])
                    claim_table.write(cr, uid, claim.id, {'sdqs_id': result['codigoRequerimiento']}, context=context)
                else:
                    raise osv.except_osv('Error retornado por el sistema SDQS', result['codigoError'])
            except Exception as e:
                raise osv.except_osv('Error al consultar servicio web SDQS', str(e))

        return {'type': 'ir.actions.act_window_close'}

ocs_sdqs_wizard_radicar()
