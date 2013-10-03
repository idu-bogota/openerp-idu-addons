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
from crm import crm
from tools.translate import _
import re
from geocoder.geocode import geo_code_address,is_bogota_address_valid,extract_basic_address
##"other.extra:900913"

class crm_claim(crm.crm_case,osv.osv):
    """
    Inherit from ocs and ocs crm_claim
    """

    def test_response(self, cr, uid, ids, *args):
        """
        Check if Response Text is Empty and partner_forwarded_id is selected when claim is redirected
        """
        is_valid_super = super(crm_claim, self).test_response(cr, uid, ids, args)

        for claim in self.browse(cr, uid, ids,context = None):
            classification = self.pool.get('ocs.claim_classification').name_search(cr, uid, name='Trámites a cargo de otras entidades remitidos a IDU', args=None, operator='=', context=None)
            if claim.classification_id.id == classification[0][0] and claim.partner_forwarded_id.id == False:
                raise osv.except_osv(_('Error'),_('Need Partner Forwarded'))

        return is_valid_super


    def _check_is_outsourced(self,cr,uid,ids,fieldname,arg,context=None):
        """
        Check if the citizen service point is outsourced, with this
        validates when is csp outsourced
        """
        res = {}
        for claim in self.browse(cr, uid, ids, context = context):
            res[claim.id] = claim.csp_id.is_outsourced
        return  res

    def _check_is_editable(self,cr,uid,ids,fieldname,arg,context=None):
        """
        Check if current user can edit the PQR based on status and group.
        Used this options instead of attributes with some logic in the view
        useful just in web mode no in XMLRPC.
        cannot use object level permissions as all roles need to add messages and for that requires update permission on crm.claim
        """
        res = {}
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        ocs_role = None

        regex = "^ocs_idu\.group_ocs_outsourced_(.*)$"
        for grp in user.groups_id:
            grp_id = grp.get_external_id()[grp.id] # Returns the external id like ocs.group_ocs_outsourced_user
            result = re.search(regex, grp_id)
            if result:
                ocs_role = result.group(1)
                if ocs_role == 'manager':
                    break

        for claim in self.browse(cr, uid, ids, context = context):
            status = claim.state
            is_editable = True
            if status in ['done', 'cancel', 'pending']:
                is_editable = False
            elif ocs_role in ['reader','reviewer']:
                is_editable = False
            elif ocs_role == 'user' and status in ['review']:
                is_editable = False
            res[claim.id] = is_editable
        return  res

    def _get_csp_contract(self, cr, uid, ids, fieldname, arg, context=None):
        """
        Returns current contract linked to the CSP
        """
        res = {}
        for claim in self.browse(cr, uid, ids, context = context):
            res[claim.id] = claim.csp_id.contract_id.contract_id
        return  res

    def case_review(self, cr, uid, ids, *args):
        """Review the Case
        :param ids: List of case Ids
        """
        cases = self.browse(cr, uid, ids)
        self.message_append(cr, uid, cases, _('Review'))
        for case in cases:
            data = {'state': 'review', 'active': True }
            if not case.user_id:
                data['user_id'] = uid
            self.write(cr, uid, case.id, data)
        self._action(cr, uid, cases, 'review')
        return True

    def case_reject(self, cr, uid, ids, *args):
        """Case Rejected
        :param ids: List of case Ids
        """
        cases = self.browse(cr, uid, ids)
        self.message_append(cr, uid, cases, _('Rejected'))
        for case in cases:
            data = {'state': 'rejected', 'active': True }
            if not case.user_id:
                data['user_id'] = uid
            self.write(cr, uid, case.id, data)
        self._action(cr, uid, cases, 'rejected')
        return True

    def _check_contract_reference(self, cr, uid, ids, context = None):
        """
        Constraint:
        follow format ddd-yyyy
        """
        is_valid = False
        for claim in self.browse(cr, uid, ids,context):
            if claim.contract_reference != False:
                if re.match("^[0-9]{1,4}-([0-9]{4})$", claim.contract_reference) != None:
                    is_valid = True
            else:
                is_valid = True
        return is_valid

    def _check_claim_address(self, cr, uid, ids, context = None):
        """
        Constraint:
        Check an address like this is valid
        Cr 102 BIS 10 A BIS Z 30 Int 3 Loc 4
        """
        is_valid = False
        for claim in self.browse(cr, uid, ids,context):
            if claim.claim_address != False:
                if is_bogota_address_valid(claim.claim_address):
                    is_valid = True
            else:
                is_valid = True
        return is_valid

    def onchange_classification_id(self, cr, uid, ids, classification_id):
        """Changes based on classification_id
        """
        solution = self.pool.get('ocs.claim_solution_classification').name_search(cr, uid, name='Redireccionado Internamente', args=None, operator='=', context=None)
        v={ 'sub_classification_id': '', 'solution_classification_id': solution[0][0] }
        if classification_id:
            sub_classification = self.pool.get('ocs.claim_classification').name_search(cr, uid, name='Queja contra servidores públicos IDU', args=None, operator='=', context=None, limit=1)
            if (len(sub_classification) and classification_id == sub_classification[0][0]):
                category = self.pool.get('crm.case.categ').name_search(cr, uid, name='Queja', args=None, operator='=', context=None)
                v['categ_id'] = category[0][0]
            else:
                classification = self.pool.get('ocs.claim_classification').name_search(cr, uid, name='Denuncias sobre actuación IDU', args=None, operator='=', context=None, limit=1)
                if (len(classification) and classification_id == classification[0][0]):
                    category = self.pool.get('crm.case.categ').name_search(cr, uid, name='Denuncia', args=None, operator='=', context=None)
                    v['categ_id'] = category[0][0]
                else:
                    classification = self.pool.get('ocs.claim_classification').name_search(cr, uid, name='Trámites a cargo de otras entidades remitidos a IDU', args=None, operator='=', context=None, limit=1)
                    if (len(classification) and classification_id == classification[0][0]):
                        solution = self.pool.get('ocs.claim_solution_classification').name_search(cr, uid, name='Redireccionado Externamente', args=None, operator='=', context=None)
                        v['solution_classification_id'] = solution[0][0]

        return {'value':v}

    def onchange_partner_address_id(self, cr, uid, ids, add, email=False):
        """This function returns value of partner email based on Partner Address
          :param part: Partner's id
        """
        result = super(crm_claim, self).onchange_partner_address_id(cr, uid, ids, add, email)
        if add:
            address = self.pool.get('res.partner.address').browse(cr, uid, add)
            if(address.twitter):
                channel = self.pool.get('crm.case.channel').name_search(cr, uid, name='Twitter', args=None, operator='=', context=None)
                result['value']['channel'] = channel[0][0]
            if(address.facebook):
                channel = self.pool.get('crm.case.channel').name_search(cr, uid, name='Facebook', args=None, operator='=', context=None)
                result['value']['channel'] = channel[0][0]

        return result

    def onchange_district_id(self, cr, uid, ids, district_id, geo_point):
        """Restricts the neighborhood list to the selected district_id
        """
        result = super(crm_claim, self).onchange_district_id(cr, uid, ids, district_id, geo_point)
        d = result['domain']
        v = result['value']
        if district_id:
            district = self.pool.get('ocs.district').browse(cr, uid, district_id)
            if(district.name == 'FUERA DE BOGOTÁ'):
                classification = self.pool.get('ocs.claim_classification').name_search(cr, uid, name='Trámites a cargo de otras entidades remitidos a IDU', args=None, operator='=', context=None, limit=1)
                v['classification_id'] = classification[0][0]
        return {'domain':d, 'value':v}

    def onchange_address_value(self, cr, uid, ids, addr):
        """
        GeoCode claim address
        param addr: Claim Address
        """
        return geocode_address(self, cr, uid, ids, addr)

    def _check_address_related_fields(self, cr, uid, ids, context = None):
        """
        If address district and neighborhood must be selected except when address is "fuera de bogota"
        """
        is_valid = True
        for claim in self.browse(cr,uid,ids,context=None):
            if ((claim.claim_address != False) and (claim.neighborhood_id.id == False or claim.district_id.id == False) and (claim.district_id.name != 'FUERA DE BOGOTÁ')):
                is_valid = False
        return is_valid

    _name="crm.claim"
    _inherit="crm.claim"
    _columns = {
        'district_id':fields.many2one('ocs.district','District',required=True, readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
        'resolution': fields.text('Resolution',readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)],'rejected':[('readonly',False)]},
            write = ['ocs_idu.group_ocs_outsourced_user','ocs_idu.group_ocs_outsourced_manager','ocs.group_ocs_user','ocs.group_ocs_manager'],
            read = ['ocs_idu.group_ocs_outsourced_user','ocs_idu.group_ocs_outsourced_manager','ocs_idu.group_ocs_outsourced_reviewer','ocs.group_ocs_user','ocs.group_ocs_manager'],
            ),
        'solution_classification_id':fields.many2one('ocs.claim_solution_classification','Solution Classification',
            domain="[('parent_id','!=',False),('enabled','=',True)]",required=False,readonly=True,
            states={'draft':[('readonly',False)],'open':[('readonly',False)],'rejected':[('readonly',False)]},
            write = ['ocs_idu.group_ocs_outsourced_user','ocs_idu.group_ocs_outsourced_manager','ocs.group_ocs_user','ocs.group_ocs_manager'],
            read = ['ocs_idu.group_ocs_outsourced_user','ocs_idu.group_ocs_outsourced_manager','ocs_idu.group_ocs_outsourced_reviewer','ocs.group_ocs_user','ocs.group_ocs_manager'],
            ),
        'partner_forwarded_id': fields.many2one('res.partner', 'Partner Forwarded',domain="[('supplier','=',True)]",readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)],'rejected':[('readonly',False)]},
            write = ['ocs_idu.group_ocs_outsourced_user','ocs_idu.group_ocs_outsourced_manager','ocs.group_ocs_user','ocs.group_ocs_manager'],
            read = ['ocs_idu.group_ocs_outsourced_user','ocs_idu.group_ocs_outsourced_manager','ocs_idu.group_ocs_outsourced_reviewer','ocs.group_ocs_user','ocs.group_ocs_manager'],
        ),
        'priority': fields.selection([('h','High'),('n','Normal'),('l','Low')], 'Priority', required=True, readonly=True),
        'date_deadline': fields.date('Deadline',readonly=True),
        'state':fields.selection([('draft', 'New'),('open', 'In Progress'),('cancel', 'Cancelled'),
                                  ('review','Review'),('rejected','Rejected'),('done', 'Closed'),('pending', 'Pending')],
                                 'State',help='Introduce a new state between open and done, in this step,\
                                  other people makes a review and approve the response given to citizen'),
        'is_outsourced':fields.function(_check_is_outsourced,type='boolean',string='Is Outsourced',method=True, store=True),
        'is_editable':fields.function(_check_is_editable,type='boolean',string='Check if current user can edit the data',method=True),
        'csp_contract':fields.function(_get_csp_contract,type='string',string='Contract',method=True),
        'contract_reference': fields.char('Contract Reference',size=9,help='Construction contract number number-year',states={'done':[('readonly',True)]}),
        'damage_type_by_citizen': fields.selection([('via-fisura', 'Via fisura'),('via-hueco', 'Via Hueco'),('via-hundimiento-canalizacion', 'Via hundimiento o canalización'),
                                                    ('anden-hueco', 'Anden hueco'),('anden-desnivel', 'Anden desnivel'),('anden-accesibilidad', 'Anden accesibilidad'),
                                                    ('cicloruta-hueco', 'Cicloruta hueco'),('cicloruta-obstruccion', 'cicloruta obstrucción'),('cicloruta-segnal', 'Cicloruta señalización'),
                                                    ('puente-peatonal-grieta', 'Puente peatonal grieta'),('puente-peatonal-laminas', 'Puente peatonal láminas'),('puente-peatonal-accesibilidad', 'Puente peatonal accesibilidad'),
                                                   ],
                                                   'Via Damage Type', help='Damage type provided by the citizen'),
        'damage_width_by_citizen':  fields.char('Via damage width',size=10,help='Damage width provided by the citizen',states={'done':[('readonly',True)]}),
        'damage_length_by_citizen': fields.char('Via damage length',size=10,help='Damage length provided by the citizen',states={'done':[('readonly',True)]}),
        'damage_deep_by_citizen': fields.char('Via damage deep',size=10,help='Damage size provided by the citizen',states={'done':[('readonly',True)]}),
        'damage_element_by_citizen': fields.selection([('via', 'Via'),('anden', 'Anden'),('puente_peatonal', 'Puente Peatonal'),('cicloruta', 'Cicloruta')], 'Via Element Type',help='Element type provided by the citizen'),
    }
    _constraints = [
        (_check_contract_reference,'Contract Reference format is number-year, ie. 123-2012',['contract_reference']),
        (_check_claim_address,'Claim Address should follow IDU conventions ie. Cr 102 BIS 10 A BIS Z 30 Int 3 Loc 4',['claim_address']),
        (_check_address_related_fields,'Please select district and neigboohood',['claim_address']),
    ]
    _defaults = {
        'is_editable': True
    }

