<?php

// This will allow someone to request the most recent peers by timestamp from the database
// The number will be determine by the "num" value in the GET request 
// It will have the following format- guid1,address1,port1:guid2,address2,port2:....etc 

include "./zeitcoins.php";

$zeitcoins = new zeitcoins;

if (isset($_GET['num'])){
	$num=$_GET['num'];
}
else{
	$num=10;
}

$link=$zeitcoins->dbconnect();

$res=$zeitcoins->getpeers($num,$mysqli);

$str1=""
if ($res>0){
	// Peers are return	
	while ($row = $res->fetch_assoc()){
		$str1.=$row['guid'].",".$row['address'].",".$row['port'].":"
	}
	$str1=rtrim($str1, ":");
}
else{
	// The is no peers in the database
	$str1="No peers in the database";
}

echo $str1;
echo "end";

?>
