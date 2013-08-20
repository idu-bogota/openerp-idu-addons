>>> from wsclient import SdqsClient
>>> import logging
>>> url = 'http://sdqspruebas.alcaldiabogota.gov.co/sdqs-ws/radicacion?wsdl'
>>> client = SdqsClient(url,1)
>>> #logging.basicConfig(level=logging.DEBUG)
>>> #logging.getLogger('suds.client').setLevel(logging.DEBUG)

-------------------------------------------
Prueba de ciudadano anónimo - Campos vacios
-------------------------------------------

>>> params = {
...     "numeroDocumento": "",
...     "nombres": "",
...     "apellidos": "",
...     "email": "",
...     "telefonoCasa": "",
...     "telefonoOficina": "",
...     "telefonoCelular": "",
...     "direccion": "",
...     "numeroRadicado": "ABC0002",
...     "numeroFolios": "2",
...     "asunto": "Prueba usuario anonimo completo",
...     "codigoCiudad": "11001",
...     "codigoDepartamento": "250",
...     "codigoPais": "1",
...     "codigoTipoRequerimiento": "1",
...     "clasificacionRequerimiento": {
...     "codigoSector": [11],
...     "codigoEntidad": [143],
...     "codigoSubtema": [4],
...     },
...     "observaciones": "Esto es una prueba de registro 2.",
...     "prioridad": "2",
...     "entidadQueIngresaRequerimiento": 2972,
...     }
>>> r = client.registrarRequerimiento(params)
>>> #print client.last_sent()
>>> r['codigoError']
0
>>> r['codigoRequerimiento'] > 0
True
>>> consulta = client.consultarRequerimiento(r['codigoRequerimiento'])
>>> consulta['codigoError']
0
>>> consulta_fields = ('nombres','apellidos','asunto','codigoCiudad','codigoDepartamento',
... 'codigoPais','codigoTipoRequerimiento','entidadQueIngresaRequerimiento',
... 'numeroDocumento','numeroFolios','numeroRadicado','observaciones', 'prioridad'
... )
>>> for f in consulta_fields:
...     print "'{0}': {1}".format(f, str(consulta['requerimiento'][f]).upper() == str(params[f]).upper())
'nombres': True
'apellidos': True
'asunto': True
'codigoCiudad': True
'codigoDepartamento': True
'codigoPais': True
'codigoTipoRequerimiento': True
'entidadQueIngresaRequerimiento': True
'numeroDocumento': True
'numeroFolios': True
'numeroRadicado': True
'observaciones': True
'prioridad': True

-----------------------------------------------
Prueba de ciudadano anónimo - Sin enviar campos
-----------------------------------------------

>>> params = {
...     "numeroRadicado": "ABC0003",
...     "numeroFolios": "2",
...     "asunto": "Prueba usuario anonimo completo",
...     "codigoCiudad": "11001",
...     "codigoDepartamento": "250",
...     "codigoPais": "1",
...     "codigoTipoRequerimiento": "1",
...     "clasificacionRequerimiento": {
...     "codigoSector": [11],
...     "codigoEntidad": [143],
...     "codigoSubtema": [4],
...     },
...     "observaciones": "Esto es una prueba de registro 2.",
...     "prioridad": "2",
...     "entidadQueIngresaRequerimiento": 2972,
...     }
>>> r = client.registrarRequerimiento(params)
>>> #print client.last_sent()
>>> r['codigoError']
0
>>> r['codigoRequerimiento'] > 0
True
>>> consulta = client.consultarRequerimiento(r['codigoRequerimiento'])
>>> consulta['codigoError']
0
>>> consulta_fields = ('asunto','codigoCiudad','codigoDepartamento',
... 'codigoPais','codigoTipoRequerimiento','entidadQueIngresaRequerimiento',
... 'numeroFolios','numeroRadicado','observaciones', 'prioridad'
... )
>>> for f in consulta_fields:
...     print "'{0}': {1}".format(f, str(consulta['requerimiento'][f]).upper() == str(params[f]).upper())
'nombres': True
'apellidos': True
'asunto': True
'codigoCiudad': True
'codigoDepartamento': True
'codigoPais': True
'codigoTipoRequerimiento': True
'entidadQueIngresaRequerimiento': True
'numeroDocumento': True
'numeroFolios': True
'numeroRadicado': True
'observaciones': True
'prioridad': True
