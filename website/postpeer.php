<?php

// This will allow peers to POST their guid, address and port to the database
// This database will be used for bootstrapping and secondary source for peer locations
// Need to find a way to keep someone from spamming this webpage and putting
// abunch of bogus data into the database thus messing up the bootstrapping process

include "./zeitcoins.php";

$zeitcoins = new zeitcoins;

$ipaddress = $_SERVER["REMOTE_ADDR"];

if (isset($_POST['guid'])&&isset($_POST['address'])&&isset($_POST['port'])&&$ipaddress==$address){
	$guid=$_POST['guid'];
	$address=$_POST['address'];
	$port=$_POST['port'];

	$link=$zeitcoins->dbconnect();

	$r1=$zeitcoins->checkguid($guid,$link);
	if ($r1>0){
		// The guid exist in the database thus just update address,port and timestamp
		$r2=$zeitcoins->updatepeer($guid,$address,$port,$link);	
	}
	else{
		// The guid does not exist in the database thus add the peer
		$r2=$zeitcoins->addpeer($guid,$address,$port,$link);
	}
}

echo "ok";

?>
