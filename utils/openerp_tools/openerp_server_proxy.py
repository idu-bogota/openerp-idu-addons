# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Instituto de Desarrollo Urbano (<http://www.idu.gov.co>). 
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Autor Andres Ignacio Báez Alba
#
#
#########t#####################################################################
import xmlrpclib

class openerp_proxy():
    def __int__(self,openerp_server,port,user,passwd,dbname):
        self._openerp_server = openerp_server
        self._port = port
        self._user = user
        self._passwd = passwd
        self._dbname = dbname
        self._openerp_server_url = "http://"+self._openerp_server+":"+self._port+"/xmlrpc/"
        self._isLoggedIn = False
        self._uid = self.__login()
        
    def __login(self):
        #Hace loggin automaticamente en openerp
        print "Haciendo loggin en openerp"
        sock_login = xmlrpclib.ServerProxy(self.openerp_server_url+"common")
        uid = sock_login.login(self._dbname,self._user,self._passwd)
        print "hecho"
        if self.uid == 0:
            raise Exception ("No se puede hacer loggin en openerp")
        else:
            self._isLoggedIn = True
        return uid 

    def create(self,object,vals):
        #Ejecuta un metodo crear en openerp
        if not self._isLoggedIn:
            self.__login()
        print "Creando objeto "+object+"en openerp"
        sock = xmlrpclib.ServerProxy(self._openerp_server_url+"object")
        id_object = xmlrpclib.execute(self._dbname,self._uid,self._passwd,object,'create',vals)
        print "hecho"
        return id_object

    def write(self, object,id,vasl):
        if not self._isLoggedIn:
            self.__login()
        print "Actualizando objeto "+object+"en openerp"
        sock = xmlrpclib.ServerProxy(self._openerp_server_url+"object")
        result = xmlrpclib.execute(self._dbname,self._uid,self._passwd,object,'write',id,vals)
        print "hecho"
        return result

    def search (self,object,args):
        if not self._isLoggedIn:
            self.__login()
        print "Buscando objeto "+object+"en openerp"+args
        sock = xmlrpclib.ServerProxy(self._openerp_server_url+"object")
        id_object = xmlrpclib.execute(self._dbname,self._uid,self._passwd,object,'search',args)
        print "hecho"
        return True
    
    def unlink (self,object,ids):
        if not self._isLoggedIn:
            self.__login()
        print "Buscando objeto "+object+"en openerp"+args
        sock = xmlrpclib.ServerProxy(self._openerp_server_url+"object")
        id_object = xmlrpclib.execute(self._dbname,self._uid,self._passwd,object,'unlink',ids)
        print "hecho"
        return True
    
    def execute_method(self,object,method,args):
        if not self._isLoggedIn:
            self.__login()
        print "Ejecutando método "+method+" en objeto "+object+"en openerp"
        sock = xmlrpclib.ServerProxy(self._openerp_server_url+"object")
        id_object = xmlrpclib.execute(self._dbname,self._uid,self._passwd,object,method,args)
        print "hecho"
        return True
