DROP PROCEDURE IF EXISTS creare_rezervare_completa;
-- PROC_END

CREATE PROCEDURE creare_rezervare_completa(
        IN p_id_client INT,
        IN p_id_masa INT,
        IN p_data_ora DATETIME,
        IN p_nr_persoane INT,
        IN p_meniuri_json JSON
)
BEGIN
    DECLARE v_id_rezervare INT;
    DECLARE v_i INT DEFAULT 0;
    DECLARE v_len INT DEFAULT 0;
    DECLARE v_cod_meniu VARCHAR(50);
    DECLARE v_cantitate INT;
    DECLARE v_id_meniu INT;

    INSERT INTO rezervari (id_client, id_masa, data_ora_rezervare, numar_persoane)
    VALUES(p_id_client, p_id_masa, p_data_ora,p_nr_persoane);

    SET v_id_rezervare = LAST_INSERT_ID();

    SET v_len = JSON_LENGTH(p_meniuri_json);

    WHILE v_i < v_len DO
        SET v_cod_meniu = JSON_UNQUOTE(JSON_EXTRACT(p_meniuri_json,CONCAT('$[', v_i, '].cod')));
        SET v_cantitate = JSON_EXTRACT(p_meniuri_json,CONCAT('$[', v_i, '].cantitate'));

        SELECT id_meniu INTO v_id_meniu FROM meniuri WHERE cod_meniu = v_cod_meniu LIMIT 1;

        INSERT INTO rezervari_meniuri (id_rezervare, id_meniu, cantitate)
        VALUES (v_id_rezervare, v_id_meniu, v_cantitate);

        SET v_i = v_i + 1;
    END WHILE;

    SELECT v_id_rezervare AS id_rezervare;
END
-- PROC_END
