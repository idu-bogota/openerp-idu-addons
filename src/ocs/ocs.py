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
# Generated by the OpenERP plugin for Dia ! and modified by Andres Ignacio Baez
from osv import fields,osv
from base_geoengine import geo_model
from datetime import datetime
from datetime import timedelta
from crm import crm
from crm_claim import crm_claim

class Res_Partner(osv.osv):
    """Add Partner Identificator for Colomb        ia """
    _name="res.partner"
    _inherit="res.partner"
    _columns={
        'partner_identificator':fields.char('Company Identificator',size=64,help="Useful in Colombia to Store (NIT-Numero de Identificacion Tributaria)")
     }

class ResPartnerAddress(geo_model.GeoModel):
    """This class inherhits from res.partner.address"""
    def name_get(self, cr, user, ids, context=None):
        """Get Full Name of Citizen """        
        if context is None:
            context = {}
        if not len(ids):
            return []
        res = []
        for r in self.read(cr, user, ids, ['name','last_name','document_id','zip','country_id', 'city','partner_id', 'street']):
            if context.get('contact_display', 'contact')=='partner' and r['partner_id']:
                res.append((r['id'], r['partner_id'][1]))
            else:
                # make a comma-separated list with the following non-empty elements
                #elems = [r['name'],r['last_name'],r['document_id'],r['country_id'] and r['country_id'][1], r['city'], r['street']]
                elems = [r['name'],r['last_name'],r['document_id']]
                addr = ', '.join(filter(bool, elems))
                if (context.get('contact_display', 'contact')=='partner_address') and r['partner_id']:
                    res.append((r['id'], "%s: %s" % (r['partner_id'][1], addr or '/')))
                else:
                    res.append((r['id'], addr or '/'))
        return res
    
       
       
    def _get_full_name(self,cr,uid,ids,fieldname,arg,context=None):
        """Get Full Name of Citizen """
        res = {}
        for citizen in self.browse(cr, uid, ids, context = context):
            if citizen.last_name == False:
                res[citizen.id] = "{0}".format(citizen.name)
            else:
                res[citizen.id] = "{0},{1}".format(citizen.last_name, citizen.name)             
        return  res
    
    
    def _checkinputdata(self, cr, uid, ids, context = None):
        """
        This constraint allow evaluate at least one of these data.         
        """        
        is_valid_data = False
        for citizen in self.browse(cr,uid,ids,context=None):
            if ((citizen.email != False)|
                (citizen.twitter != False)|
                (citizen.phone != False)|
                (citizen.facebook != False)|
                (citizen.mobile != False)):                    
                is_valid_data = True                    
        return is_valid_data
    
    _name = 'res.partner.address'
    _inherit='res.partner.address' 
    _columns = {
        'last_name':fields.char('Last Name:',size=128,required=True), 
        'name':fields.char('First Name',size=128,required=True), 
        'gender':fields.selection([('m','Male'),('f','Female')],'Gender'),                     
        'document_id': fields.char('Document Number', size=64,selectable=True),
        'document_type': fields.selection([('C','CC'),('T','T.I'),('P','Passport'),('E','CE'),('N','NIT')],'Document Type',help='Type of Identification Document for example: CC,TI.. etc'),        
        'twitter': fields.char('Twitter', size=64),
        'facebook':fields.char('Facebook:',size=240),        
        'district_id':fields.many2one('ocs.district','District'),        
        'neighborhood_id':fields.many2one('ocs.neighborhood','Neighborhood'),
        'full_name':fields.function(_get_full_name,type='char',string='Full Name',method=True),
        'geo_point':fields.geo_point('Location',srid=4668,readonly=True),
        #'issue_comment': fields.one2many('cso.issue_comment','issue_id','Comments',help="comment to issue"),
        'claim_id':fields.one2many('crm.claim','id','Historic of Claims',help="Claims opened by User")         
    } 
    _rec_name = 'document_id'          
    _order= "last_name asc"
    _sql_constraints = [
        ('unique_cc_document_id','unique(document_type,document_id)','Combination document type, document id must be unique!!!')    
    ]   
    _constraints = [
     (_checkinputdata,'You must type at least one of these: email, phone, cell phone, facebook or twitter to create a contact',['document_id']),
    ]
     
ResPartnerAddress()


class ocs_citizen_service_point(geo_model.GeoModel):
    """Point of Citizen Service"""
    _name = 'ocs.citizen_service_point'
    _columns = {     
        'name': fields.char('Description',size=128,help='Description of Citizen Service Point point',required=True),   
        'creation_date': fields.datetime('Creation Date',help='Date when Citizen Atention Point is installed'),        
        'close_date': fields.datetime('End Date',help='When citizen Atention Point is closed'),
        'schedule': fields.char('Schedule',size=60,help='For example L-V 8:30 am -12:50 pm'),       
        'geo_point':fields.geo_point('Location',srid=4668,readonly=True),
    }
ocs_citizen_service_point()

