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
from crm import crm
from crm_claim import crm_claim
from osv import fields,osv

class crm_claim(osv.osv):
    _name = "crm.claim"
    _inherit = "crm.claim"

    _columns={
        'sdqs_id':fields.char('SDQS ID',size=128,help='Sistema Distrital de Quejas y Soluciones de la Alcaldía de Bogotá D.C. Número de radicado',readonly=True,states={'draft':[('readonly',False)],'open':[('readonly',False)]}),
    }
crm_claim()


class crm_case_categ(osv.osv):
    "This class enable/Disable Categories according current politics"
    _name="crm.case.categ"
    _inherit="crm.case.categ"
    _columns={        
        'sdqs_req_type':fields.integer('sdqs_req_type',help='SDQS request type'),
    }
crm_case_categ()