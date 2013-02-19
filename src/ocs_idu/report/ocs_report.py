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
#    but WITHOUT ANY WARRANTY, without even the implied warranty of
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

import base64
from osv import fields,osv
from tools.translate import _
import time
import cStringIO as StringIO
import csv

class ocs_report(osv.osv_memory):
    """
    Wizard to create custom report
    """
    _name = "report"
    _description = "Create Report"
    _columns = {
                'start_date' : fields.date('Fecha Inicial', required=True),
                'end_date' : fields.date('Fecha Final', required=True),
                'data': fields.binary('Archivo', readonly=True),
                'filename': fields.char('Nombre del archivo', 32, readonly=True),
                'state': fields.selection( ( ('choose','choose'),# choose date
                     ('get','get'),# get the file
                   ) ),
                }
   
    def create_report(self,cr,uid,ids,context={}):
        this = self.browse(cr, uid, ids)[0]
        cr.execute("""SELECT
              pqr.id AS "ID",
              pqr.create_date::timestamp::date AS "Fecha de atención (a-m-d)",
              COALESCE(ctz.document_type,'NO REPORTA')  AS "Tipo de documento",
              COALESCE(ctz.document_number,'NO REPORTA') AS "Número documento de identidad",
              COALESCE(ctz.name,'NO REPORTA') AS "Nombres",
              COALESCE(ctz.last_name,'NO REPORTA') AS "Apellidos",
              COALESCE(ctz.gender,'NO REPORTA') AS "Genero",
              COALESCE(ctz.mobile,ctz.phone,ctz.email,ctz.twitter,ctz.facebook,ctz.fax,'NO REPORTA') AS "Datos de contacto",
              COALESCE(ctz.street,'NO REPORTA') AS "Dirección correspondencia",
              COALESCE(ctz_loc.name,'NO REPORTA') AS "Localidad Correspondencia",
              COALESCE(ctz_bar.name,'NO REPORTA') AS "Barrio Correspondencia",
              COALESCE(pqr.claim_address,'NO REPORTA') AS "Dirección del asunto",
              COALESCE(pqr_loc.name,'NO REPORTA') AS "Localidad",
              COALESCE(pqr_bar.name,'NO REPORTA') AS "Barrio",
              COALESCE(cri.name,'NO REPORTA') AS "Criterio (Tipificación)",
              COALESCE(scr.name,'NO REPORTA') AS "Sub Criterio",
              COALESCE(tip.name,'NO REPORTA') AS "Tipo requerimiento",
              COALESCE(pqr.description,'NO REPORTA') AS "Asunto",
              COALESCE(pqr.resolution,'NO REPORTA') AS "Solución",
              COALESCE(can.name,'NO REPORTA') AS "Canal de atención",
              COALESCE(usr.name,'NO REPORTA') AS "Funcionario que atendió",
              COALESCE(pqr.contract_reference,'NO REPORTA') AS "Contrato o Convenio",
              COALESCE(ent.name,'NO REPORTA') AS "Entidad",
              pqr.state AS "Estado"
            FROM
              crm_claim AS pqr
              LEFT JOIN res_partner_address AS ctz ON pqr.partner_address_id = ctz.id
              LEFT JOIN ocs_claim_classification AS cla ON pqr.classification_id = cla.id
              LEFT JOIN ocs_district AS ctz_loc ON ctz.district_id = ctz_loc.id
              LEFT JOIN ocs_neighborhood AS ctz_bar ON ctz.neighborhood_id = ctz_bar.id
              LEFT JOIN ocs_district AS pqr_loc ON pqr.district_id = pqr_loc.id
              LEFT JOIN ocs_neighborhood AS pqr_bar ON pqr.neighborhood_id = pqr_bar.id
              LEFT JOIN ocs_claim_classification AS cri ON pqr.classification_id = cri.id
              LEFT JOIN ocs_claim_classification AS scr ON pqr.sub_classification_id = scr.id
              LEFT JOIN crm_case_categ AS tip ON pqr.categ_id = tip.id
              LEFT JOIN crm_case_channel AS can ON pqr.channel = can.id
              LEFT JOIN res_users AS usr ON pqr.create_uid = usr.id
              LEFT JOIN res_partner AS ent ON pqr.partner_forwarded_id = ent.id 
          WHERE 
              pqr.create_date BETWEEN '{0}' AND '{1}'
          """.format(this.start_date, this.end_date))

        csvfile = StringIO.StringIO()
        csvwriter = csv.writer(csvfile, dialect='excel')
        csvwriter.writerow(["ID","Fecha de atención (a-m-d)","Tipo de documento","Número documento de identidad","Nombres","Apellidos","Genero","Datos de contacto","Dirección correspondencia","Localidad Correspondencia","Barrio Correspondencia","Dirección del asunto","Localidad","Barrio","Criterio (Tipificación)","Sub Criterio","Tipo requerimiento","Asunto","Solución","Canal de atención","Funcionario que atendió","Contrato o Convenio","Entidad","Estado"])
        map(lambda x:csvwriter.writerow(x), cr.fetchall())
        out = base64.encodestring(csvfile.getvalue())
        return self.write(cr, uid, ids, {'state':'get', 'data':out, 'filename':'pqr_{0}_{1}.csv'.format(this.start_date, this.end_date)}, context=context)
       
    _defaults = {
                 'state': lambda *a: 'choose',
                 'start_date' : lambda *a: time.strftime('%Y-%m-%d'),
                 'end_date' : lambda *a: time.strftime('%Y-%m-%d'),
                }


ocs_report()