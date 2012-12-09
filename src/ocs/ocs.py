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
from base_geoengine import geo_model
from datetime import datetime
from datetime import timedelta
from crm import crm
from crm_claim import crm_claim
import re

class crm_case_channel(osv.osv):
    _name = "crm.case.channel"
    _inherit="crm.case.channel"
    _order = 'id'

class ResPartnerAddress(geo_model.GeoModel):
    """This class inherhits from res.partner.address"""
    def name_get(self, cr, user, ids, context=None):
        """Get Full Name of Citizen """
        if context is None:
            context = {}
        if not len(ids):
            return []
        res = []
        for r in self.read(cr, user, ids, ['name','last_name','document_number','zip','country_id', 'city','partner_id', 'street']):
            if context.get('contact_display', 'contact')=='partner' and r['partner_id']:
                res.append((r['id'], r['partner_id'][1]))
            else:
                # make a comma-separated list with the following non-empty elements
                #elems = [r['name'],r['last_name'],r['document_number'],r['country_id'] and r['country_id'][1], r['city'], r['street']]
                elems = [r['name'],r['last_name'],r['document_number']]
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

    def _checkdocument(self, cr, uid, ids, context = None):
        """
        Constraint:

        Document Number Regex Validation
        """
        is_valid_document = False
        for citizen in self.browse(cr, uid, ids,context=None):
            if citizen.document_type == 'C' :
                if citizen.document_number != False:
                    if re.match("^[0-9]+$", citizen.document_number) != None:
                        is_valid_document = True
                    else:
                        is_valid_document = False #Empty document are permited....
            else:
                is_valid_document = True
        return is_valid_document

    def _checkinputdata(self, cr, uid, ids, context = None):
        """
        Constraint:
        Should have filled at least one contact detail
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
        'document_number': fields.char('Document Number', size=64,selectable=True),
        'document_type': fields.selection([('C','CC'),('T','T.I'),('P','Passport'),('E','CE')],'Document Type',help='Identification Document Type. ie CC,TI.. etc'),
        'twitter': fields.char('Twitter', size=64),
        'facebook':fields.char('Facebook:',size=240),
        'district_id':fields.many2one('ocs.district','District'),
        'neighborhood_id':fields.many2one('ocs.neighborhood','Neighborhood'),
        'full_name':fields.function(_get_full_name,type='char',string='Full Name',method=True),
        'geo_point':fields.geo_point('Location',srid=4668,readonly=True),
        'claim_id':fields.one2many('crm.claim','id','Historic of Claims',help="Claims opened by User")
    }
    _rec_name = 'document_number'
    _order= "last_name asc"
    _sql_constraints = [
        ('unique_cc_document_number','unique(document_type,document_number)','Combination document type, document id must be unique!!!'),
        ('unique_email','unique(email)','This email is already registered'),
    ]
    _constraints = [
    (_checkinputdata,'You must type at least one of these: email, phone, cell phone, facebook or twitter to create a contact',['document_number']),
    (_checkdocument,'When Document Type is CC, the document number must be numeric only!!!',['document_number']),
    ]
ResPartnerAddress()


class ocs_citizen_service_point(geo_model.GeoModel):
    """Citizen Service Point"""
    _name = 'ocs.citizen_service_point'
    _columns = {
        'name': fields.char('Name',size=128,help='Description of Citizen Service Point',required=True),
        'creation_date': fields.datetime('Creation Date',help='Date when Citizen Service Point is installed',required=True),
        'close_date': fields.datetime('End Date',help='When Citizen Service Point is closed'),
        'schedule': fields.char('Schedule',size=60,help='For example L-V 8:30 am -12:50 pm'),
        'geo_point':fields.geo_point('Location',srid=4668,readonly=True),
        'users_id':fields.many2many('res.users','ocs_citizen_service_point_users','csp_id','user_id','Users'),
    }
ocs_citizen_service_point()

class res_users(osv.osv):
    """
    Add many 2 many relationship with Citizen Service Point.
    """
    _name="res.users"
    _inherit="res.users"
    _columns = {
        'csp_id':fields.many2many('ocs.citizen_service_point','ocs_citizen_service_point_users','user_id','csp_id','Citizen Service Point')
    }

class ocs_claim_classification(osv.osv):
    """This field contains internal classification for claims """
    _name="ocs.claim_classification"
    _columns={
      'id':fields.integer('ID',readonly=True),
      'is_portal_visible':fields.boolean('Is Portal Visible',help="If this field is set, when claim portal can retrieve this classification."),
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

class crm_case_categ(osv.osv):
    "This class enable/Disable Categories according current politics"
    _name="crm.case.categ"
    _inherit="crm.case.categ"
    _columns={
        'active':fields.boolean('Active',help='Enable/Disable Case Category'),
    }


class crm_claim(geo_model.GeoModel):
    _name = "crm.claim"
    _inherit = "crm.claim"

    def test_response(self, cr, uid, ids, *args):
        """
        Check if Response Text is Empty
        """
        isResponsed = False
        for claim in self.browse(cr,uid,ids,context=None):
            response = claim.resolution
            if response == False:
                isResponsed = False
                message = "Resolution text could not be Empty"
            else:
                isResponsed = True
                message = "The claim: {0} -- has been closed".format(claim.name)
        self.log(cr, uid, claim.id, message)
        return isResponsed

    def _check_user_in_csp(self, cr, uid, ids, context = None):
        """
        Constraint:
        If user is in Citizen Service Point allow create or update claim if not refuse
        """
        is_valid_data = False

        for claim in self.browse(cr,uid,ids,context=None):
            for user_id in claim.csp_id.users_id:
                if user_id==claim.user_id:
                    is_valid_data = True
        return is_valid_data


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

    def onchange_partner_address_id(self, cr, uid, ids, add, email=False):
        """This function returns value of partner email based on Partner Address
          :param part: Partner's id
          :param email: ignored
        """
        if not add:
            return {'value': {'email_from': False}}
        address = self.pool.get('res.partner.address').browse(cr, uid, add)
        return {'value': {'email_from': address.email, 'partner_phone': address.phone,'claim_address':address.street}}

    _columns={
        #'user_id': fields.many2one('res.users', 'Salesman', readonly=True, states={'draft':[('readonly',False)]}),
        'description': fields.text('Description',required=True,readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'priority': fields.selection([('h','High'),('n','Normal'),('l','Low')], 'Priority', required=True, readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'external_id':fields.char('External ID',size=128,help='External Claim System Identificator',readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'external_dms_id': fields.char('External DMS ID',size=20,help='External Document Management System Identificator',readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'csp_id':fields.many2one('ocs.citizen_service_point','CSP',help='Citizen Service Point',required=True,readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'channel':fields.many2one('crm.case.channel','Case Channel',help='Case Channel',required=True,readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'categ_id': fields.many2one('crm.case.categ', 'Requirement Type', \
                            domain="[('section_id','=',section_id),\
                            ('object_id.model', '=', 'crm.claim')],\
                            ('active','=',True)",
                            required=True,readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),

        'claim_address':fields.char('Claim Address',size=256,help='Place of Claim',readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'district_id':fields.many2one('ocs.district','District',readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'neighborhood_id':fields.many2one('ocs.neighborhood','Neighborhood',readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'geo_point':fields.geo_point('Location',srid=4668,readonly=True),
        'classification_id':fields.many2one('ocs.claim_classification','Classification', \
                                              domain="[('parent_id','=',False),('enabled','=',True)]", required=True,readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'sub_classification_id':fields.many2one('ocs.claim_classification','Sub Classification',domain="[('parent_id','=',classification_id),('enabled','=',True)]", required=True,readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'name':fields.function(_get_full_name,type='char',string='Full Name',method=True),
        #Se repiten campos del modelo original para poder controlarlos en los estados
        'partner_id': fields.many2one('res.partner', 'Partner',readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'partner_address_id': fields.many2one('res.partner.address', 'Contact', \
                                # domain="[('partner_id','=',partner_id)]"
                                  readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'email_from': fields.char('Email', size=128, help="These people will receive email.",readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'partner_phone': fields.char('Phone', size=32,readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'resolution': fields.text('Resolution',readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'date_deadline': fields.date('Deadline',readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'user_id': fields.many2one('res.users', 'Responsible',readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]},domain="[('csp_id','=',csp_id)]"),
    }

    _order='create_date desc'
    _rec_name = 'classification'
    _defaults = {
        'date_deadline': lambda *a:  date_by_adding_business_days(datetime.now(), 15).__format__('%Y-%m-%d %H:%M:%S'),#Default +15 working days
        'priority': lambda *a: 'l'
        }
    _constraints = [
    (_check_user_in_csp,'User must registered in the Point of Citizen Service',['user_id']),
    ]
crm_claim()


def date_by_adding_business_days(from_date, add_days):
    business_days_to_add = add_days
    current_date = from_date
    while business_days_to_add > 0:
        current_date += timedelta(days=1)
        weekday = current_date.weekday()
        if weekday >= 5: # sunday = 6
            continue
        business_days_to_add -= 1
    return current_date
