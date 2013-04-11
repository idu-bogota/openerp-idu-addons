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
import re, json
from openerp.osv.osv import except_osv
from tools.translate import _


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
        for r in self.read(cr, user, ids, ['name','last_name','email','twitter','document_number','zip','country_id', 'city','partner_id', 'street']):
            if context.get('contact_display', 'contact')=='partner' and r['partner_id']:
                res.append((r['id'], r['partner_id'][1]))
            else:
                # make a comma-separated list with the following non-empty elements
                #elems = [r['name'],r['last_name'],r['document_number'],r['country_id'] and r['country_id'][1], r['city'], r['street']]
                elems = [r['name'],r['last_name'],r['document_number'],r['email'],r['twitter']]
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
            ids = self.search(cr, user, ['|',('name', 'ilike', name),'|',('document_number', 'ilike', name),'|',('email', 'ilike', name),('twitter', 'ilike', name)] + args,
                    limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('name', operator, name)] + args,
                    limit=limit, context=context)
        return self.name_get(cr, user, ids, context)

    def _get_full_name(self,cr,uid,ids,fieldname,arg,context=None):
        """Get Full Name of Citizen """
        res = {}
        for citizen in self.browse(cr, uid, ids, context = context):
            if citizen.last_name == False and citizen.name == False:
                res[citizen.id] = "-"
            elif citizen.last_name == False:
                res[citizen.id] = "{0}".format(citizen.name)
            else:
                res[citizen.id] = "{0},{1}".format(citizen.last_name, citizen.name)
        return  res

    def _check_contact_data(self, cr, uid, ids, context = None):
        """
        Constraint:
        Should have filled at least one contact detail
        """
        is_valid_data = False
        for citizen in self.browse(cr,uid,ids,context=None):
            if ((citizen.email != False) or
                (citizen.twitter != False) or
                (citizen.phone != False) or
                (citizen.facebook != False) or
                (citizen.street != False) or
                (citizen.mobile != False)):
                is_valid_data = True
        return is_valid_data

    def _check_document_type_and_number(self, cr, uid, ids, context = None):
        """
        Constraint:

        Document type defined must have document number
        """
        is_valid_document = True
        for citizen in self.browse(cr, uid, ids,context=None):
            if ((citizen.document_type and not citizen.document_number) or
                (citizen.document_number and not citizen.document_type)):
                is_valid_document = False

        return is_valid_document

    def _check_twitter(self, cr, uid, ids, context = None):
        """
        Constraint:
        regex /[a-zA-Z0-9_]{1,15}/
        """
        is_valid_data = False
        for citizen in self.browse(cr,uid,ids,context=None):
            if (citizen.twitter == False) or (re.match("^[a-zA-Z0-9_]{1,15}$", citizen.twitter) != None):
                is_valid_data = True
        return is_valid_data

    def _check_facebook(self, cr, uid, ids, context = None):
        """
        Constraint:
        regex /[a-zA-Z0-9\.]{5,50}/
        """
        is_valid_data = False
        for citizen in self.browse(cr,uid,ids,context=None):
            if (citizen.facebook == False) or (re.match("^[a-zA-Z0-9\.]{5,50}$", citizen.facebook) != None):
                is_valid_data = True
        return is_valid_data

    def _check_email(self, cr, uid, ids, context = None):
        """
        Constraint:
        simple checking with regex /^[^@]+@[^@]+\.[^@]+$/
        """
        is_valid_data = False
        for citizen in self.browse(cr,uid,ids,context=None):
            if (citizen.email == False) or (re.match("^[^@]+@[^@]+\.[^@]+$", citizen.email) != None):
                is_valid_data = True
        return is_valid_data

    def onchange_district_id(self, cr, uid, ids, district_id, geo_point):
        """Restricts the neighborhood list to the selected district_id
        """
        v={}
        d={}
        if district_id:
            district = self.pool.get('ocs.district').browse(cr, uid, district_id)
            n_ids = district.neighborhood_ids()
            d['neighborhood_id'] = "[('id','in',{0})]".format(n_ids)
            if not geo_point:
                v['neighborhood_id'] = ''
        return {'domain':d, 'value':v}

    def onchange_street(self, cr, uid, ids, street):
        """
        GeoCode claim address Override this using your own geocoder
        param addr: Claim Address
        """
        return {'value':{'geo_point':False}}

    def onchange_geopoint(self, cr, uid, ids, point):
        return onchange_geopoint(cr, uid, ids, point)

    def create(self, cr, uid, vals, context=None):
        vals = self.trim_vals(vals)
        return super(ResPartnerAddress, self).create(cr, uid, vals, context)

    def write(self, cr, uid, ids, vals, context=None):
        vals = self.trim_vals(vals)
        return super(ResPartnerAddress, self).write(cr, uid, ids, vals, context=context)

    def trim_vals(self, vals):
        for key, value in vals.items():
            if type(value) == str:
                vals[key] = value.strip()
        return vals

    _name = 'res.partner.address'
    _inherit='res.partner.address'
    _columns = {
        'last_name':fields.char('Last Name:',size=128,required=True),
        'name':fields.char('First Name',size=128,required=True),
        'gender':fields.selection([('m','Male'),('f','Female')],'Gender'),
        'document_number': fields.char('Document Number', size=64,selectable=True),
        'document_type': fields.selection([('NI','National ID'),('passport','Passport')],'Document Type',help='Document Type'),
        'twitter': fields.char('Twitter', size=64),
        'facebook':fields.char('Facebook:',size=240),
        'district_id':fields.many2one('ocs.district','District'),
        'neighborhood_id':fields.many2one('ocs.neighborhood','Neighborhood'),
        'full_name':fields.function(_get_full_name,type='char',string='Full Name',method=True),
        'geo_point':fields.geo_point('Location',readonly=False),
        'claim_id':fields.one2many('crm.claim','id','Historic of Claims',help="Claims opened by User")
    }
    _rec_name = 'document_number'
    _order= "last_name asc"
    _sql_constraints = [
        ('unique_cc_document_number','unique(document_type,document_number)','Combination document type, document id must be unique!!!'),
        ('unique_email','unique(email)','This email is already registered'),
        ('unique_twitter','unique(twitter)','This twitter account is already registered'),
        ('unique_facebook','unique(facebook)','This facebook account is already registered'),
    ]
    _constraints = [
        (_check_contact_data,'You must type at least one of these: email, phone, cell phone, facebook or twitter to create a contact',['street']),
        (_check_twitter,'twitter account is max 15 long and contains just letters, numbers and "_"',['twitter']),
        (_check_facebook,'facebook account is min 5 max 50 long and contains just letters, numbers and "."',['facebook']),
        (_check_email,'email is not valid',['email']),
        (_check_document_type_and_number,'Document Type and Document Number are required',['document_type','document_number']),
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
        'geo_point':fields.geo_point('Location',readonly=True),
        'users_id':fields.many2many('res.users','ocs_citizen_service_point_users','csp_id','user_id','Users'),
    }