class ocs_claim_classification(osv.osv):
    """This field contains internal classification for claims """
    _name="ocs.claim_classification"
    _columns={
      'id':fields.integer('ID',readonly=True),
      'code':fields.char('Code',size=6),
      'name':fields.char('Name',size=128),
      'enabled':fields.boolean('Enabled',help='If item is valid now'),
      'parent_id':fields.many2one('ocs.claim_classification','Parent')
    }    
    constraints = [
        (osv.osv._check_recursion,'Error ! You cannot create recursive Claim Classification Category',['parent_id'])
    ]    
ocs_claim_classification()

class ocs_neighborhood(geo_model.GeoModel):
    """Contains geographic information about all towns in the city"""
    _name = 'ocs.neighborhood'
    _columns = {        
        'code': fields.char('Neighborhood Code',size=30,help='Identify a Cadastral Code'),        
        'name': fields.char('Neighborhood Name', size = 128),
        'geo_polygon':fields.geo_multi_polygon('Geometry',srid=4668),
    }
ocs_neighborhood()

class ocs_district(geo_model.GeoModel):
    """ Contaihow to delete a field from parent class openerpns geografic information about localities"""
    _name = 'ocs.district'
    _columns = {       
        'code': fields.char('District Code',size=30),
        'name': fields.char('District Name',size=20),
        'geo_polygon':fields.geo_multi_polygon('Geometry',srid=4668),           
    }
ocs_district()

class ocs_sub_district(geo_model.GeoModel):
    """ Contains geografic information about especific territories """
    _name = 'ocs.sub_district'
    _columns= {
        'name' : fields.char('Sub District Name :',size=150, help='Sub-District name'),
        'code' : fields.char('Territory Code :',size=150,help='Territory Code'),
        'geo_polygon':fields.geo_multi_polygon('Geometry',srid=4668),    
    } 
ocs_sub_district()

class crm_claim(geo_model.GeoModel):
   _name = "crm.claim"
   _inherit = "crm.claim"   
   def _get_full_name(self,cr,uid,ids,fieldname,arg,context=None):
        """Get Full Name of Citizen """
        res = {}
        for citizen in self.browse(cr, uid, ids, context = context):
                res[citizen.id] = "{0}/{1} ".format(citizen.classification_id.name,citizen.sub_classification_id.name)                         
        return  res   
   def _get_channel(self, cr, uid, context=None):
       obj = self.pool.get('ocs.input_channel')
       ids = obj.search(cr, uid, [])
       res = obj.read(cr, uid, ids, ['name', 'id'], context)
       res = [(r['id'], r['name']) for r in res]
       return res   
   def _get_main_classification(self, cr, uid, context=None):
       """This function get the main Categories
      Select name,id from ocs_claim_classification where 
      parent_id = null 
      """
       obj = self.pool.get('ocs.claim_classification_id')
       ids = obj.search(cr, uid, [('parent_id','=',False)])
       result = obj.read(cr, uid, ids, ['name','id'], context)
       return [(r['id'], r['name']) for r in result]       
   
   _columns={
        'description': fields.text('Description',required=True),
        'priority': fields.selection([('h','High'),('n','Normal'),('l','Low')], 'Priority', required=True),
        'external_id':fields.char('External ID',size=128,help='External Claim System Identificator'),
        'external_dms_id': fields.char('External DMS ID',size=20,help='External Document Management System Identificator'),
        'csp_id':fields.many2one('ocs.citizen_service_point','CSP',domain="[('close_date','=',False)]",help='Citizen Service Point',required=True),
        'channel':fields.many2one('crm.case.channel','Case Channel',help='Case Channel',required=True),
        'categ_id': fields.many2one('crm.case.categ', 'Category', \
                            domain="[('section_id','=',section_id),\
                            ('object_id.model', '=', 'crm.claim')]",required=True),
              
        'claim_address':fields.char('Claim Address',size=256,help='Place of Claim'),
        'district_id':fields.many2one('ocs.district','District'),        
        'neighborhood_id':fields.many2one('ocs.neighborhood','Neighborhood'),
        'geo_point':fields.geo_point('Location',srid=4668,readonly=True),
        'classification_id':fields.many2one('ocs.claim_classification','Classification', \
                                               domain="[('parent_id','=',False),('enabled','=',True)]", required=True),
        'sub_classification_id':fields.many2one('ocs.claim_classification','Sub Classification',domain="[('parent_id','=',classification_id),('enabled','=',True)]", required=True),
        'name':fields.function(_get_full_name,type='char',string='Full Name',method=True)
    }   
   _rec_name = 'classification'
   #time.strftime('%Y-%m-%d %H:%M:%S')
   _defaults = {
        'date_deadline': lambda *a:  (datetime.now()+timedelta(days=9)).__format__('%Y-%m-%d %H:%M:%S'),
        'priority': lambda *a: 'l'
        }
   
   def test_response(self, cr, uid, ids, *args):
       """
       Check if Response Text is Empty      
       """       
       isResponsed = False
       for claim in self.browse(cr,uid,ids,context=None):
           response = claim.resolution
           if response == False:
               isResponsed = False
               message = "Resolution could not be Empty"
           else:
               isResponsed = True
               message = "The claim: {0} -- has been closed".format(claim.name)
       self.log(cr, uid, claim.id, message)
       return isResponsed
   
crm_claim()


