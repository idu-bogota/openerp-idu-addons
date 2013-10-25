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
from lxml import etree

class ocs_idu_wizard_classify_damage(osv.osv_memory):
    _name = 'ocs_idu.wizard.classify_damage'
    _description = 'Radica la PQR como en el sistema de gestión documental Orfeo'

    _columns = {
        'id':fields.integer('Identifier'),
        'dependencia_id':fields.many2one('ocs_orfeo.dependencia', 'Dependencia', required=True),
        'res_user_id': fields.many2one('res.users', 'Responsable', required=True),
        'classification_id': fields.many2one('ocs.claim_damage_classification', 'Clasificación del daño'),
        'description': fields.text('Descripción', required=True),
    }

    def default_get(self, cr, uid, fields, context=None):
        """
        Get default values to fill the form
        """
        res = super(ocs_idu_wizard_classify_damage, self).default_get(cr, uid, fields, context=context)
        image_field = None
        if 'active_id' in context:
            claim_id = context['active_id']
        else:
            #request asking for image
            image_field = fields[0]
            claim_id = image_field.split('_')[1] #extract claim_id from field name like image_1234

        claim = self.pool.get('crm.claim').browse(cr, uid, claim_id, context)
        if claim_id != None:
            res.update({'description': claim.description})

        #TODO: Hacer geoprocesamiento 
        #TODO: Crear una respuesta de acuerdo al geoprocesamiento
        #TODO: Preseleccionar Dependencia de acuerdo al resultado del geoprocesamiento
        #TODO: Crear wizard para aprobar respuesta propuesta por el sistema claim cambia de estado a pending y cuando se aprueba respuesta cambia a in progress, enviando email al claim.responsible
        if image_field != None:
            attachment_id = self.pool.get('ir.attachment').search(cr, uid, [('res_model', '=', 'crm.claim'), ('res_id', '=', claim_id)])
            attachment = self.pool.get('ir.attachment').read(cr, uid, attachment_id, ['datas'], context = context)[0]
            res.update({image_field: attachment.get('datas','')})

        return res

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        """
            Add field to display the image uploaded by the user
        """
        result = super(ocs_idu_wizard_classify_damage, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
        attachment_id = self.pool.get('ir.attachment').search(cr, uid, [('res_model', '=', 'crm.claim'), ('res_id', '=', context['claim_id'])])
        if(attachment_id):
            xml = etree.fromstring(result['arch'])
            image_identifier = "image_{0}".format(context['claim_id'])
            result['fields'][image_identifier] = {
                'domain': [],
                'string': 'Fotografía',
                'type': 'binary',
                'context': {},
                'required': False,
                'readonly': True,
            }
            photo = etree.Element("field", name=image_identifier, widget="image", attrs="{'readonly': 1}", colspan="4")
            xml.insert(0,photo)
            result['arch'] = etree.tostring(xml)
        return result

    def onchange_dependencia_id(self, cr, uid, ids, dependencia_id):
        """
        Selecciona listado de usuarios basado en la dependencia
        """
        v={}
        d={}
        if dependencia_id:
            users = self.pool.get('res.users').search(cr, uid, [('dependencia_id','=',dependencia_id)])
            d['res_user_id'] = "[('id','in',{0})]".format(users)
        return {'domain':d, 'value':v}

    def radicar(self, cr, uid, ids, context=None):
        current_user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        claim_ids = context and context.get('active_ids', False)
        claim_table = self.pool.get('crm.claim')
        damage_table = self.pool.get('ocs.claim_damage')

        form_object_id = ids and ids[0] or False
        form_object = self.browse(cr, uid, form_object_id, context=context)
        description = form_object.description.strip()
        usuario_destino = form_object.res_user_id
        classification = form_object.classification_id
        dependencia = form_object.dependencia_id

        for claim in claim_table.browse(cr, uid, claim_ids, context=context):
            data = {
                'res_user_id': usuario_destino.id,
                'dependencia_id': dependencia.id,
                'classification_id': classification.id,
                'description': "{0}\n\n----- Datos adicionales reportados por el ciudadano -----\nElemento afectado: {4}\nTipo de daño: {5}\nAncho: {1}\nLargo: {2}\nProfundo: {3}".format(
                                description, claim.damage_width_by_citizen,claim.damage_length_by_citizen,claim.damage_deep_by_citizen,
                                claim.damage_element_by_citizen, claim.damage_type_by_citizen),
                'geo_point': claim.geo_point,
                'element':claim.damage_element_by_citizen,
            }
            attachment_id = self.pool.get('ir.attachment').search(cr, uid, [('res_model', '=', 'crm.claim'), ('res_id', '=', claim.id)])
            if(attachment_id):
                attachment = self.pool.get('ir.attachment').read(cr, uid, attachment_id, ['datas'], context = context)[0]
                data['image'] = attachment.get('datas','')
            damage_id = damage_table.create(cr, uid, data, context)
            #TODO: Enviar email al responsible
            claim_table.write(cr, uid, claim.id, {'damage_id': damage_id}, context=context)

        return {'type': 'ir.actions.act_window_close'}

ocs_idu_wizard_classify_damage()
