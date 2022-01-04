<?php
require("lib_esp32.php");
?>

<html>
    <head>
        <link href="css/main.css" rel="stylesheet" media="screen">
    </head>
    <body>
        <div id="side">
            <h2>ESP32</h2>
            <p>監視サーバログ</p>
            <ul id="manu">
                <li class="now"><a>ログ</a></li>
            </ul>
            <div id="footer" class="footer">Takahashi Yunosuke</div>  
        </div>

        <div id="contents">
            <?php log_show(); ?>
        </div>

        <script type="text/javascript" src="js/main.js"></script>
    </body>
</html>