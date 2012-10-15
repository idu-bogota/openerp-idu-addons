<?php
class OpenErpWebServiceClient {
    public $openerp_server;
    public $username;
    public $pwd;
    public $dbname;
    protected $client;
    protected $user_id;

    public function __construct($openerp_server, $username, $pwd, $dbname) {
        $this->openerp_server = $openerp_server;
        $this->username = $username;
        $this->pwd = $pwd;
        $this->dbname = $dbname;
    }

    protected function login() {
        $client = new Zend_XmlRpc_Client($this->openerp_server.'/common');
        $this->user_id = $client->call('login', array($this->dbname, $this->username, $this->pwd));
        return $this->user_id;
    }

    public function execute($model, $operation, $parameters) {
        if(empty($this->user_id)){
            $this->login();
        }
        if(empty($this->client)) {
            $this->client = new Zend_XmlRpc_Client($this->openerp_server.'/object');
        }
        $auth = array($this->dbname, $this->user_id, $this->pwd);
        $extra = array($model, $operation, $parameters);
        return $this->client->call('execute', array_merge($auth,$extra));
    }
}

abstract class OpenErpObject {
    protected abstract function getClassName();
    protected abstract function getAttributesMetadata();
    protected $client;
    public $id;
    public $attributes;

    public function __construct($ws_client) {
        $this->client = $ws_client;
    }

    public function create() {
        $this->processAttributes();
        $this->checkCompulsoryAttributes();
        return $this->id = $this->client->execute($this->getClassName(), 'create', $this->attributes);
    }

    public function update() {
    }

    public function fetch($args = array()) {
        $ids = $this->client->execute($this->getClassName(), 'search', $args);
        //var_export($ids);
        return $this->load($ids);
    }

    public function fetchOne($args = array()) {
        $ids = $this->client->execute($this->getClassName(), 'search', $args);
        return $this->loadOne($ids);
    }

    public function loadOne($id) {
        return $this->load($id, TRUE);
    }

    public function load($ids, $load_one = FALSE) {
        $classname = get_class($this);
        $result = array();
        if(!is_array($ids)) {
            $ids = array($ids);
        }
        if(empty($ids)) {
            return FALSE;
        }
        foreach($ids as $id){
            $obj = new $classname($this->client);
            $obj->id = $id;
            $obj->attributes = $this->client->execute($this->getClassName(), 'read', $id, $this->getAttributesMetadata());
            $result[] = $obj;
            if($load_one) {
                break;
            }
        }
        if($load_one) {
            $this->id = $result[0]->id;
            $this->attributes = $result[0]->attributes;
            return $this;
        }
        return $result;
    }

    /**
     * Check if compulsory attributes are defined, doesn't check if values are valid
     */
    protected function checkCompulsoryAttributes() {
        $atts = $this->getAttributesMetadata();
        foreach ($atts as $att => $conf) {
            if($conf['compulsory'] && !isset($this->attributes[$att])) {
                throw new Exception(get_class($this)."::$att needs to be defined");
            }
        }
        return TRUE;
    }

    /**
     * Check current $this->attributes and process them to be ready for a create/update operation
     */
    protected function processAttributes(){
        $this->attributes2ForeingKeyId();
    }

    /**
     * Transform attributes in a valid id for attributes related to linked objects
     * The method uses the $this->attributes and the fields metadata to set the right linked object id.
     * You can add the object id or the values to find one or the data to create the object and link it
     */
    protected function attributes2ForeingKeyId() {
        $attributes = $this->attributes;
        $map = $this->getAttributesMetadata();
        $data = array();
        foreach($map as $att => $conf) {
            //var_export($conf);
            if(!empty($conf['references'])) {
                if(isset($attributes[$att])) {
                    $classname = $conf['references']['classname'];
                    $reference_id = $reference = $attributes[$att];
                    if($reference instanceof $classname) {
                        $reference_id = $reference->id;
                    }
                    elseif(is_array($reference)) {
                        $method_name = 'retrieve_or_create_'.strtolower($classname);
                        if(method_exists($this, $method_name)) {
                            $reference = $this->$method_name($attributes, $att);
                        }
                        else {
                            $reference = $this->retrieve_or_create_openerpobject($attributes, $att, $conf);
                        }
                        $reference_id = $reference->id;
                    }
                    if(empty($reference_id)) {
                        throw new Exception("No ID found to set at '".get_class($this)."'::$att");
                    }
                    $data[$att] = $reference_id;
                }
            }
        }
        $this->attributes = array_merge($this->attributes,$data);
    }

    protected function retrieve_or_create_openerpobject($att, $key, $conf) {
        $search_key = 'name';
        if(isset($conf['references']['search_key'])) {
            $search_key = $conf['references']['search_key'];
        }
        $classname = $conf['references']['classname'];
        if(empty($classname)) {
            throw new Exception('class is required');
        }

        $obj = new $classname($this->client);
        if(!isset($att[$key][$search_key])) throw new Exception(get_class($this).'::'.__FUNCTION__.": Search value '$search_key' is not set");
        $search_value = $att[$key][$search_key];
        if($obj->fetchOne(array(array($search_key,'=',$search_value))) === FALSE) {
            $obj->attributes = $att[$key];
            $obj->create();
        }
        return $obj;
    }
}
