CREATE DATABASE IF NOT EXISTS civic_issues_db;
USE civic_issues_db;

CREATE TABLE IF NOT EXISTS issues (
    issue_id INT PRIMARY KEY AUTO_INCREMENT,
    reporter_name VARCHAR(100) NOT NULL,
    location VARCHAR(200) NOT NULL,
    category VARCHAR(60) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL,
    priority_score INT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Open',
    reported_at DATETIME NOT NULL
);