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
from osv.orm import except_orm
from base_geoengine import geo_model
from crm import crm
from tools.translate import _
import re

class crm_claim(crm.crm_case,osv.osv):
    """
    Inherit from ocs and ocs crm_claim
    """

    def _check_classification_partner_forwarded_id(self, cr, uid, ids, context = None):
        """
        Check a partner_forwarded_id is selected
        """
        is_valid = True
        for claim in self.browse(cr, uid, ids,context):
            classification = self.pool.get('ocs.claim_classification').name_search(cr, uid, name='Trámites a cargo de otras entidades remitidos a IDU', args=None, operator='=', context=None)
            if claim.classification_id.id == classification[0][0] and claim.partner_forwarded_id.id == False:
                is_valid = False
        return is_valid



    def _check_is_outsourced(self,cr,uid,ids,fieldname,arg,context=None):
        """
        Check if the citizen service point is outsourced, with this
        validates when is csp outsourced
        """
        res = {}
        for claim in self.browse(cr, uid, ids, context = context):
            res[claim.id] = claim.csp_id.is_outsourced
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
        result = super(crm_claim, self).onchange_district_id(cr, uid, ids, add)
        address = self.pool.get('res.partner.address').browse(cr, uid, add)
        if(address.twitter):
            channel = self.pool.get('crm.case.channel').name_search(cr, uid, name='Twitter', args=None, operator='=', context=None)
            result['value']['channel'] = channel[0][0]
        if(address.facebook):
            channel = self.pool.get('crm.case.channel').name_search(cr, uid, name='Facebook', args=None, operator='=', context=None)
            result['value']['channel'] = channel[0][0]

        return result

    def onchange_district_id(self, cr, uid, ids, district_id):
        """Restricts the neighborhood list to the selected district_id
        """
        result = super(crm_claim, self).onchange_district_id(cr, uid, ids, district_id)
        d = result['domain']
        v = result['value']
        if district_id:
            district = self.pool.get('ocs.district').browse(cr, uid, district_id)
            if(district.name == 'FUERA DE BOGOTÁ'):
                classification = self.pool.get('ocs.claim_classification').name_search(cr, uid, name='Trámites a cargo de otras entidades remitidos a IDU', args=None, operator='=', context=None, limit=1)
                v['classification_id'] = classification[0][0]

        return {'domain':d, 'value':v}

    def new_from_data(self, cr, uid, data, context = None):
        """
        Metodo que sirve para ser llamado via servicio XML-RPC desde aplicaciones externas
        Retorna {'status': 'success|failed', 'message':'error message','result': {'id': claim.id }}
        """
        print data
        result = {'status': 'success', 'result': {}}
        ctz_uniq_fields = ['document_number','email','twitter','facebook']
        ctz_where = []
        cnt = 0
        for f in ctz_uniq_fields:
            if f in data['partner_address_id']:
                ctz_where.insert(0,(f,'=',data['partner_address_id'][f]))
                cnt += 1
                if cnt > 1:
                    ctz_where.insert(0, '|')

        if len(ctz_where):
            try:
                ctz_ids = self.pool.get('res.partner.address').search(cr, uid, ctz_where)
                ctz_cnt = len(ctz_ids)
                if ctz_cnt == 0:
                    #Crear un nuevo citizen
                    ctz_id = self.pool.get('res.partner.address').create(cr, uid, data['partner_address_id'])
                elif ctz_cnt == 1:
                    #Utilizar citizen y actualizar datos
                    ctz_id = ctz_ids[0]
                    self.pool.get('res.partner.address').write(cr, uid, ctz_ids, data['partner_address_id'])
                elif ctz_cnt > 1:
                    #FIXME: Revisar cual de todos actualizar y utilizar
                    ctz_ids = self.pool.get('res.partner.address').search(cr, uid, [('document_number','=',data['partner_address_id']['document_number'])])
                    ctz_id = ctz_ids[0]
                    self.pool.get('res.partner.address').write(cr, uid, ctz_id, data['partner_address_id'])
            except except_orm as e:
                return {'status': 'failed', 'message': e.value }
            except Exception as e:
                return {'status': 'failed', 'message': e.message }
        else:
            return {'status': 'failed', 'message': 'No hay datos del ciudadano para registrar' }

        data['partner_address_id'] = ctz_id

        try:
            result['result']['id'] = self.create(cr, uid, data, context)
        except except_orm as e:
            return {'status': 'failed', 'message': e.value }
        except Exception as e:
            return {'status': 'failed', 'message': e.message }

        return result

    _name="crm.claim"
    _inherit="crm.claim"
    _columns = {
        'priority': fields.selection([('h','High'),('n','Normal'),('l','Low')], 'Priority', required=True, readonly=True),
        'date_deadline': fields.date('Deadline',readonly=True),
        'state':fields.selection([('draft', 'New'),('open', 'In Progress'),('cancel', 'Cancelled'),
                                  ('review','Review'),('done', 'Closed'),('pending', 'Pending')],
                                 'State',help='Introduce a new state between open and done, in this step,\
                                  other people makes a review and approve the response given to citizen'),
        'is_outsourced':fields.function(_check_is_outsourced,type='boolean',string='Is Outsourced',method=True),
        'contract_reference': fields.char('Contract Reference',size=9,help='Construction contract number number-year',states={'done':[('readonly',True)]}),
        'damage_type_by_citizen': fields.selection([('fisura', 'Fisura'),('hueco', 'Hueco'),('hundimiento', 'Hundimiento')], 'Via Damage Type',help='Damage type provided by the citizen'),
        'damage_width_by_citizen':  fields.char('Via damage width',size=10,help='Damage width provided by the citizen',states={'done':[('readonly',True)]}),
        'damage_length_by_citizen': fields.char('Via damage length',size=10,help='Damage length provided by the citizen',states={'done':[('readonly',True)]}),
        'damage_deep_by_citizen': fields.char('Via damage deep',size=10,help='Damage size provided by the citizen',states={'done':[('readonly',True)]}),
    }
    _constraints = [
        (_check_contract_reference,'Contract Reference format is number-year, ie. 123-2012',['contract_reference']),
        (_check_claim_address,'Claim Address should follow IDU conventions ie. Cr 102 BIS 10 A BIS Z 30 Int 3 Loc 4',['claim_address']),
        (_check_classification_partner_forwarded_id,'Please select partner forwarded',['classification_id']),
    ]

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
            if csp.is_outsourced:
                res[csp.id] = "{0} / {1} ".format(csp.tract_id.full_name, csp.name)
            else :
                res[csp.id] = "{0}".format(csp.name)
        return  res

    _name="ocs.citizen_service_point"
    _inherit="ocs.citizen_service_point"
    _columns = {
        'is_outsourced':fields.boolean('is Outsourced',help='When is set, this is an outsourced citizen service point'),
        'tract_id':fields.many2one('ocs.tract','Tract Id'),
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
        'partner_id': fields.many2one('res.partner','Contractor',size=30,required=True),
    }
    _rec_name = 'contract_id'