crm_claim()

class ResPartnerAddress(geo_model.GeoModel):
    def _check_address(self, cr, uid, ids, context = None):
        """
        Constraint:
        Check an address like this is valid
        Cr 102 BIS 10 A BIS Z 30 Int 3 Loc 4
        """
        is_valid = False
        for contact in self.browse(cr, uid, ids, context):
            if contact.street != False:
                if is_bogota_address_valid(contact.street):
                    is_valid = True
            else:
                is_valid = True
        return is_valid

    def _check_document(self, cr, uid, ids, context = None):
        """
        Constraint:

        Document Number Regex Validation
        """
        is_valid_document = False
        for citizen in self.browse(cr, uid, ids,context=None):
            if citizen.document_type == 'CC' :
                if citizen.document_number != False:
                    if re.match("^[0-9]{6,15}$", citizen.document_number) != None:
                        is_valid_document = True
                    else:
                        is_valid_document = False #Empty document are permited....
            else:
                is_valid_document = True
        return is_valid_document

    def _check_gender(self, cr, uid, ids, context = None):
        """
        Constraint:
        Should have filled gender if name is filled in
        """
        is_valid_data = False
        for citizen in self.browse(cr,uid,ids,context=None):
            if ((citizen.name != False) and (citizen.gender != False) or
                (citizen.name == False) and (citizen.gender == False) or
                citizen.gender != False
            ):
                is_valid_data = True
        return is_valid_data

    def _check_address_related_fields(self, cr, uid, ids, context = None):
        """
        If address district and neighborhood must be selected
        """
        is_valid = True
        for citizen in self.browse(cr,uid,ids,context=None):
            if ((citizen.street != False) and (citizen.neighborhood_id.id == False or citizen.district_id.id == False) and (citizen.district_id.name != 'FUERA DE BOGOTÁ')):
                is_valid = False
        return is_valid

    def onchange_street(self, cr, uid, ids, addr):
        """
        GeoCode claim address
        param addr: Claim Address
        """
        return geocode_address(self, cr, uid, ids, addr)

    def _check_facebook(self, cr, uid, ids, context = None):
        """
        OTC no desea esta validacion
        """
        return True

    _name = 'res.partner.address'
    _inherit='res.partner.address'
    _columns = {
        'last_name':fields.char('Last Name:',size=128,required=False),
        'name':fields.char('First Name',size=128,required=False),
        'document_type': fields.selection([('CC','Cédula de ciudadanía'),('TI','Tarjeta de Identidad'),('Pasaporte','Pasaporte'),('CE','Cedula Extranjería')],'Document Type',help='Tipo de documento de identificación'),
    }
    _constraints = [
        (_check_address,'Claim Address should follow IDU conventions ie. KR 102 BIS 10 A BIS Z 30 INT 3 LOC 4',['street']),
        (_check_document,'When Document Type is CC, the document number must be numeric only!!!',['document_number']),
        (_check_gender,'Please select gender',['gender']),
        (_check_address_related_fields,'Please select district and neigboohood',['street']),
        (_check_facebook,'facebook account is min 5 max 50 long and contains just letters, numbers and "."',['facebook']),
    ]
    _rec_name = 'document_number'

