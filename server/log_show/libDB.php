<?php

class libDB{
    //private PDO $pdo;
    private $pdo;
    /**
     * コンストラクタ
     */
    public function __construct()
    {
        $this->pdo = new PDO("mysql:host=localhost;dbname=iot;charset=utf8","user","asdf1234", 
        [PDO::ATTR_ERRMODE => PDO::ERRMODE_WARNING]);

    }

    public function getPDO(){
        return $this->pdo;
    }

}
?>