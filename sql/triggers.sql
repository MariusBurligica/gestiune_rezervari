DROP TRIGGER IF EXISTS trg_rezervari_before_insert;
--TRIGGER_END

CREATE TRIGGER trg_rezervari_before_insert
BEFORE INSERT ON rezervari
FOR EACH ROW
BEGIN
    IF NEW.data_ora_rezervare < CURRENT_TIME THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Data este invalida!';
        END IF;
    END;
--TRIGGER_END

DROP TRIGGER IF EXISTS trg_actualizeaza_masa_after;
--TRIGGER_END

CREATE TRIGGER trg_actualizeaza_masa_after
AFTER INSERT ON rezervari
FOR EACH ROW
BEGIN
    IF NEW.status = 'Confirmata' THEN
        UPDATE mese
        SET status = 'Rezervata'
        WHERE id_masa = NEW.id_masa;
    END IF;
END;
--TRIGGER_END
DROP TRIGGER IF EXISTS ev_elibereaza_mese_expirate;
--TRIGGER_END
CREATE EVENT IF NOT EXISTS ev_elibereaza_mese_expirate
ON SCHEDULE EVERY 10 MINUTE
DO
  BEGIN
    UPDATE mese m
    JOIN rezervari r ON m.id_masa = r.id_masa
    SET m.status = 'Libera'
    WHERE r.status = 'Confirmata'
      AND ADDTIME(r.data_ora_rezervare, '02:00:00') <= CURRENT_TIMESTAMP;
  END;
--TRIGGER_END