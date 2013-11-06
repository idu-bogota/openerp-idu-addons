>>> from wsclient import SdqsClient
>>> import logging
>>> url = 'http://sdqspruebas.alcaldiabogota.gov.co/sdqs-ws/radicacion?wsdl'
>>> client = SdqsClient(url,1)
>>> #logging.basicConfig(level=logging.DEBUG)
>>> #logging.getLogger('suds.client').setLevel(logging.DEBUG)

----------------------------------
Prueba de registro con adjunto
----------------------------------

>>> params = {
...     "numeroRadicado": "ABC0003-attachment",
...     "numeroFolios": "3",
...     "asunto": "Prueba con adjunto",
...     "nombres": "mi nombre",
...     "apellidos": "mi apellido",
...     "telefonoCasa": "200000002",
...     "codigoCiudad": "11001",
...     "codigoDepartamento": "250",
...     "codigoPais": "1",
...     "codigoTipoRequerimiento": "1",
...     "clasificacionRequerimiento": {
...     "codigoSector": [11],
...     "codigoEntidad": [143],
...     "codigoSubtema": [4],
...     },
...     "observaciones": "Esto es una prueba de registro con adjunt.",
...     "prioridad": "2",
...     "entidadQueIngresaRequerimiento": 2972,
...     }
>>> import base64
>>> path = '/etc/lsb-release'
>>> with open(path, "rb") as myfile:
...     params['documento'] = {
...         'contenidoDocumento': base64.b64encode(myfile.read()),
...         'nombreArchivo': 'mi_test.txt',
...         'mimeType': 'plain/text'
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

----------------------------------
Prueba de adjunto
----------------------------------

>>> params = {
...     "numeroRadicado": "ABC0003-attachment",
...     "numeroFolios": "3",
...     "asunto": "Prueba con adjunto",
...     "nombres": "mi nombre",
...     "apellidos": "mi apellido",
...     "telefonoCasa": "200000002",
...     "codigoCiudad": "11001",
...     "codigoDepartamento": "250",
...     "codigoPais": "1",
...     "codigoTipoRequerimiento": "1",
...     "clasificacionRequerimiento": {
...     "codigoSector": [11],
...     "codigoEntidad": [143],
...     "codigoSubtema": [4],
...     },
...     "observaciones": "Esto es una prueba de registro con adjunt.",
...     "prioridad": "2",
...     "entidadQueIngresaRequerimiento": 2972,
...     }
>>> r = client.registrarRequerimiento(params)
>>> path = '/etc/lsb-release'
>>> with open(path, "rb") as myfile:
...     documento = base64.b64encode(myfile.read())

>>> r = client.adjuntarArchivoEnRequerimiento(r['codigoRequerimiento'], documento, 'test.txt', 'plain/text')
>>> #print client.last_sent()
>>> r['codigoError']
0
