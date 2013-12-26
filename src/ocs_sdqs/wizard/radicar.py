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
from suds.client import Client

class ocs_sdqs_wizard_radicar(osv.osv_memory):
    _name = 'ocs_sdqs.wizard.radicar'
    _description = 'Radica la PQR EN (SDQS)'    

    _columns = {
        'description': fields.text('Description', help='Texto a ser radicado', required=True),
        'folios':fields.integer('folios', help='Numero de folios', required=True),
    }
    
    def default_get(self, cr, uid, fields, context=None):
        claim = self.pool.get('crm.claim').browse(cr, uid, context['active_id'], context=None);
        res = super(ocs_sdqs_wizard_radicar, self).default_get(cr, uid, fields, context=context)
        res.update({'description': claim.description })
        return res
    
    def radicar(self, cr, uid, ids, context=None):
        wsdl_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'sdqs.ws.url', default='', context=context)
        #client = Client(wsdl_url)

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
                    numeroDocumento = ciudadano.document_number
                else:
                    numeroDocumento = 1
                if ciudadano.name:
                    nombreCiudadano = ciudadano.name
                else:
                    nombreCiudadano = " "
                if ciudadano.last_name:
                    apellidoCiudadano = ciudadano.last_name
                else:
                    apellidoCiudadano = " "
                if ciudadano.email:
                    correoCiudadano = ciudadano.email
                else:
                    correoCiudadano = "nn@nn.com"
                if ciudadano.phone:
                    telefonoCiudadano = ciudadano.phone
                else:
                    telefonoCiudadano = "000000"
            if form_object:
                if form_object.folios:
                    foliosSDQS = form_object.folios
                else:
                    foliosSDQS = 1
                if form_object.description:
                    descripcionSDQS = form_object.description
                else:
                    descripcionSDQS = "Sin descripcion"
            
            if claim:
                if claim.claim_address:
                    direccionReclamo = claim.claim_address
                else:    
                    direccionReclamo = "Sin direccion"
                if claim.id:
                    numeroRadicado = claim.id
                else:              
                    numeroRadicado = 0      
            
            if categoria:
                codigoTipoRequerimiento = categoria.sdqs_req_type 
            else:
                codigoTipoRequerimiento = 1
            
            params = {
            "numeroRadicado": numeroRadicado,
            "numeroFolios": foliosSDQS,        
            "asunto": descripcionSDQS.strip(),
            "numeroDocumento": numeroDocumento,
            "nombres": nombreCiudadano,
            "apellidos": apellidoCiudadano,
            "email": correoCiudadano,
            "telefonoCasa": telefonoCiudadano,
            "telefonoOficina": "000000000",
            "telefonoCelular": "000000000",
            "direccion": direccionReclamo,
            "codigoCiudad": "11001",
            "codigoDepartamento": "250",
            "codigoPais": "1",
            "codigoTipoRequerimiento": codigoTipoRequerimiento,
            "clasificacionRequerimiento": {
            "codigoSector": [11],
            "codigoEntidad": [143],
            "goSubtema": [4],
            },
            "observaciones": descripcionSDQS,
            "prioridad": "2",
            "entidadQueIngresaRequerimiento": 2972,
            }
                                  
            #try:              
            #    result = client.registrarRequerimiento(params)
            #    if result['codigoRequerimiento'] > 0:
            #        claim_table.write(cr, uid, claim.id, {'sdqs_id': result['codigoRequerimiento']}, context=context)    
            #    else:
            #        raise osv.except_osv('Error retornado por el sistema SDQS', result['codigoError'])                
            #except Exception as e:
            #    raise osv.except_osv('Error al consultar servicio web SDQS', str(e))

        return {'type': 'ir.actions.act_window_close'}



ocs_sdqs_wizard_radicar()
    