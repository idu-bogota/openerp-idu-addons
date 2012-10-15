<?php
require dirname(__FILE__).'/../../externals/testmore-php/testmore.php';
require('../config.inc.php');

plan('no_plan');
require_ok('../OpenErpOcs.php');


$time = time();
diag($openerp_server);
diag("time = $time");
diag("username = $username");
diag("db = $dbname");


$c = new OpenErpWebServiceClient($openerp_server, $username, $pwd, $dbname);

//***********************************************************
$partner_address_id = new OpenErpPartnerAddress($c);
$partner_address_id->attributes = array(
    'name' => 'citizen '.$time,
    'document_type' => 'C',
    'document_id' => $time,
    'name' => 'name '.$time,
    'last_name' => 'lastname '.$time,
);

try {
    $id = $partner_address_id->create();
    ok($id > 0, 'Object Created');
}
catch(Exception $e) {
    fail('Object no created due: '. $e->getMessage());
    diag($e->getTraceAsString());
}

//***********************************************************
$partner_id = new OpenErpPartner($c);
$partner_id->attributes = array(
    'name' => 'partner '.$time,
    'ref' => $time
);

try {
    $id = $partner_id->create();
    ok($id > 0, 'Object Created');
}
catch(Exception $e) {
    fail('Object no created due: '. $e->getMessage());
    diag($e->getTraceAsString());
}

//***********************************************************
$pqr_id;
$pqr = new OpenErpPqr($c);
$pqr->attributes = array(
    'partner_id' => $partner_id,
    'partner_address_id' =>  $partner_address_id,
    'categ_id' => array('name' => 'Policy Claim'),
    'classification' => array('name' => 'test '.$time),
    'sub_classification' => array('name' => 'sub test '.$time),
    'description' => 'This is a PQR '.$time,
    'state' => 'pending',
    'priority' => 'h',
    'pcs_id' => array('name' => 'my pcs '.$time),
    'channel' => array('name' => 'direct'),
    'external_dms_id' => $time
);

try {
    $pqr_id = $pqr->create();
    ok($pqr_id > 0, 'PQR created with ID:'.$pqr_id);
}
catch(Exception $e) {
    fail('PQR no created due: '. $e->getMessage());
    diag($e->getTraceAsString());
}

$pqr_load = new OpenErpPqr($c);
$pqr_load->loadOne($pqr_id);
is($pqr_load->id,$pqr_id,'ID found is OK' );
is($pqr_load->attributes['description'],'This is a PQR '.$time,'description is OK' );
is($pqr_load->attributes['state'],'pending','state is OK' );

$pqr_found = new OpenErpPqr($c);
$pqr_found->fetchOneByDmsId($time);
is($pqr_found->id,$pqr_id,'ID found is OK' );
is($pqr_found->attributes['description'],'This is a PQR '.$time,'description is OK' );
is($pqr_found->attributes['state'],'pending','state is OK' );
//var_export($pqr_found->attributes);

//***********************************************************
$pqr = new OpenErpPqr($c);
$pqr->attributes = array(
    'partner_address_id' =>  array(
        'name' => 'citizen '.$time,
        'document_type' => 'C',
        'document_id' => $time,
        'name' => 'name '.$time,
        'last_name' => 'lastname '.$time,
    ),
    'partner_id' => array(
        'name' => 'my organisation '.$time,
        'ref' => 'nit_'.$time,
    ),
    'categ_id' => array('name' => 'Policy Claim'),
    'priority' => 'h',
    'classification_id' => array('name' => 'test '.$time),
    'sub_classification_id' => array('name' => 'sub test '.$time),
    'pcs_id' => array('name' => 'my pcs '.$time),
    'description' => 'This is a PQR '.$time,
    'state' => 'pending',
    'channel' => array('name' => 'direct'),
    'external_dms_id' => $time,
);
try {
    $pqr_id = $pqr->create();
    ok($pqr_id > 0, 'PQR created with ID:'.$pqr_id);
}
catch(Exception $e) {
    fail('PQR no created due: '. $e->getMessage());
    diag($e->getTraceAsString());
}

// $client = new Zend_XmlRpc_Client($openerp_server.'/object');
// $data = array(
//   'partner_address_id' => 4,
//   'partner_id' => 18,
//   'categ_id' => 16,
//   'priority' => 'h',
//   'classification' => 1,
//   'sub_classification' => 2,
//   'pcs_id' => 15,
//   'state' => 'open',
//   'channel' => 3,
//   'description' => 'test',
// );
// echo $id = $client->call('execute', array($dbname, 1, 'admin', 'crm.claim', 'create', $data));
