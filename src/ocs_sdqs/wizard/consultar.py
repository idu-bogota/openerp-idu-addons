# -*- coding: utf-8 -*-

from osv import osv, fields
from suds.client import Client

class ocs_sdqs_wizard_consultar(osv.osv_memory):
    _name = 'ocs_sdqs.wizard.consultar'
    _description = 'consulta la PQR EN (SDQS)'    

    _columns = {
        'request_number': fields.text('Number', help='Numero del requerimiento SDQS', required=True),
    }
    
    def consultar(self, cr, uid, ids, context=None):
        wsdl_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'sdqs.ws.url', default='', context=context)
        client = Client(wsdl_url)
        form_object_id = ids and ids[0] or False
        form_object = self.browse(cr, uid, form_object_id, context=context)
        claim_table = self.pool.get('crm.claim')
        try:
            consulta = client.consultarRequerimiento(form_object.request_number)
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
                                                  
            #try:              
            #    result = client.registrarRequerimiento(params)
            #    if result['codigoRequerimiento'] > 0:
            #        claim_table.write(cr, uid, claim.id, {'sdqs_id': result['codigoRequerimiento']}, context=context)    
            #    else:
            #        raise osv.except_osv('Error retornado por el sistema SDQS', result['codigoError'])                
            #except Exception as e:
            #    raise osv.except_osv('Error al consultar servicio web SDQS', str(e))

        return {'type': 'ir.actions.act_window_close'}



ocs_sdqs_wizard_consultar()
    