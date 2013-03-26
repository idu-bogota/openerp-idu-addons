#!/usr/bin/env python
from optparse import OptionParser
import urllib2
import simplejson as json
import pprint
import commands
import os
from subprocess import call

def main():
    usage = "Create an OpenERP database\nusage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-n", "--db_name", dest="db_name", help="New database name")
    parser.add.option("-u", "--db_user",dest="db_user",help="Database user")
    parser.add_option("-p", "--db_password", dest="db_password", help="New database password")
    parser.add_option("-H", "--host", dest="host", help="OpenERP server host", default="localhost")
    parser.add_option("-j", "--port", dest="port", help="OpenERP server port", default="8069")
    parser.add_option("-l", "--db_lang", dest="db_lang", help="New database language", default="en_US")
    parser.add_option("-d", "--demo_data", action="store_true", dest="demo_data", help="New database loads demo data")
    parser.add_option("-g", "--activate_postgis", action="store_true", dest="activate_postgis", help="Activate postgis 1.5")
    parser.add_option("-i", "--init_module", dest="init_module", help="Init module")
    parser.add_option("-s", "--super_admin_pwd", dest="super_admin_pwd", help="Super Admin Password", default="admin")
    parser.add_option("-c", "--config_file", dest="config_file", help="OpenERP config file - absolute path", default="/etc/openerp/openerp-server.conf")
    parser.add_option("-b", "--data_dir", dest="data_dir", help="Folder that includes SQL files to be loaded via psql", default="/opt/addons-idu/data_idu/sql/")
    (options, args) = parser.parse_args()
    #pprint.pprint(options);
    if not options.db_name:
        parser.error('db_name not given')
    if not options.db_password:
        parser.error('db_password not given')

    created = create_openerp_database(options)

    if created and options.activate_postgis:
        activate_postgis_15(options)

    if created and options.init_module:
        init_module(options)

    if created and options.data_dir:
        load_data_dir_files(options)


def create_openerp_database(options):
    data = {
        "jsonrpc":"2.0","method":"call","id":"r11","params": {
            "fields":[
                {"name":"super_admin_pwd","value":options.super_admin_pwd},
                {"name":"db_name","value":options.db_name},
                {"name":"demo_data","value":options.demo_data},
                {"name":"db_lang","value":options.db_lang},
                {"name":"create_admin_pwd","value":options.db_password},
                {"name":"create_confirm_pwd","value":options.db_password}
            ],
            "session_id":""
        },
    }

    req = urllib2.Request('http://' + options.host + ':' + options.port + '/web/database/create')
    req.add_header('Content-Type', 'application/json')
    print "Creating ....";
    resp = urllib2.urlopen(req, json.dumps(data))
    result = json.loads(resp.read())
    #print resp.getcode()
    #print resp.info()
    #print json.dumps(result, sort_keys=True, indent=4)
    try:
        if(result['result']):
            print "Database created: " + options.db_name
            return True
    except KeyError:
        print result['error']['data']['fault_code']
        return False

def activate_postgis_15(options):
    print "Activating postgis 1.5";
    call('sudo su postgres -c "psql -f /usr/share/postgresql/9.1/contrib/postgis-1.5/postgis.sql ' + options.db_name + '"', shell=True)
    call('sudo su postgres -c "psql -f /usr/share/postgresql/9.1/contrib/postgis-1.5/spatial_ref_sys.sql ' + options.db_name + '"', shell=True)

def init_module(options):
    print "Installing module";
    cmd_str = "sudo start-stop-daemon --start --chuid openerp --exec /usr/bin/openerp-server --  --stop-after-init -d %s -r openerp --config=%s -i %s" % (options.db_name, options.config_file, options.init_module)
    call(cmd_str, shell=True)
    print "Restarting OpenERP";
    call('sudo /etc/init.d/openerp restart', shell=True)

def load_data_dir_files(options):
    print 'Loading *.sql files from: ' + options.data_dir;
    for r,d,f in os.walk(options.data_dir):
        for files in f:
            if files.endswith(".sql"):
                filename = os.path.join(r,files)
                print '* ' + filename
                call('sudo su postgres -c "psql -f ' + filename +' ' + options.db_name + '"', shell=True)

if __name__ == '__main__':
    main()
