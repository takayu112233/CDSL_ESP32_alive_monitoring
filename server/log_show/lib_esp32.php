<?php
require("libDB.php");

//共通
function start_table(){
    echo "<table>" . "\n";
    echo "<thead>" . "\n";
    echo "<tr>" . "\n";
    echo "<th>ログID</th>" . "\n";
    echo "<th>日時</th>". "\n";
    echo "<th>内容</th>". "\n";
    echo "</tr>". "\n";
    echo "</thead>". "\n";
    echo "<tbody>". "\n";
}

function end_table(){
    echo "</tbody>". "\n";
    echo "</table>". "\n";
}

function log_show(){
    $db = new libDB();
    $pdo = $db->getPDO();
    $sql = $pdo->prepare("select * from log_t ORDER BY log_time DESC limit 50");
    $sql->execute();
    $result = $sql->fetchAll();

    $color_array = array("#f5f5f5", "#fffff0", "#afffaf", "#ffefaf", "#ffafaf", "#ffffaf");

    start_table();
    foreach($result as $loop){
        $color = (int)$loop["log_color"];

        echo "<tr";
        echo " bgcolor=\"$color_array[$color]\"";
        echo ">"."\n";
        echo "<td>" . $loop["log_id"] . "</td><td>" . $loop["log_time"] . "</td><td>" . htmlspecialchars($loop["log_text"]) . "\n";
        echo "<tr>". "\n";
    }
    end_table();
}
?>
