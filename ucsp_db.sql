-- ============================================================
--  UCSP DATABASE SCHEMA
--  Run this in MySQL: mysql -u root -p < ucsp_db.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS ucsp_db DEFAULT CHARACTER SET utf8mb4;
USE ucsp_db;

-- ── ADMINS ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS admins (
    id       INT AUTO_INCREMENT PRIMARY KEY,
    name     VARCHAR(100) NOT NULL,
    username VARCHAR(50)  NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default admin account
INSERT INTO admins (name, username, password) VALUES
('Super Admin', 'admin', 'admin123'),
('Principal',   'principal', 'prin@2026')
ON DUPLICATE KEY UPDATE id=id;

-- ── FACULTY ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS faculty (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    phone      VARCHAR(15),
    experience VARCHAR(20),
    role       VARCHAR(50)  NOT NULL,
    department VARCHAR(100) NOT NULL,
    username   VARCHAR(50)  NOT NULL UNIQUE,
    password   VARCHAR(100) NOT NULL,
    image      VARCHAR(255) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── STUDENTS ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS students (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    reg_no     VARCHAR(20)  NOT NULL UNIQUE,
    department VARCHAR(100) NOT NULL,
    year       VARCHAR(20),
    username   VARCHAR(50)  NOT NULL UNIQUE,
    password   VARCHAR(100) NOT NULL,
    phone      VARCHAR(15),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample student
INSERT INTO students (name, reg_no, department, year, username, password, phone) VALUES
('Priya S',    '22CS001', 'Computer Science & Engineering', '2nd Year', '22CS001', 'student123', '9876501234'),
('Karthik R',  '22CS002', 'Computer Science & Engineering', '2nd Year', '22CS002', 'student123', '9876502345'),
('Meera T',    '22IT001', 'Information Technology',         '2nd Year', '22IT001', 'student123', '9876503456'),
('Rajan M',    '22EC001', 'Electronics & Communication',    '2nd Year', '22EC001', 'student123', '9876504567')
ON DUPLICATE KEY UPDATE id=id;

-- ── BUS ROUTES ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bus_routes (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    label   VARCHAR(100) DEFAULT 'Bus Route',
    img_in  VARCHAR(255) DEFAULT '',
    img_out VARCHAR(255) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── EVENTS ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS events (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(150) NOT NULL,
    event_date DATE         NOT NULL,
    dept       VARCHAR(100) DEFAULT 'All Departments',
    photo      VARCHAR(255) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── PLACED STUDENTS ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS placed_students (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    name    VARCHAR(100) NOT NULL,
    company VARCHAR(100) NOT NULL,
    dept    VARCHAR(100) NOT NULL,
    ctc     VARCHAR(50),
    photo   VARCHAR(255) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── RANK HOLDERS ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS rank_holders (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    name    VARCHAR(100) NOT NULL,
    rank_no INT          NOT NULL,
    cgpa    DECIMAL(4,2) NOT NULL,
    dept    VARCHAR(100) NOT NULL,
    year    VARCHAR(20),
    photo   VARCHAR(255) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
