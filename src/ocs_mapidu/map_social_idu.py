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
from osv import fields,osv
from base_geoengine import geo_model
import logging
_logger = logging.getLogger(__name__)


class res_partner(osv.osv):
    _name="res.partner"
    _inherit="res.partner"
    _rec_name = "documento"
    
    def name_get(self, cr, user, ids, context=None):
        """Get Full Name of Citizen """
        if context is None:
            context = {}
        if not len(ids):
            return []
        res = []
        for r in self.read(cr, user, ids, ['nombres','apellidos','documento','tipo_documento']):
            if context.get('contact_display', 'contact')=='partner' and r['partner_id']:
                res.append((r['id'], r['partner_id'][1]))
            else:
                # make a comma-separated list with the following non-empty elements
                #elems = [r['name'],r['last_name'],r['document_number'],r['country_id'] and r['country_id'][1], r['city'], r['street']]
                elems = [r['nombres'],r['apellidos'],r['tipo_documento'],r['documento']]
                addr = ', '.join(filter(bool, elems))
                if (context.get('contact_display', 'contact')=='partner_address') and r['partner_id']:
                    res.append((r['id'], "%s: %s" % (r['partner_id'][1], addr or '-no-address-')))
                else:
                    res.append((r['id'], addr or '-no-address-'))
        return res
    
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args:
            args=[]
        if not context:
            context={}
        ids = False
        if name:
            ids = self.search(cr, user, ['|',('documento', 'ilike', name),'|',('nombres', 'ilike', name),'|',('apellidos', 'ilike', name),('email', 'ilike', name)] + args,
                    limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, ['|',('nombres', operator, name),('apellidos', operator, name)] + args,
                    limit=limit, context=context)
        return self.name_get(cr, user, ids, context)
    
    
    def _get_full_name(self,cr,uid,ids,fieldname,arg,context=None):
        """Get Full Name of Citizen """
        res = {}
        for citizen in self.browse(cr, uid, ids, context = context):
            if citizen.apellidos == False and citizen.nombres == False:
                res[citizen.id] = "-"
            elif citizen.nombres == False:
                res[citizen.id] = "{0}".format(citizen.nombres)
            else:
                res[citizen.id] = "{0},{1}".format(citizen.apellidos, citizen.nombres)
        return  res
    
    _columns = {
        'nombres':fields.char('Nombres',size=256,required=True),
        'apellidos':fields.char('Apellidos',size=256,required=True),
        'tipo_documento':fields.selection([
                                           ('cc','Cedula de Ciudadanía'),
                                           ('ti','Tarjeta de Identidad'),
                                           ('ce','Cedula de Extrangería'),
                                           ('nit','NIT'),
                                           ]
                                          ,'Tipo de Documento',required=True),
        'documento':fields.char('Documento',size=50,required=True),
        'email':fields.char('E-mail',size=256,),
        'telefono_fijo':fields.integer('Telefono fijo'),
        'celular':fields.integer('Celular'),
        'direccion':fields.char('Dirección',size=512,),
        'nombre_completo':fields.function(_get_full_name,type='char',string='Nombre Completo',method=True),
    }
    
    _sql_constraints = [
        ('unique_cc_document_number','unique(tipo_documento,documento)','Este documento ya se encuentra registrado'),
        ('unique_cc_email','unique(email)','El email ya se encuentra registrado'),
    ]
res_partner()

class ocs_mapidu_problema_social(geo_model.GeoModel):
    _name="ocs_mapidu.problema_social"
    _columns={
        'ciudadano_id':fields.many2one('res.partner','Ciudadano',required=True),
        'tipo_problema':fields.selection([
                                          ('economico','Economico'),
                                          ('social','Social'),
                                          ('ambiental','Ambiental'),
                                          ('movilidad','Movilidad'),
                                          ]
                                         ,'Tipo de Prolema',required=True),
        'tipo_problema_movilidad':fields.selection([
                                                    ('congestion_vehicular','Congestión Vehícular'),
                                                    ('carencia_semaforos','Carencia de Semaforos'),
                                                    ('puentes_peatonales','Puentes Peatonales'),
                                                    ('senalizacion','Señalizacion'),
                                                    ('dano_malla_vial','Daño en Malla Vial'),
                                                    ],
                                                   'Tipo de Problema de Movilidad'
                                                   ),
        'imagen':fields.binary('Imagen'),
        'descripcion':fields.text('Descripción',required=True),
        'shape':fields.geo_point('Ubicacion',readonly=False),
    }
