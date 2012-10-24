{
  'name': 'Módulo para crear datos del IDU',
  'version': '1.0',
  'category': 'Generic Modules/Others',
  'description': "Módulo para cargar datos usados en el IDU",
  'author': 'STRT',
  'website': 'http://www.idu.gov.co',
  'depends': ['base'],
  'init_xml': [
      'crm.case.categ.csv',
      'crm.case.channel.csv',
      'ocs.citizen_service_point.csv',
      'ocs.claim_classification.csv'
  ],
  'update_xml': [],
  'installable': True,
  'active': False,
}