ocs_contract()

class ocs_tract(osv.osv):
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
        'name': fields.char('Description',size=20,required=True),
        'contract_id': fields.many2one('ocs.contract','Contract',required=True),
    }
    _rec_name = 'full_name'
ocs_tract()

def is_bogota_address_valid(address):
    """ This function checks if the parameter fits Bogotá D.C. address schema.

    >>> print is_bogota_address_valid('KR 102 10 30')
    True
    >>> print is_bogota_address_valid('KR 102 10 30 INT 2 AP 1023')
    True
    >>> print is_bogota_address_valid('KR 102 10 30 INT 2')
    True
    >>> print is_bogota_address_valid('KR 102 10 30 AP 1123')
    True
    >>> print is_bogota_address_valid('KR 102 A 10 A 30')
    True
    >>> print is_bogota_address_valid('KR 102 A 10 A 30 INT 3 AP 12')
    True
    >>> print is_bogota_address_valid('KR 102 A 10 A BIS 30')
    True
    >>> print is_bogota_address_valid('KR 102 A 10 A BIS Z 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS 10 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS 10 30 AP 12')
    True
    >>> print is_bogota_address_valid('KR 102 BIS 10 A 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS 10 BIS 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS 10 BIS Z 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS 10 A BIS 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS 10 A BIS Z 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS 10 A BIS Z 30 INT 3 LOC 4')
    True
    >>> print is_bogota_address_valid('KR 102 BIS A 10 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS A 10 30 E')
    True
    >>> print is_bogota_address_valid('KR 102 BIS A 10 A 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS A 10 A BIS 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS A 10 A BIS A 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS A 10 A BIS A 30 LOC 5')
    True
    >>> print is_bogota_address_valid('KR 102 BIS A 10 BIS Z 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS 10 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS 10 A 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS 10 A BIS 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS 10 A BIS A 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS 10 BIS Z 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS Z 10 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS Z 10 30 SE')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS Z 10 A 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS Z 10 A BIS 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS Z 10 A BIS A 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS Z 10 BIS Z 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS Z 10 BIS Z 30 N')
    True
    >>> print is_bogota_address_valid('TV 34 F 45 B BIS Z 32 MZ 32 INT 5 TO 23 AP 123 S')
    True
    >>> print is_bogota_address_valid('CL 22 A 52 07 TO C AP 1102')
    True
    """
    st_type = '(CL|AC|DG|KR|AK|TV|CA|CT|PS)'
    st_number = '[0-9]+'
    st_suffix = '(\s[A-Z])?((\sBIS)|(\sBIS\s[A-Z]))?'
    st_horizontal = '(\s(AP|OF|CON|PEN|LOC|DEP|GJ)\s[0-9]+)?'
    st_interior = '(\s((INT|BQ|TO|CA)\s[0-9A-Z]+))?'
    st_manzana = '(\s((MZ|LO|ET)\s[A-Z0-9]+))?'
    st_sector = '(\s(N|E|S|O|NE|SE|SO|NO))?'
    regex = "^{0}\s{1}{2}\s{1}{2}\s{1}{6}{6}{3}{3}{4}{5}$".format(st_type, st_number, st_suffix, st_interior, st_horizontal, st_sector, st_manzana);
    #print regex
    if re.match(regex, address) != None:
        return True
    else:
        return False


if __name__ == "__main__":
    import doctest
    doctest.testmod()