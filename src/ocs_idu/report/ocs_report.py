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
import time
import cStringIO as StringIO
import csv, xlwt
from datetime import datetime

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
                'format': fields.selection( ( ('xls','MS Excel'),
                     ('csv','CSV - Comma Separated Values'),
                   ), 'Formato del reporte', required=True ),
                }
   
    def create_report(self,cr,uid,ids,context={}):
        this = self.browse(cr, uid, ids)[0]

        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        otc = False
        otc_admin = False
        otc_admin_outsourced = False
        otc_user = False
        otc_user_outsourced = False
        otc_reviewer = False
        otc_reader = False

        for grp in user.groups_id:
            grp_id = grp.get_external_id()[grp.id] # Returns the external id like ocs.group_ocs_outsourced_user
            if grp_id == 'ocs.group_ocs_user':
                otc_user = True
                otc = True

            if grp_id == 'ocs_idu.group_ocs_outsourced_user':
                otc_user_outsourced = True
                otc = True

            if grp_id == 'ocs.group_ocs_manager':
                otc_admin = True
                otc = True

            if grp_id == 'ocs_idu.group_ocs_outsourced_manager':
                otc_admin_outsourced = True
                otc = True

            if grp_id == 'ocs_idu.group_ocs_outsourced_reviewer':
                otc_reviewer = True
                otc = True

            if grp_id == 'ocs_idu.group_ocs_outsourced_reader':
                otc_reader = True
                otc = True


        query = """SELECT
              pqr.id AS "ID",
              pqr.create_date::timestamp::date AS "Fecha de atención (a-m-d)",
              COALESCE(ctz.document_type,'NO REPORTA')  AS "Tipo de documento",
              COALESCE(ctz.document_number,'NO REPORTA') AS "Número documento de identidad",
              COALESCE(ctz.name,'NO REPORTA') AS "Nombres",
              COALESCE(ctz.last_name,'NO REPORTA') AS "Apellidos",
              COALESCE(ctz.gender,'NO REPORTA') AS "Genero",
              COALESCE(ctz.mobile,ctz.phone,ctz.email,ctz.twitter,ctz.facebook,ctz.fax,'NO REPORTA') AS "Datos de contacto",
              COALESCE(ctz.street,'NO REPORTA') AS "Dirección correspondencia",
              COALESCE(ctz_bar.name,'NO REPORTA') AS "Barrio Correspondencia",
              COALESCE(ctz_loc.name,'NO REPORTA') AS "Localidad Correspondencia",
              COALESCE(pqr.claim_address,'NO REPORTA') AS "Dirección del asunto",
              COALESCE(pqr_bar.name,'NO REPORTA') AS "Barrio",
              COALESCE(pqr_loc.name,'NO REPORTA') AS "Localidad",
              COALESCE(cri.name,'NO REPORTA') AS "Criterio (Tipificación)",
              COALESCE(scr.name,'NO REPORTA') AS "Sub Criterio",
              COALESCE(tip.name,'NO REPORTA') AS "Tipo requerimiento",
              COALESCE(pqr.description,'NO REPORTA') AS "Asunto",
              COALESCE(pqr.resolution,'NO REPORTA') AS "Solución",
              COALESCE(can.name,'NO REPORTA') AS "Canal de atención",
              COALESCE(usr.name,'NO REPORTA') AS "Funcionario que atendió",
              COALESCE(csp.name,'NO ASIGNADO') AS "Punto de atención",
              CASE WHEN csp.is_outsourced=TRUE THEN COALESCE(ctr.contract_id,'NO ASIGNADO')
                  WHEN csp.is_outsourced=FALSE THEN COALESCE(pqr.contract_reference,'NO REPORTA')
              END AS "Contrato o Convenio",
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
              LEFT JOIN ocs_citizen_service_point as csp ON pqr.csp_id = csp.id
              LEFT JOIN ocs_contract as ctr ON csp.contract_id = ctr.id
          WHERE 
              pqr.create_date BETWEEN '{0}' AND '{1}'
          """.format(this.start_date, this.end_date)

        if not otc:
            raise osv.except_osv(_('Error'),_('Su usuario no tiene asignado ningún grupo de la OTC'))

        if (otc_admin or otc_admin_outsourced):
            if (otc_admin and otc_admin_outsourced):
                pass
            elif (otc_admin):
                query += " AND csp.is_outsourced = FALSE"
            elif (otc_admin_outsourced):
                query += " AND csp.is_outsourced = TRUE"
        elif (otc_user):
            query += " AND pqr.create_uid = {0}".format(uid)
        elif (otc_reviewer or otc_reader or otc_user_outsourced):
            query += " AND pqr.csp_id IN ({0})".format(",".join(str(x) for x in user.get_csp_ids))

        cr.execute(query)
        out = ''
        headers = ("ID",u"Fecha de atención (a-m-d)","Tipo de documento",u"Número documento de identidad","Nombres","Apellidos","Genero","Datos de contacto",u"Dirección correspondencia","Barrio Correspondencia","Localidad Correspondencia",u"Dirección del asunto","Barrio","Localidad",u"Criterio (Tipificación)","Sub Criterio","Tipo requerimiento","Asunto",u"Solución",u"Canal de atención",u"Funcionario que atendió",u"Punto de Atención","Contrato o Convenio","Entidad","Estado")
        if(this.format == 'csv'):
            csvfile = StringIO.StringIO()
            csvwriter = csv.writer(csvfile, dialect='excel')
            csvwriter.writerow(headers)
            map(lambda x:csvwriter.writerow(x), cr.fetchall())
            out = base64.encodestring(csvfile.getvalue())
        else:
            xlsfile = StringIO.StringIO()

            date_style = xlwt.XFStyle()
            date_style.num_format_str = 'DD-MM-YYYY'
            bold_font = xlwt.Font()
            bold_font.bold = True
            bold_style = xlwt.XFStyle()
            bold_style.font = bold_font

            wb = xlwt.Workbook()
            ws = wb.add_sheet('Reporte PQR')

            ws.write(0, 0, 'Reporte PQRs periodo: {0} {1}'.format(this.start_date, this.end_date), bold_style)
            row_cnt = 2;
            results = cr.fetchall()
            results.insert(0, headers)
            for row in results:
                col_cnt = 0
                for value in row:
                    if(row_cnt != 2 and col_cnt == 1):
                        ws.write(row_cnt, col_cnt, datetime.strptime(value, '%Y-%m-%d'), date_style)
                    elif(row_cnt == 2):
                        ws.write(row_cnt, col_cnt, value, bold_style)#set Bold style to header
                    else:
                        ws.write(row_cnt, col_cnt, value)
                    col_cnt += 1
                row_cnt += 1
            wb.save(xlsfile)
            out = base64.encodestring(xlsfile.getvalue())

        return self.write(cr, uid, ids, {'state':'get', 'data':out, 'filename':'pqr_{0}_{1}.{2}'.format(this.start_date, this.end_date, this.format)}, context=context)
       
    _defaults = {
                 'state': lambda *a: 'choose',
                 'start_date' : lambda *a: time.strftime('%Y-%m-%d'),
                 'end_date' : lambda *a: time.strftime('%Y-%m-%d'),
                 'format': 'xls',
                }


ocs_report()