ocs_mapidu_problema_social()


class ocs_mapidu_reunion(geo_model.GeoModel):
    _name="ocs_mapidu.reunion"
    
    def _get_district(self,cr,uid,ids,fieldname,arg,context=None):
        res = {}
        #Este bloque try es porque a veces los datos vienen con inconsistencia topológica y se pretende evitar que deje de funcionar
        #la página cuando se manda el query, en ves de eso mejor que siga funcionando y deje un log de eventos        
        for reunion in self.browse(cr, uid, ids, context = context):
            try:
                geom = reunion.shape.wkt
                districts=""
                if geom != False:
                    if reunion.shape.is_valid:
                        query = "SELECT name FROM base_map_district WHERE st_intersects(shape,st_geomfromtext('{0}',900913)) = true".format(geom)
                        cr.execute(query)
                        for row in cr.fetchall():
                            districts = row[0]+","+districts
                res[reunion.id] = districts
            except Exception as e:
                _logger.debug("Geoprocessing error: {0}".format(e))
                res[reunion.id] = ""
        return res
    
    _columns={
        'fecha':fields.datetime('Fecha y Hora de Reunion'),  
        'descriptcion':fields.text('Descripcion'),
        'asistentes':fields.many2many('res.partner.address','ocs_mapidu_reunion_partner_rel','reunion_id','asistente_id','Asistentes'),
        'localidad':fields.function(_get_district,string='Districts',method=True,type="char"),
        'shape':fields.geo_point('Lugar'),
    }
ocs_mapidu_reunion()
    

class ocs_mapidu_proyecto(osv.osv):
    _name="ocs_mapidu.proyecto"
    _rec_name="nombre"
    _columns={
        'nombre':fields.char('Nombre del Proyecto',size=256),
        'codigo':fields.integer('Codigo de proyecto'),
        'descripcion':fields.text('Descripcion')
    }
ocs_mapidu_proyecto()

class ocs_mapidu_tramo(geo_model.GeoModel):
    _name="ocs_mapidu.tramo"
    _columns={
        'proyecto_id':fields.many2one('ocs_mapidu.proyecto','Proyecto'),
        'nombre':fields.char('Nombre',size=256),
        'descripcion':fields.text('Descripcion'),
        'shape':fields.geo_polygon('Shape'),
    }
ocs_mapidu_tramo()
    
class ocs_mapidu_reporte_social(osv.osv):
    _name="ocs_mapidu.reporte_social"
    _columns={
        'district_id':fields.many2one('base_map.district','Localidad'),
        'proyecto_id':fields.many2one('ocs_mapidu.proyecto','Proyecto'),
        'tramo_id':fields.many2one('ocs_mapidu.tramo','Tramo'),
        'descripcion':fields.char('Descripcion',size=256),
        'reporte_adjunto':fields.binary('Reporte Social Adjunto'),
        'cartografia':fields.binary('Reporte Cartografia Social'),
    }
ocs_mapidu_reporte_social()

class ocs_mapidu_matriz_multicriterio(osv.osv):
    _name="ocs_mapidu.matriz_multicriterio"
    _columns = {
        'district_id':fields.many2one('base_map.district','Localidad'),
        'proyecto_id':fields.many2one('ocs_mapidu.proyecto','Proyecto'),
        'tramo_id':fields.many2one('ocs_mapidu.tramo','Tramo'),
        'descripcion':fields.char('Descripcion',size=256),
        'adjunto':fields.binary('Adjunto'),
    }