ResPartnerAddress()

class ocs_citizen_service_point(geo_model.GeoModel):
    """
    IDU High Specific Requeriment for Office of Citizen Service  with Outsourced partner
    """

    def _check_is_outsourced (self,cr,uid,context):
        """
        Verifiy Context to Set default value
        """
        if context.has_key("is_outsourced"):
            if context["is_outsourced"]:
                return True
            else :
                return False
        return False

    def _get_full_name(self,cr,uid,ids,fieldname,arg,context=None):
        """Get Full Name of Contract """
        res = {}
        for csp in self.browse(cr, uid, ids, context = context):
                res[csp.id] = "{0}".format(csp.name)
        return  res

    _name="ocs.citizen_service_point"
    _inherit="ocs.citizen_service_point"
    _columns = {
        'is_outsourced':fields.boolean('is Outsourced',help='When is set, this is an outsourced citizen service point'),
        'contract_id':fields.many2one('ocs.contract','Contract Id', required=True),
        'full_name':fields.function(_get_full_name,type='char',string='Full Name',method=True),
    }
    _defaults={
        'is_outsourced':  _check_is_outsourced,
    }
    _rec_name = 'full_name'
ocs_citizen_service_point()


class ocs_contract(osv.osv):
    """
    Contract Information
    """
    _name="ocs.contract"
    _columns = {
        'contract_id': fields.char('Contract Number',size=20,help="Contract Number or Serial", required=True),
        'start_date': fields.datetime('Start Date',help="When contract start", required=True),
        'end_date': fields.datetime('End Date',help="When contract ends"),
        'description': fields.text('Description',help="Description about this contract"),
        'partner_id': fields.many2one('res.partner','Contractor',size=30,required=True),
    }
    _rec_name = 'contract_id'
