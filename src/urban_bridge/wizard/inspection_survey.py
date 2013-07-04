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
#
#    Creado por Andres Ignacio Baez Alba
#
##############################################################################

from osv import osv, fields
from lxml import etree
from ast import literal_eval
#from suds.client import Client

class urban_bridge_wizard_inspection_survey(osv.osv_memory):
    _name="urban_bridge.wizard.inspection_survey"
    _description="Creates a survey for the Bridge"
    _columns={
        'name':fields.char('Name',size=128),
        'bridge_id':fields.many2one('urban_bridge.bridge','Bridge')
    }
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        """
        Fields View Get method :- generate the new view and display the survey pages of selected survey.
        """
        result = super(urban_bridge_wizard_inspection_survey, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar,submenu)
        
        #1. Mostrar de acuerdo a la metodología escogida los datos que son generales
        
        #2. De acuerdo al inventario existente para cada elemento de infraestructura, se muestra los aspectos que 
        #se deben evaluar
        
        #3. De acuerdo a los valores ingresados por el usuario se manda un vector de datos al interpretador para que muestre 
        #el resultado del diagnostico...
        
        #4. El resultado del diagnostico se debe almacenar en el objeto inspection_survey para obtener la calificacion general
        # del puente de acuerdo con la metodología seleccionada.
        
        return result

urban_bridge_wizard_inspection_survey()