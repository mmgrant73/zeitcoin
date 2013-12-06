<?php

// PHP class that will store and retrieve (guid,address,port) from the zeitcoin database
// Is used with bootstraping the zeitcoin network and a place where one can find other peers
// This will be one of many ways used for bootstrapping and finding peers
// When new peer joins the network it will look here to find peers
// Table: peer - guid, address, port, timestamp
//        Transaction - txid,thash,timestamp

class zeitcoins{
	public dbhost="localhost";
	public dbuser="mmgrant73";
	public dbpassword="mmgrant3672";
	public db="zeitcoins";
	
	private function dbconnect(){
		$mysqli = new mysqli($this->$dbhost, $this->dbuser, $this->dbpassword, $this->db);
		if ($mysqli->connect_errno) {
			//echo "Failed to connect to MySQL: " . $mysqli->connect_error;
			$this->writeerror("Could not connect to the zeitcoins database". $mysqli->connect_error);
			return false;
		}
		return $mysqli;
	}
	
	public function addpeer($guid,$address,$port,$mysqli){
		$tstamp=time();
		$str1="INSERT INTO zeitpeers (guid, address, port, timestamp) VALUES ('$guid', '$address', '$port', '$tstamp')";
		$res = $mysqli->query($str1);
		if(!$res){
			//error
			$this->writeerror("Could not add peer to the zeitpeer table ($str1), database error code - 284");
		}
		return $res;
	}

	public function addtx($txid,$thash,$tstamp,$mysqli){
		$tstamp=time();
		$str1="INSERT INTO zeittx (txid, thash, timestamp) VALUES ('$txid', '$thash', '$tstamp')";
		$res = $mysqli->query($str1);
		if(!$res){
			//error
			$this->writeerror("Could not add peer to the zeittx table ($str1), database error code - 284");
		}
		return $res;
	}
	
	public function updatepeer($guid,$address,$port,$mysqli){
		$tstamp=time();
		$str1="UPDATE zeitpeer SET address='$address', port='$port', timestamp='$tstamp'where guid=$guid";
		$res = $mysqli->query($str1);
		if(!$res){
			//error
			$this->writeerror("Could not update peer in the zeitpeer table ($str1), database error code - 284");
		}
		return $res;
	}

	public function updatepeertime($guid,$mysqli){
		$tstamp=time();
		$str1="UPDATE zeitpeer SET timestamp='$tstamp' where guid=$guid";
		$res = $mysqli->query($str1);
		if(!$res){
			//error
			$this->writeerror("Could not update peer timestamp in the zeitpeer table ($str1), database error code - 284");
		}
		return $res;
	}
	
	public function deletepeer($guid,$mysqli){
		$str1="DELETE FROM zeitpeer where guid=$guid"
		$res = $mysqli->query($str1);
		if(!$res){
			//error
			$this->writeerror("Could not delete peer from the zeitpeer table ($str1), database error code - 284");
		}
		return $res;
	}
	
	public function checkguid($guid,$mysqli){
		$str1="SELECT guid from zeitpeer where guid=$guid";
		$res = $mysqli->query($str1);
		if(!$res){
			//error
			$this->writeerror("Could not run the select guid on the zeitpeer table ($str1), database error code - 284");
			return -1;
		}
		$rows1 = $res1->num_rows;
		return $rows1;
	}
	
	public function checktx($txid,$mysqli){
		$str1="SELECT txid from zeittx where txid=$txid";
		$res = $mysqli->query($str1);
		if(!$res){
			//error
			$this->writeerror("Could not run the select yxid on the zeittx table ($str1), database error code - 284");
			return -1;
		}
		$rows1 = $res1->num_rows;
		return $rows1;
	}

	public function getpeeraddress($guid,$mysqli){
		$str1="SELECT address,port from zeitpeer where guid=$guid";
		$res = $mysqli->query($str1);
		if(!$res){
			//error
			$this->writeerror("Could not run the select query on the zeitpeer table ($str1), database error code - 284");
			return false;
		}
		$row = $res->fetch_assoc();
		$address=$row['address'].":".$row['port'];
		return $address;
	}
	
	public function getpeers($numpeer,$mysqli){
		$str1="SELECT guid,address,port from zeitpeer order by timestamp limit $numpeer";
		$res = $mysqli->query($str1);
		if(!$res){
			$this->writeerror("Could not run the select query from the zeitpeer table ($str1), database error code - 284");
			return 0;
		}
		return $res;
	}

	public function getrecentpeers($mysqli){
		$str1="SELECT guid,address,port from zeitpeer order by timestamp limit 1";
		$res = $mysqli->query($str1);
		if(!$res){
			$this->writeerror("Could not run the select query from the zeitpeer table ($str1), database error code - 284");
			return false;
		}
		return $res;
	}

	public function getrecenttx($numtxid,$mysqli){
		$str1="SELECT txid,thash,timestamp from zeittx order by timestamp limit $numtxid";
		$res = $mysqli->query($str1);
		if(!$res){
			$this->writeerror("Could not run the select query from the zeittx table ($str1), database error code - 284");
			return false;
		}
		return $res;
	}
	
	private function writeerror($strerror){
		// Let's make sure the file exists and is writable first.
		$filename = './admin/errorlog.txt';
		$tstamp1 = new DateTime('NOW');
		$tstamp=$tstamp1->format('Y-m-d H:i:s');
		$remoteadd = $_SERVER['REMOTE_ADDR'];
		$str1="$tstamp  -  $remoteadd  -  $strerror";
		if (is_writable($filename)) {
	
			if (!$handle = fopen($filename, 'a')) {
				//echo "Cannot open file ($filename)";
				exit;
			}
	
			if (fwrite($handle, $str1) === FALSE) {
				//echo "Cannot write to file ($filename)";
				exit;
			}
	
			//echo "Success, wrote ($somecontent) to file ($filename)";
	
		}
		else {
			//echo "The file $filename is not writable";
		}
		fclose($handle);
	}
	
}
?>
