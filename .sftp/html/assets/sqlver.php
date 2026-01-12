<?php
require_once ($_SERVER['DOCUMENT_ROOT'].'/core/config/config.inc.php');
require_once (MODX_CORE_PATH.'model/modx/modx.class.php');


function make_query($modx, $query)
{
	$output = false;
	$stmt = $modx->prepare($query);
	
	if ($stmt && $stmt->execute()){
		$output = true;
	}else{
		$modx->log(modX::LOG_LEVEL_ERROR, "sqlver ".$query . "\n" . implode(', ',$stmt->errorInfo()));
	}
    $stmt->closeCursor();
	return $output;
}

function make_count_query($modx, $query)
{
    $count = 0;
    $stmt = $modx->prepare($query);
    if ($stmt && $stmt->execute()){
        $count = $stmt->fetchColumn();
        //$modx->log(modX::LOG_LEVEL_ERROR, "sqlver row count " . $count);
    }else{
        $modx->log(modX::LOG_LEVEL_ERROR, "sqlver " . $query . "\n" . implode(', ',$stmt->errorInfo()));
    }
    return intval($count);
}

function make_response_query($modx, $query)
{
	$response = array();
	$stmt = $modx->prepare($query);
	
	if ($stmt && $stmt->execute()){
		while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $response[] = $row;
			//$modx->log(modX::LOG_LEVEL_ERROR, "sqlver row ".$row);
		}
	}else{
		$modx->log(modX::LOG_LEVEL_ERROR, "sqlver " . $query . "\n" . implode(', ',$stmt->errorInfo()));
	}
    $stmt->closeCursor();
	return $response;
}

function del_data_query($config, $table_name, $field_name, $field_values)
{
	$table_name_ = $config['table_prefix'].$table_name;
	return "DELETE FROM `".$table_name_."` WHERE `".$field_name."` IN (".$field_values.")";
}

function del_image_file($config, $field)
{
	$image_path = realpath($config["modx_base_path"].$config["images_path"].$field.$config["image_file_extension"]);
	
	if (is_file($image_path)){
		if (@unlink($image_path)) del_img($config, $field);
	}
	return true;
}

function get_table_data($config, $table_name, $fields, $sort_field = "id")
{
	$table_name_ = $config['table_prefix'].$table_name;
	$query = "SELECT ".$fields." FROM `".$table_name_."`";
	if (!empty($sort_field)){
		$query .= " ORDER BY `".$sort_field."` ASC";
	}
	return $query;
}

function get_columns($config, $table_name)
{
	$table_name_ = $config['table_prefix'].$table_name;
	return "SHOW COLUMNS FROM ".$table_name_;
}

function insert_data_query($config, $table_name, $columns, $values)
{
	$table_name_ = $config['table_prefix'].$table_name;
	return "INSERT `".$table_name_."`(".$columns.") VALUES (".$values.")";
}

function count_rows_query($config, $table_name)
{
    $table_name_ = $config['table_prefix'].$table_name;
    return "SELECT COUNT(*) FROM ".$table_name_;
}


$modx = new modX();
$table_prefix = $modx->getOption('table_prefix');

$config = array(
	"modx_base_path" => MODX_BASE_PATH,
    "table_prefix" => $table_prefix
);

$data = json_decode(file_get_contents('php://input', true), true);

if (array_key_exists("check", $data)){
    echo "1";
}
if (array_key_exists("get_columns", $data)){
    $table_name = $data["table_name"];
	$column_name = $data["get_columns"];
	$query = get_columns($config, $table_name);
	$resp =  make_response_query($modx, $query);
	$response = array();
	foreach ($resp as $row){
		$response[] = $row[$column_name];
	}
	$output = json_encode($response);

    echo "". $output;
}
if (array_key_exists("get_catalog", $data)){
	$modx->log(modX::LOG_LEVEL_ERROR, " ".$data["table_name"]);
    $table_name = $data["table_name"];
	$columns_names = $data["get_catalog"];
	$columns = explode(",", $columns_names);
	$query = get_table_data($config, $table_name, $columns_names);
	$resp =  make_response_query($modx, $query);
	$response = array();
	foreach ($resp as $row){
		$response_row = array();
		foreach ($columns as $column){
			$modx->log(modX::LOG_LEVEL_ERROR, "column ".$column." row[$column] ".$row[$column]);
			$response_row[] = $row[$column];
		}
		$response[] = $response_row;
	}
	$output = json_encode($response);

    echo "". $output;
}
if (array_key_exists("delete_data", $data)){
    $table_name = $data["table_name"];
	$ids = $data["delete_data"]["ids"];
	$articles = $data["delete_data"]["articles"];
    $query_ = count_rows_query($config, $table_name);
    $num_rows_before = make_count_query($modx, $query_);

    $query = del_data_query($config, $table_name, "id", $ids);
    $output = make_query($modx, $query);

    $num_rows_after = make_count_query($modx, $query_);
    $del_rows = $num_rows_before - $num_rows_after;

    echo "".$del_rows;
}
if (array_key_exists("insert_data", $data)){
    $table_name = $data["table_name"];
    $columns = $data["insert_data"]["columns"];
    $output = false;
    $query_ = count_rows_query($config, $table_name);
    $num_rows_before = make_count_query($modx, $query_);

    foreach ($data["insert_data"]["rows"] as $row){
        $query = insert_data_query($config, $table_name, $columns, $row);
        $output = make_query($modx, $query);
        if (!$output) break;
    }
    $num_rows_after = make_count_query($modx, $query_);
    $del_rows = $num_rows_after - $num_rows_before;
    echo "".$del_rows;
}