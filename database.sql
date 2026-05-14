CREATE DATABASE IF NOT EXISTS ucsp_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ucsp_db;

-- Admins
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL
);

-- Faculty
CREATE TABLE IF NOT EXISTS faculty (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50) DEFAULT 'Assistant Professor',
    dept VARCHAR(100) NOT NULL,
    phone VARCHAR(15) DEFAULT '',
    experience VARCHAR(10) DEFAULT '',
    photo MEDIUMTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Students
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    reg_no VARCHAR(20) UNIQUE NOT NULL,
    dept VARCHAR(100) NOT NULL,
    year VARCHAR(20) DEFAULT '1st Year',
    section VARCHAR(5) DEFAULT 'A',
    email VARCHAR(100) DEFAULT '',
    phone VARCHAR(15) DEFAULT '',
    photo MEDIUMTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bus Routes
CREATE TABLE IF NOT EXISTS bus_routes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    label VARCHAR(100) NOT NULL,
    date_str VARCHAR(50) DEFAULT '',
    inbound MEDIUMTEXT,
    outbound MEDIUMTEXT
);

-- Events
CREATE TABLE IF NOT EXISTS events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    date DATE,
    dept VARCHAR(100) DEFAULT 'All',
    photo MEDIUMTEXT
);

-- Placed Students
CREATE TABLE IF NOT EXISTS placed (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    company VARCHAR(100) NOT NULL,
    package VARCHAR(50) DEFAULT '',
    dept VARCHAR(100) DEFAULT '',
    photo MEDIUMTEXT,
    year VARCHAR(20) DEFAULT ''
);

-- Rank Holders
CREATE TABLE IF NOT EXISTS rank_holders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    rank_no INT DEFAULT 1,
    cgpa VARCHAR(10) DEFAULT '',
    dept VARCHAR(100) DEFAULT '',
    year VARCHAR(20) DEFAULT '',
    photo MEDIUMTEXT
);

-- Updates / Ticker
CREATE TABLE IF NOT EXISTS updates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message TEXT NOT NULL,
    type VARCHAR(20) DEFAULT 'info',
    dept VARCHAR(100) DEFAULT 'All',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- dept column already in CREATE TABLE above

-- Attendance
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    student_name VARCHAR(100),
    dept VARCHAR(100),
    subject VARCHAR(100),
    att_date DATE,
    period INT,
    status VARCHAR(10) DEFAULT 'Present',
    UNIQUE KEY uniq_att (student_id, subject, att_date, period),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Marks
CREATE TABLE IF NOT EXISTS marks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    student_name VARCHAR(100),
    dept VARCHAR(100),
    subject VARCHAR(100),
    exam_type VARCHAR(20),
    mark INT DEFAULT 0,
    max_mark INT DEFAULT 100,
    UNIQUE KEY uniq_mark (student_id, subject, exam_type),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Leaves
CREATE TABLE IF NOT EXISTS leaves (
    id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id INT NOT NULL,
    faculty_name VARCHAR(100),
    faculty_dept VARCHAR(100),
    leave_type VARCHAR(50),
    from_date DATE,
    to_date DATE,
    days INT,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'Pending',
    applied_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE CASCADE
);

-- Notes
CREATE TABLE IF NOT EXISTS notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id INT NOT NULL,
    faculty_name VARCHAR(100),
    dept VARCHAR(100),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    year_group VARCHAR(20) DEFAULT 'All',
    section VARCHAR(5) DEFAULT 'All',
    file_name VARCHAR(200) DEFAULT '',
    file_data LONGTEXT,
    file_mime VARCHAR(100) DEFAULT '',
    posted_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE CASCADE
);

-- Assignments
CREATE TABLE IF NOT EXISTS assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id INT NOT NULL,
    faculty_name VARCHAR(100),
    dept VARCHAR(100),
    title VARCHAR(200) NOT NULL,
    subject VARCHAR(100),
    due_date DATE,
    year_group VARCHAR(20) DEFAULT 'All',
    section VARCHAR(5) DEFAULT 'All',
    description TEXT,
    posted_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE CASCADE
);