ocs_citizen_service_point()

class res_users(osv.osv):
    """
    Add many 2 many relationship with Citizen Service Point.
    """
    _name="res.users"
    _inherit="res.users"

    def _get_csp_ids(self, cr, uid, ids, fieldname, arg, context=None):
        """
        Return list of csp_ids this user belongs to, used to force_domain, as the csp_id is not iterable
        """
        res = {}
        for user in self.browse(cr, uid, ids, context = context):
            res[user.id] = [csp.id for csp in user.csp_id] 
        return  res

    _columns = {
        'csp_id':fields.many2many('ocs.citizen_service_point','ocs_citizen_service_point_users','user_id','csp_id','Citizen Service Point'),
        'get_csp_ids': fields.function(_get_csp_ids, type='list', string='List of CSP IDs', method=True),
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

class ocs_claim_solution_classification(osv.osv):
    """This field contains internal classification for claim's solution """
    _name="ocs.claim_solution_classification"
    _columns={
      'id':fields.integer('ID',readonly=True),
      'code':fields.char('Code',size=6),
      'name':fields.char('Name',size=128),
      'enabled':fields.boolean('Enabled',help='If item is valid now'),
      'parent_id':fields.many2one('ocs.claim_solution_classification','Parent')
    }
    constraints = [
        (osv.osv._check_recursion,'Error ! You cannot create recursive Claim Solution Classification',['parent_id'])
    ]
ocs_claim_solution_classification()

class ocs_neighborhood(geo_model.GeoModel):
    """Contains geographic information about all towns in the city"""
    _name = 'ocs.neighborhood'
    _order = 'name asc'
    _columns = {
        'code': fields.char('Neighborhood Code',size=30,help='Identify a Cadastral Code'),
        'name': fields.char('Neighborhood Name', size = 128),
        'geo_polygon':fields.geo_multi_polygon('Geometry'),
    }
ocs_neighborhood()

class ocs_district(geo_model.GeoModel):
    """ Contaihow to delete a field from parent class openerpns geografic information about localities"""
    _name = 'ocs.district'
    _order = 'name asc'
    _columns = {
        'code': fields.char('District Code',size=30),
        'name': fields.char('District Name',size=20),
        'geo_polygon':fields.geo_multi_polygon('Geometry'),
    }

    def neighborhood_ids(self, cr, uid, id, default=None, context=None):
        """Return a list with neighborhoods from the district uses a postgis query
        """
        #neighborhoods = self.pool.get('ocs.neighborhood').geo_search(cr, uid, geo_domain=[('geo_polygon', 'geo_intersect', {'ocs.district.geo_polygon': []})])
        query = 'SELECT DISTINCT(n.id) FROM ocs_neighborhood AS n, ocs_district AS d ' \
            "WHERE intersects(n.geo_polygon, d.geo_polygon) = TRUE AND d.id = {0};".format(id[0])
        cr.execute(query)
        n_ids = []
        for n_id in cr.fetchall():
            n_ids.append(n_id[0])
        return n_ids

ocs_district()

class ocs_sub_district(geo_model.GeoModel):
    """ Contains geografic information about especific territories """
    _name = 'ocs.sub_district'
    _order = 'name asc'
    _columns= {
        'name' : fields.char('Sub District Name :',size=150, help='Sub-District name'),
        'code' : fields.char('Territory Code :',size=150,help='Territory Code'),
        'geo_polygon':fields.geo_multi_polygon('Geometry'),
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
            response_classification = claim.solution_classification_id
            message = ''
            if response == False:
                isResponsed = False
                message = "Resolution text can not be empty."

            if response_classification.id == False:
                isResponsed = False
                message += " Solution Classification cannot be empty."

            if not message:
                isResponsed = True
                message = "The claim: {0} -- has been closed".format(claim.name)
        if not isResponsed:
            raise osv.except_osv(_('Error'),_(message))

        return isResponsed

    def set_default_csp_id(self, cr, uid, context = None):
        """
        If user has one citizen service point assigned then select it by default
        """
        csp_id = self.pool.get('ocs.citizen_service_point').search(cr, uid, [], offset=0, limit=2);
        if len(csp_id) == 1:
            return csp_id[0]

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

    def onchange_partner_address_id(self, cr, uid, ids, add, email=False):
        """This function returns value of partner email based on Partner Address
          :param part: Partner's id
          :param email: ignored
        """
        if not add:
            return {'value': {'email_from': False}}

        address = self.pool.get('res.partner.address').browse(cr, uid, add)
        return {'value': {'email_from': address.email, 'partner_phone': address.phone,
                          'partner_id': address.partner_id.id,
                          }
                }

    def onchange_district_id(self, cr, uid, ids, district_id, geo_point):
        """Restricts the neighborhood list to the selected district_id
        """
        v={}
        d={}
        if district_id:
            district = self.pool.get('ocs.district').browse(cr, uid, district_id)
            n_ids = district.neighborhood_ids()
            d['neighborhood_id'] = "[('id','in',{0})]".format(n_ids)
            if not geo_point: 
                v['neighborhood_id'] = ''
        return {'domain':d, 'value':v}

    def onchange_address_value(self, cr, uid, ids, addr):
        """
        GeoCode claim address Override this using your own geocoder
        param addr: Claim Address
        """
        return {'value':{'geo_point':False}}

    def onchange_geopoint(self, cr, uid, ids, point):
        return onchange_geopoint(cr, uid, ids, point)

    def message_new(self, cr, uid, msg, custom_values=None, context=None):
        """Automatically called when new email message arrives"""
        subject = msg.get('subject')
        body = msg.get('body_text')
        msg_from = msg.get('from')

        vals = {
            'email_from': msg_from,
            'email_cc': msg.get('cc'),
        }
        if custom_values == None:
            custom_values = {}
        custom_values['description'] = "{0}\n\n{1}".format(subject, body)
        custom_values.update(self.message_default_values(cr, uid, msg))
        #res_id = super(crm_claim,self).message_new(cr, uid, msg, custom_values=custom_values, context=context)
        res_id = self.create(cr, uid, custom_values, context=context)
        self.message_append_dict(cr, uid, [res_id], msg, context=context)
        vals.update(self.message_partner_by_email(cr, uid, msg.get('from', False)))
        self.write(cr, uid, [res_id], vals, context=context)
        return res_id

    def message_default_values(self, cr, uid, msg, **args):
        custom_values = {}
        partner_address_id = self.pool.get('res.partner.address').search(cr, uid, [('email','=',msg.get('from'))], offset=0, limit=1)
        if len(partner_address_id):
            custom_values['partner_address_id'] = partner_address_id[0]

        channel = self.pool.get('crm.case.channel').search(cr, uid, [('active','=',True),('name','=',msg.get('to'))], offset=0, limit=1)
        if len(channel):
            custom_values['channel'] = channel[0]
        else:
            custom_values['channel'] = self.pool.get('crm.case.channel').search(cr, uid, [('active','=',True)], offset=0, limit=1)[0]

        custom_values['categ_id'] = self.pool.get('crm.case.categ').search(cr, uid, [('active','=',True)], offset=0, limit=1)[0]
        custom_values['csp_id'] = self.pool.get('ocs.citizen_service_point').search(cr, uid, [], offset=0, limit=1)[0]
        csp = self.pool.get('ocs.citizen_service_point').read(cr, uid, custom_values['csp_id'])
        custom_values['user_id'] = csp['users_id'][0]
        custom_values['classification_id'] = self.pool.get('ocs.claim_classification').search(cr, uid, [], offset=0, limit=1)[0]
        custom_values['sub_classification_id'] = self.pool.get('ocs.claim_classification').search(cr, uid, [('parent_id','=',custom_values['classification_id'])], offset=0, limit=1)[0]
        return custom_values

    def _check_address_related_fields(self, cr, uid, ids, context = None):
        """
        If address district and neighborhood must be selected
        """
        is_valid = True
        for claim in self.browse(cr,uid,ids,context=None):
            if ((claim.claim_address != False) and (claim.neighborhood_id.id == False or claim.district_id.id == False)):
                is_valid = False
        return is_valid

    _columns={
        #'user_id': fields.many2one('res.users', 'Salesman', readonly=True, states={'draft':[('readonly',False)]}),
        'description': fields.text('Description',required=True,readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'priority': fields.selection([('h','High'),('n','Normal'),('l','Low')], 'Priority', required=True, readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
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
        'geo_point':fields.geo_point('Location',readonly=True),
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
        'solution_classification_id':fields.many2one('ocs.claim_solution_classification','Solution Classification', \
            domain="[('parent_id','!=',False),('enabled','=',True)]",required=False,readonly=True,
            states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'partner_forwarded_id': fields.many2one('res.partner', 'Partner Forwarded',domain="[('supplier','=',True)]",readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
    }

    _order='create_date desc'
    _rec_name = 'classification'
    _defaults = {
        'date_deadline': lambda *a:  date_by_adding_business_days(datetime.now(), 15).__format__('%Y-%m-%d %H:%M:%S'),#Default +15 working days
        'priority': lambda *a: 'l',
        'csp_id': set_default_csp_id,
        'section_id': lambda *a: 1, #All belong to the default sales team
        }
    _constraints = [
    (_check_user_in_csp,'User must registered in the Point of Citizen Service',['user_id']),
    (_check_address_related_fields,'Please select district and neigboohood',['claim_address']),
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

def onchange_geopoint(cr, uid, ids, point):
    """
    Based on geo referenced address update district_id and neighborhood
    geo_point is set by a geocoder 
    param geo_point: address coordinate in GeoJSON format
    """
    try:
        if (point is not False):
            """
            Calculating District and Neighborhood from claim_address
            """
            coord = json.loads(point)["coordinates"]
            x = coord[0]
            y = coord[1]
            query = "SELECT id FROM ocs_district \
                WHERE INTERSECTS(geo_polygon, ST_GEOMETRYFROMTEXT('POINT({0} {1})',900913)) IS TRUE".format(x,y)
            cr.execute(query)
            district_id = False
            for n_ids in cr.fetchall():
                for i in n_ids :
                    district_id = i
            #res = {'value':{'geo_point':point}}
            query_neigh = "SELECT id FROM ocs_neighborhood \
                WHERE INTERSECTS(geo_polygon, ST_GEOMETRYFROMTEXT('POINT({0} {1})',900913)) IS TRUE".format(x,y)
            cr.execute(query_neigh)
            neighborhood_id = False
            for n_ids in cr.fetchall():
                for i in n_ids :
                    neighborhood_id = i
            return {'value':{'district_id':district_id,'neighborhood_id':neighborhood_id}}
        else :
            return {}
    except Exception, exc:
        raise except_osv(_('Geoencoding fails'), str(exc))
