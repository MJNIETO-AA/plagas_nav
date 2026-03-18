CREATE DATABASE IF NOT EXISTS plagas_nav CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE plagas_nav;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    dui VARCHAR(10) NOT NULL UNIQUE,
    telefono VARCHAR(20),
    posicion VARCHAR(60),
    salario DECIMAL(10, 2) DEFAULT 0,
    active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo VARCHAR(120) NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);




CREATE TABLE IF NOT EXISTS inventory_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    unidad VARCHAR(50) DEFAULT 'unidad',
    stock DECIMAL(10, 2) DEFAULT 0,
    min_stock DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    fecha_servicio DATE NOT NULL,
    description VARCHAR(255),
    cantidad_total DECIMAL(10, 2) DEFAULT 0,
    FOREIGN KEY (client_id) REFERENCES clients(id),
);


CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_id INT NOT NULL,
    dia_pago DATE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    method ENUM('cash', 'card', 'transfer') DEFAULT 'cash',
    note VARCHAR(255),
    FOREIGN KEY (service_id) REFERENCES services(id),
);