ocs_contract()

class ocs_tract(osv.osv):
    # FIXME: This class should change, and the relationships with a CSP is many2many
    """ This class is only for IDU (Instituto Desarrollo Urbano Colombia), who need take control about claims
    in building projects, from outsourcing  """
    def _get_full_name(self,cr,uid,ids,fieldname,arg,context=None):
        """Get Full Name of Contract """
        res = {}
        for tract in self.browse(cr, uid, ids, context = context):
                res[tract.id] = "{0} / {1} ".format(tract.contract_id.contract_id, tract.name)
        return  res

    _name = 'ocs.tract'
    _columns = {
        'full_name':fields.function(_get_full_name,type='char',string='Full Name',method=True),
        'road_id': fields.char('Road ID',size = 16,help="Road Identification Number",required=True),
        'name': fields.char('Description',size=255,required=True),
        'contract_id': fields.many2one('ocs.contract','Contract',required=True),
    }
    _rec_name = 'full_name'
ocs_tract()


def geocode_address(self, cr, uid, ids, addr):
    res = {'value':{'geo_point':False}}
    if addr:
        url_geocoder = self.pool.get('ir.config_parameter').get_param(cr, uid, 'geo_coder.ws.url', default='', context=None)
        srid = "esri.extra:900913"
        zone = 1100100 #Bogota
        point = geo_code_address(extract_basic_address(addr), srid, url_geocoder, zone)
        res['value']['geo_point'] = point
    return res