-- Submissions
DROP TABLE IF EXISTS submissions;
CREATE TABLE submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    assignment_id INT NOT NULL,
    student_id INT NOT NULL,
    student_name VARCHAR(100),
    file_name VARCHAR(200) DEFAULT '',
    file_data LONGTEXT,
    submitted_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mark INT DEFAULT NULL,
    grade VARCHAR(20),
    feedback TEXT,
    UNIQUE KEY uniq_sub (assignment_id, student_id),
    FOREIGN KEY (assignment_id) REFERENCES assignments(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);



-- Timetable Config
CREATE TABLE IF NOT EXISTS timetable_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dept VARCHAR(100) NOT NULL,
    year_no INT NOT NULL,
    section VARCHAR(5) NOT NULL DEFAULT 'A',
    config_json LONGTEXT NOT NULL,
    UNIQUE KEY uniq_tt (dept, year_no, section)
);

-- Default Data
INSERT IGNORE INTO admins (username, password, name) VALUES
('admin', 'admin123', 'Super Admin'),
('principal', 'prin2026', 'Principal');

INSERT IGNORE INTO faculty (username, password, name, role, dept, phone, experience) VALUES
('ramesh.k', 'faculty123', 'Dr. Ramesh K', 'HOD', 'Computer Science & Engineering', '9876543210', '12'),
('priya.s', 'faculty123', 'Mrs. Priya S', 'Assistant Professor', 'Computer Science & Engineering', '9876543211', '5'),
('babu.k', 'faculty123', 'Mr. Babu K', 'Assistant Professor', 'Computer Science & Engineering', '9876543212', '3');


-- ══════════════════════════════════════════════
-- Safe ALTER: add missing columns if not exist
-- (handles re-import on existing DB)
-- ══════════════════════════════════════════════

INSERT IGNORE INTO students (username, password, name, reg_no, dept, year, section, email, phone) VALUES
('cs001', 'student123', 'Arun Kumar', 'CS001', 'Computer Science & Engineering', '2nd Year', 'A', 'arun@cs.edu', '9876500001'),
('cs002', 'student123', 'Priya Dharshini', 'CS002', 'Computer Science & Engineering', '2nd Year', 'A', 'priya@cs.edu', '9876500002'),
('cs003', 'student123', 'Karthick R', 'CS003', 'Computer Science & Engineering', '3rd Year', 'B', 'karthick@cs.edu', '9876500003');

INSERT IGNORE INTO updates (message, type) VALUES
('Welcome to UCSP College Management System!', 'info'),
('Semester exams scheduled from April 15th', 'warning');

