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
from shapely.wkt import dumps,loads
import geojson 

class ocs_mapidu_ciudadano(osv.osv):
    _name="ocs_mapidu.ciudadano"
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
                                           ('pasaporte','Pasaporte'),
                                           ('nit','NIT'),
                                           ]
                                          ,'Tipo de Documento',required=True),
        'documento':fields.char('Documento',size=50,required=True),
        'email':fields.char('E-mail',size=256,),
        'telefono_fijo':fields.char('Telefono fijo',size=30),
        'celular':fields.char('Celular',size=30),
        'direccion':fields.char('Dirección',size=512,),  
        'nombre_completo':fields.function(_get_full_name,type='char',string='Nombre Completo',method=True),
    }

    _sql_constraints = [
        ('unique_cc_document_number','unique(tipo_documento,documento)','Este documento ya se encuentra registrado'),
        ('unique_cc_email','unique(email)','El email ya se encuentra registrado'),
    ]
ocs_mapidu_ciudadano()

class ocs_mapidu_reuniones(osv.osv):
    """
    Reunione sociales
    """
    _name="ocs_mapidu.reuniones"
    _columns={
        'proyecto_id':fields.many2one('ocs_mapidu.proyecto','Proyecto'),
        'tramo_id':fields.many2one('ocs_mapidu.tramo','Tramo'),
        'localidad_id':fields.many2one('base_map.district','Localidad'),
        'lugar':fields.char('Lugar',size=50),
        'fecha':fields.datetime('Fecha'),
        'duracion':fields.float('Duracion (horas)'),
        'descripcion_corta':fields.char('Descripcion (corta)',size=20,required=True),
        'descripcion':fields.text('Descripcion'),
        'asistentes_id':fields.many2many('ocs_mapidu.lideres_sociales','ocs_mapidu_reuniones_lideres_rel','reunion_id','lider_id','Asistentes'),
    }
ocs_mapidu_reuniones()

class ocs_mapidu_lideres_sociales(osv.osv):
    _name="ocs_mapidu.lideres_sociales"
    _inherit="ocs_mapidu.ciudadano"
    _columns = {
        'district_id':fields.many2one('base_map.district','Localidad'),
        'sector':fields.char('Sector al que representa',size=256),
        'photo':fields.binary('Foto'),
    }
ocs_mapidu_lideres_sociales()

class ocs_mapidu_problema_social(geo_model.GeoModel):
    _name="ocs_mapidu.problema_social"
    
    def crear_peticion(self,cr,uid,vals,context=None):
        """
        Metodo consumido por el web service para crear la peticion
        recibe el metodo fraccionado en dos pedazos:
        {ciudadano:{'datos del ciudadano'},
        {problema_social:{'detalles del problema social'}
        """
        ciudadano = {
           'nombres':vals['nombres'],
           'apellidos':vals['apellidos'],
           'documento':vals['documento'],
           'tipo_documento':vals['tipo_documento'],
           'email':vals['email'],
           'telefono_fijo':vals['telefono_fijo'],
           'celular':vals['celular'],
           'direccion':vals['direccion'],
         }
        ciudadano_obj = self.pool.get('ocs_mapidu.ciudadano')
        ids_ciudadano = ciudadano_obj.search(cr,uid,[
                                            ('tipo_documento','=',ciudadano['tipo_documento']),
                                            ('documento','=',ciudadano['documento'])])
        id_ciudadano = 0
        if (len(ids_ciudadano)):
            id_ciudadano = ids_ciudadano[0]
            ciudadano_obj.write(cr,uid,id_ciudadano,ciudadano,context)
        else:
            id_ciudadano = ciudadano_obj.create(cr,uid,ciudadano,context)
        str_shape = vals['shape']
        shape = geojson.loads(str_shape)
        problema_social = {
            'ciudadano_id':id_ciudadano,
            'tipo_problema':vals['tipo_problema'],
            'tipo_problema_movilidad':vals['tipo_problema_movilidad'],
            'ubicacion':vals['ubicacion'],
            'descripcion':vals['descripcion'],
            'shape':str_shape,
            'imagen':vals['attachment']
        }
        id_problema = self.create(cr,uid,problema_social,context)
        return id_problema
    
    _columns={
        'ciudadano_id':fields.many2one('ocs_mapidu.ciudadano','Ciudadano',required=True),
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
        'ubicacion':fields.text('Descripcion sobre la Ubicación'),
        'imagen':fields.binary('Imagen'),
        'descripcion':fields.text('Descripción',required=True),
        'shape':fields.geo_point('Ubicacion',readonly=False),
    }
ocs_mapidu_problema_social()

class ocs_mapidu_proyecto(osv.osv):
    _name="ocs_mapidu.proyecto"
    _rec_name="nombre"
    _columns={
        'nombre':fields.char('Nombre del Proyecto',size=256, required = True),
        'codigo':fields.integer('Codigo de proyecto', required = True),
        'descripcion':fields.text('Descripcion', required =True),
        'tramos':fields.one2many('ocs_mapidu.tramo','proyecto_id','Tramos'),
    }
ocs_mapidu_proyecto()

class ocs_mapidu_tramo(geo_model.GeoModel):
    _name="ocs_mapidu.tramo"
    _rec_name="nombre"
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
ocs_mapidu_matriz_multicriterio()
