CREATE TABLE IF NOT EXISTS users (
    id_user INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS clienti (
    id_client INT AUTO_INCREMENT PRIMARY KEY,
    nume_client VARCHAR(100) NOT NULL,
    nr_tlf VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS mese (
    id_masa INT AUTO_INCREMENT PRIMARY KEY,
    cod_masa VARCHAR(16) NOT NULL UNIQUE,
    status VARCHAR(50) NOT NULL DEFAULT 'Libera'
);

CREATE TABLE IF NOT EXISTS rezervari (
    id_rezervare INT AUTO_INCREMENT PRIMARY KEY,
    id_client INT NOT NULL,
    id_masa INT NOT NULL,
    data_ora_rezervare DATETIME NOT NULL,
    numar_persoane INT NOT NULL,
    status VARCHAR(50) DEFAULT 'In asteptare',
    data_creare TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(id_client) REFERENCES clienti(id_client) ON DELETE CASCADE,
    FOREIGN KEY(id_masa) REFERENCES mese(id_masa) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_user INT NOT NULL,
    action VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_user) REFERENCES users(id_user) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS meniuri (
    id_meniu INT AUTO_INCREMENT PRIMARY KEY,
    cod_meniu VARCHAR(50) NOT NULL UNIQUE, -- Folosit pentru identificare în JSON
    nume_meniu VARCHAR(100) NOT NULL,
    pret DECIMAL(10, 2) NOT NULL
);


CREATE TABLE IF NOT EXISTS rezervari_meniuri (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_rezervare INT NOT NULL,
    id_meniu INT NOT NULL,
    cantitate INT NOT NULL DEFAULT 1,
    FOREIGN KEY (id_rezervare) REFERENCES rezervari(id_rezervare) ON DELETE CASCADE,
    FOREIGN KEY (id_meniu) REFERENCES meniuri(id_meniu) ON DELETE CASCADE
);