-- Student Leaves
CREATE TABLE IF NOT EXISTS student_leaves (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    student_name VARCHAR(100),
    student_reg VARCHAR(50),
    student_dept VARCHAR(100),
    student_year VARCHAR(20),
    student_section VARCHAR(5),
    leave_type VARCHAR(50),
    from_date DATE,
    to_date DATE,
    days INT DEFAULT 1,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'Pending',
    applied_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- Exam Schedule
CREATE TABLE IF NOT EXISTS exam_schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject VARCHAR(100) NOT NULL,
    exam_date DATE NOT NULL,
    start_time VARCHAR(20),
    end_time VARCHAR(20),
    hall VARCHAR(50),
    total_marks INT DEFAULT 100,
    dept VARCHAR(100),
    year_str VARCHAR(20),
    section VARCHAR(5) DEFAULT 'All',
    posted_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    message TEXT,
    type VARCHAR(30) DEFAULT 'info',
    dept VARCHAR(100) DEFAULT 'All',
    year_str VARCHAR(20) DEFAULT 'All',
    posted_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- File Submissions (assignment uploads)


CREATE TABLE IF NOT EXISTS exam_timetables (
    id INT AUTO_INCREMENT PRIMARY KEY,
    label VARCHAR(200) NOT NULL,
    sem_name VARCHAR(100) DEFAULT '',
    semester VARCHAR(20) DEFAULT '',
    year VARCHAR(20) DEFAULT '',
    dept VARCHAR(100) DEFAULT '',
    image LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Fix image column size
ALTER TABLE exam_timetables MODIFY COLUMN image LONGTEXT;

-- Add columns to exam_timetables if not exist

-- ═══════════════════════════════════════════════════════════════
-- DEMO DATA (safe to re-run - uses INSERT IGNORE)
-- ═══════════════════════════════════════════════════════════════

-- Admin
INSERT IGNORE INTO admins (username, password, name) VALUES
('admin', 'admin123', 'Administrator');

-- Faculty (10 across departments)
INSERT IGNORE INTO faculty (name, username, password, role, dept, phone, experience) VALUES
('Dr. Ramesh Kumar',    'ramesh.k',   'faculty123', 'HOD',        'MCA',                          '9876543210', '12 years'),
('Mrs. Priya Sharma',   'priya.s',    'faculty123', 'Professor',  'MCA',                          '9876543211', '8 years'),
('Mr. Arjun Nair',      'arjun.n',    'faculty123', 'Asst. Prof', 'MCA',                          '9876543212', '4 years'),
('Dr. Kavitha Rajan',   'kavitha.r',  'faculty123', 'HOD',        'Computer Science & Engineering','9876543213', '15 years'),
('Mr. Suresh Babu',     'suresh.b',   'faculty123', 'Professor',  'Computer Science & Engineering','9876543214', '10 years'),
('Mrs. Deepa Menon',    'deepa.m',    'faculty123', 'Asst. Prof', 'Information Technology',       '9876543215', '5 years'),
('Dr. Venkat Rao',      'venkat.r',   'faculty123', 'HOD',        'Information Technology',       '9876543216', '14 years'),
('Mr. Karthik S',       'karthik.s',  'faculty123', 'Asst. Prof', 'MBA',                          '9876543217', '3 years'),
('Dr. Latha Devi',      'latha.d',    'faculty123', 'HOD',        'MBA',                          '9876543218', '11 years'),
('Mr. Prasad M',        'prasad.m',   'faculty123', 'Professor',  'Electronics & Communication',  '9876543219', '9 years');

-- Students (10 MCA students)
INSERT IGNORE INTO students (name, username, password, reg_no, dept, year, section) VALUES
('Arun Kumar',      'cs001', 'student123', '22MCA001', 'MCA', '1st Year', 'A'),
('Bhavana R',       'cs002', 'student123', '22MCA002', 'MCA', '1st Year', 'A'),
('Chandru S',       'cs003', 'student123', '22MCA003', 'MCA', '1st Year', 'A'),
('Divya T',         'cs004', 'student123', '22MCA004', 'MCA', '1st Year', 'B'),
('Elavarasan K',    'cs005', 'student123', '22MCA005', 'MCA', '1st Year', 'B'),
('Fathima N',       'cs006', 'student123', '22MCA006', 'MCA', '2nd Year', 'A'),
('Gopal V',         'cs007', 'student123', '22MCA007', 'MCA', '2nd Year', 'A'),
('Harini P',        'cs008', 'student123', '22MCA008', 'MCA', '2nd Year', 'B'),
('Indra J',         'cs009', 'student123', '22MCA009', 'MCA', '2nd Year', 'B'),
('Jayanthi L',      'cs010', 'student123', '22MCA010', 'MCA', '3rd Year', 'A');

-- Bus Routes (10 routes)
INSERT IGNORE INTO bus_routes (label, inbound, outbound) VALUES
('Route 1 — Tambaram',      '7:30 AM', '5:00 PM'),
('Route 2 — Chrompet',      '7:45 AM', '5:15 PM'),
('Route 3 — Velachery',     '7:20 AM', '5:30 PM'),
('Route 4 — Medavakkam',    '7:35 AM', '5:10 PM'),
('Route 5 — Perungudi',     '7:50 AM', '5:20 PM'),
('Route 6 — OMR',           '8:00 AM', '5:00 PM'),
('Route 7 — Sholinganallur','7:25 AM', '5:45 PM'),
('Route 8 — Pallavaram',    '7:40 AM', '5:05 PM'),
('Route 9 — Nanganallur',   '7:55 AM', '5:25 PM'),
('Route 10 — Guindy',       '8:05 AM', '5:35 PM');

-- Events (10 events)
INSERT IGNORE INTO events (name, date, dept) VALUES
('Sports Day 2026',              '2026-03-20', 'All Departments'),
('AI & ML Seminar',              '2026-04-05', 'MCA'),
('National Science Day',         '2026-02-28', 'All Departments'),
('Hackathon 2026',               '2026-04-15', 'Computer Science & Engineering'),
('Cultural Fest — Utsav',        '2026-03-10', 'All Departments'),
('Industry Expert Talk',         '2026-04-22', 'MCA'),
('Alumni Meet 2026',             '2026-05-01', 'All Departments'),
('Project Expo',                 '2026-04-30', 'Information Technology'),
('Workshop on Cloud Computing',  '2026-04-10', 'MCA'),
('Placement Drive — TCS',        '2026-04-18', 'All Departments');

-- Placed Students (10)
INSERT IGNORE INTO placed (name, company, package, dept, year) VALUES
('Arun Kumar',      'TCS',          '4.5 LPA', 'MCA',                          '2025'),
('Bhavana R',       'Infosys',      '3.6 LPA', 'MCA',                          '2025'),
('Chandru S',       'Wipro',        '3.8 LPA', 'Computer Science & Engineering','2025'),
('Divya T',         'HCL',          '4.0 LPA', 'MCA',                          '2025'),
('Elavarasan K',    'Cognizant',    '4.2 LPA', 'Information Technology',       '2025'),
('Fathima N',       'Accenture',    '5.0 LPA', 'MCA',                          '2025'),
('Gopal V',         'Zoho',         '6.0 LPA', 'Computer Science & Engineering','2025'),
('Harini P',        'Amazon',       '7.5 LPA', 'MCA',                          '2025'),
('Indra J',         'Capgemini',    '4.8 LPA', 'Information Technology',       '2025'),
('Jayanthi L',      'Tech Mahindra','3.5 LPA', 'MBA',                          '2025');

-- Rank Holders (10)
INSERT IGNORE INTO rank_holders (name, rank_no, cgpa, dept, year) VALUES
('Harini P',        1, 9.8, 'MCA',                          '2025'),
('Gopal V',         2, 9.5, 'Computer Science & Engineering','2025'),
('Fathima N',       3, 9.3, 'MCA',                          '2025'),
('Divya T',         4, 9.1, 'MCA',                          '2025'),
('Arun Kumar',      5, 9.0, 'MCA',                          '2025'),
('Elavarasan K',    6, 8.9, 'Information Technology',       '2025'),
('Indra J',         7, 8.8, 'Information Technology',       '2025'),
('Bhavana R',       8, 8.7, 'MCA',                          '2025'),
('Chandru S',       9, 8.6, 'Computer Science & Engineering','2025'),
('Jayanthi L',      10,8.5, 'MBA',                          '2025');

-- Updates/Ticker (10)
INSERT IGNORE INTO updates (message, type) VALUES
('🎉 Sports Day on March 20, 2026 — All students participate!',          'info'),
('📋 Internal Exam Unit 3 starts April 1, 2026',                         'exam'),
('🏆 Rank Holders 2025 announced — Congratulations!',                    'success'),
('🚌 Bus Route 2 timing updated — Evening pickup at 5:15 PM',            'info'),
('💼 TCS Placement Drive on April 18 — Register Now',                    'placement'),
('📚 Workshop on Cloud Computing — April 10, MCA Dept',                  'event'),
('🎊 Hackathon 2026 registrations open — CSE Dept',                     'event'),
('📢 Library books return deadline: March 31, 2026',                     'notice'),
('🔬 AI & ML Seminar — April 5, MCA Hall',                              'event'),
('🎓 Alumni Meet 2026 — May 1, College Auditorium',                      'info');

-- Attendance for MCA students (10 records)
INSERT IGNORE INTO attendance (student_id, student_name, dept, subject, att_date, period, status) VALUES
(1, 'Arun Kumar',   'MCA', 'Data Structures', '2026-03-18', 1, 'Present'),
(2, 'Bhavana R',    'MCA', 'Data Structures', '2026-03-18', 1, 'Present'),
(3, 'Chandru S',    'MCA', 'Data Structures', '2026-03-18', 1, 'Absent'),
(4, 'Divya T',      'MCA', 'Data Structures', '2026-03-18', 1, 'Present'),
(5, 'Elavarasan K', 'MCA', 'Data Structures', '2026-03-18', 1, 'Present'),
(6, 'Fathima N',    'MCA', 'DBMS',            '2026-03-18', 2, 'Present'),
(7, 'Gopal V',      'MCA', 'DBMS',            '2026-03-18', 2, 'Present'),
(8, 'Harini P',     'MCA', 'DBMS',            '2026-03-18', 2, 'Absent'),
(9, 'Indra J',      'MCA', 'DBMS',            '2026-03-18', 2, 'Present'),
(10,'Jayanthi L',   'MCA', 'DBMS',            '2026-03-18', 2, 'Present');

-- Leaves for faculty (10 records)
INSERT IGNORE INTO leaves (faculty_id, faculty_name, faculty_dept, leave_type, from_date, to_date, days, reason, status) VALUES
(1, 'Dr. Ramesh Kumar',  'MCA', 'Medical',  '2026-03-10', '2026-03-11', 2, 'Fever and rest',          'Approved'),
(2, 'Mrs. Priya Sharma', 'MCA', 'Personal', '2026-03-15', '2026-03-15', 1, 'Family function',         'Approved'),
(3, 'Mr. Arjun Nair',    'MCA', 'Medical',  '2026-03-20', '2026-03-21', 2, 'Doctor appointment',      'Pending'),
(4, 'Dr. Kavitha Rajan', 'CSE', 'Official', '2026-03-25', '2026-03-26', 2, 'Conference attendance',   'Approved'),
(5, 'Mr. Suresh Babu',   'CSE', 'Personal', '2026-04-01', '2026-04-01', 1, 'Personal work',           'Pending'),
(6, 'Mrs. Deepa Menon',  'IT',  'Medical',  '2026-03-18', '2026-03-19', 2, 'Surgery follow-up',       'Approved'),
(7, 'Dr. Venkat Rao',    'IT',  'Official', '2026-04-05', '2026-04-06', 2, 'FDP Programme',           'Pending'),
(8, 'Mr. Karthik S',     'MBA', 'Personal', '2026-03-22', '2026-03-22', 1, 'Marriage function',       'Rejected'),
(9, 'Dr. Latha Devi',    'MBA', 'Medical',  '2026-04-08', '2026-04-09', 2, 'Health checkup',          'Pending'),
(10,'Mr. Prasad M',      'ECE', 'Official', '2026-04-12', '2026-04-13', 2, 'Workshop at Anna Univ',   'Approved');

-- Circulars table
CREATE TABLE IF NOT EXISTS circulars (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    dept VARCHAR(100) DEFAULT 'All',
    file_name VARCHAR(200),
    file_data LONGTEXT,
    posted_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
