# -*- coding: utf-8 -*-
"""
Este modulo contiene las funciones basicas para invocar los servicios web publicados por el Sistema Distrital de Quejas y Soluciones de la Secretaría General de la alcaldía Mayor de Bogotá
"""
import sys
from suds.client import Client
from suds.bindings import binding
from suds.plugin import MessagePlugin

# PLUGIN que se encarga de hacer un hack al request SOAP para agregar el namespace
# https://fedorahosted.org/suds/wiki/Documentation#PLUGINS
class SdqsPlugin(MessagePlugin):
    nsmapping = {
        'registrarRequerimiento': ('sqsRequerimiento','sqsRegistrarRequerimiento'),
        'adjuntarArchivoEnRequerimiento': ('sqsCodigoRequerimientoEstadoRequerimiento','sqsDocumento','sqsAdjuntarArchivoHaciaRequerimento'),
        'cerrarRequerimiento': ('sqsCierreRequerimiento','sqsCerrarRequerimiento'),
        'consultarCodigosError': ('sqsConsultarCodigosError'),
        'consultarEstadoRequerimiento': ('sqsCodigoRequerimientoEstadoRequerimiento','sqsConsultarEstadoRequerimiento'),
        'consultarEstados': ('sqsConsultarEstadosRequerimiento'),
        'consultarHojaRutaRequerimiento': ('sqsCodigoRequerimientoHojaRuta','sqsConsultarHojaRutaRequerimiento'),
        'consultarRequerimiento': ('sqsCodigoRequerimientoConsulta','sqsConsultarRequerimiento'),
        'consultarRequerimientosRangoFechas': ('sqsEntidad','sqsFechaInicio','sqsFechaFin','sqsConsultarRequerimientosPorFecha'),
        'consultarTiposRequerimiento': ('sqsConsultarTiposRequerimiento'),
        'consultarRequerimiento': ('sqsCodigoRequerimientoConsulta','sqsConsultarRequerimiento'),
    }

    def marshalled(self, context):
        servicio = context.envelope.getChild('Body').children[0].name
        cnt = 0
        for prefix_name in self.nsmapping[servicio]:
            parameter = context.envelope.getChild('Body').getChild(servicio)[cnt]
            prefix_key = 'sqs{0}'.format(cnt)
            parameter.prefix = prefix_key
            namespace = context.envelope.nsprefixes[prefix_key] = prefix_name
            cnt += 1

class SdqsClient:
    def __init__(self, url, codigo_verificacion):
        self.client = self.get_client(url)
        self.codigoVerificacion = codigo_verificacion

    def get_client(self,url):
        """
        Retorna cliente del servicio web para SOAP 1.2
        """
        #Parametro que se pasa al cliente SOAP para que cumpla con la spec de SOAP v1.2
        binding.envns = ('SOAP-ENV', 'http://www.w3.org/2003/05/soap-envelope')
        # Creacion del cliente que utiliza el plugin sdqs definido
        return Client(url, plugins=[SdqsPlugin()], headers={'Content-Type': 'application/soap+xml'})

    def last_sent(self):
        return self.client.last_sent();

    def registrarRequerimiento(self, params):
        sdqs_service = getattr(self.client.service, 'registrarRequerimiento')
        return sdqs_service(params, self.codigoVerificacion)

    def consultarRequerimiento(self, codigo_requerimiento):
        sdqs_servicio = getattr(self.client.service, 'consultarRequerimiento')
        return sdqs_servicio(codigo_requerimiento, self.codigoVerificacion)

    def adjuntarArchivoEnRequerimiento(self, codigo_requerimiento, contenido, nombre, mimetype):
        sdqs_servicio = getattr(self.client.service, 'adjuntarArchivoEnRequerimiento')
        documento = {
            'contenidoDocumento': contenido,
            'nombreArchivo': nombre,
            'mimeType': mimetype
        }
        return sdqs_servicio(codigo_requerimiento, documento, self.codigoVerificacion)
