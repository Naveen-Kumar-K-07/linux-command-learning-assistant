-- ===================================================================
-- Linux Commands Learning Assistant — Database Schema (MySQL Compatible)
-- ===================================================================

CREATE DATABASE IF NOT EXISTS `linux_learning_assistant` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `linux_learning_assistant`;

-- Table 1: Users
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `full_name` VARCHAR(150) NOT NULL,
    `email` VARCHAR(255) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `is_verified` BOOLEAN NOT NULL DEFAULT FALSE,
    `verification_token` VARCHAR(128) NULL,
    `verification_code` VARCHAR(10) NULL,
    `reset_token` VARCHAR(128) NULL,
    `reset_token_expiry` DATETIME NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `last_login` DATETIME NULL,
    INDEX `idx_user_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 2: Lessons
CREATE TABLE IF NOT EXISTS `lessons` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `lesson_slug` VARCHAR(100) NOT NULL UNIQUE,
    `title` VARCHAR(200) NOT NULL,
    `category` VARCHAR(100) NOT NULL,
    `difficulty_level` VARCHAR(50) NOT NULL,
    `command_name` VARCHAR(100) NOT NULL,
    `purpose` TEXT NOT NULL,
    `syntax` TEXT NOT NULL,
    `explanation` TEXT NOT NULL,
    `practical_examples` TEXT NOT NULL,
    `expected_output` TEXT NOT NULL,
    `step_by_step` TEXT NOT NULL,
    `common_mistakes` TEXT NOT NULL,
    `practice_task` TEXT NOT NULL,
    `practice_expected_command` VARCHAR(255) NOT NULL,
    `lesson_order` INT NOT NULL DEFAULT 1,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_lesson_order` (`lesson_order`),
    INDEX `idx_lesson_category` (`category`),
    INDEX `idx_lesson_difficulty` (`difficulty_level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 3: User Progress per Lesson
CREATE TABLE IF NOT EXISTS `user_progress` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `lesson_id` INT NOT NULL,
    `is_completed` BOOLEAN NOT NULL DEFAULT FALSE,
    `practice_completed` BOOLEAN NOT NULL DEFAULT FALSE,
    `last_position` VARCHAR(100) NOT NULL DEFAULT 'overview',
    `completed_at` DATETIME NULL,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY `unique_user_lesson` (`user_id`, `lesson_id`),
    CONSTRAINT `fk_progress_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_progress_lesson` FOREIGN KEY (`lesson_id`) REFERENCES `lessons` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 4: User Global Learning State (for resuming)
CREATE TABLE IF NOT EXISTS `user_learning_state` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL UNIQUE,
    `current_level` VARCHAR(50) NOT NULL DEFAULT 'Beginner',
    `current_category` VARCHAR(100) NOT NULL DEFAULT 'Basic Navigation',
    `current_lesson_id` INT NULL,
    `total_lessons_completed` INT NOT NULL DEFAULT 0,
    `completion_percentage` FLOAT NOT NULL DEFAULT 0.0,
    `last_activity` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_state_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_state_lesson` FOREIGN KEY (`current_lesson_id`) REFERENCES `lessons` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 5: Terminal Virtual State (Filesystem persistence per user)
CREATE TABLE IF NOT EXISTS `terminal_states` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL UNIQUE,
    `cwd` VARCHAR(255) NOT NULL DEFAULT '/home/user',
    `filesystem_json` MEDIUMTEXT NOT NULL,
    `command_history_json` TEXT NULL,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_terminal_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 6: Assessment Quizzes
CREATE TABLE IF NOT EXISTS `assessment_quizzes` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `slug` VARCHAR(100) NOT NULL UNIQUE,
    `title` VARCHAR(200) NOT NULL,
    `description` TEXT NOT NULL,
    `difficulty_level` VARCHAR(50) NOT NULL,
    `passing_score` INT NOT NULL DEFAULT 70,
    `time_limit_minutes` INT NOT NULL DEFAULT 15,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 7: Assessment Questions
CREATE TABLE IF NOT EXISTS `assessment_questions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `quiz_id` INT NOT NULL,
    `question_text` TEXT NOT NULL,
    `question_type` VARCHAR(50) NOT NULL DEFAULT 'mcq',
    `option_a` TEXT NOT NULL,
    `option_b` TEXT NOT NULL,
    `option_c` TEXT NOT NULL,
    `option_d` TEXT NOT NULL,
    `correct_option` VARCHAR(5) NOT NULL,
    `explanation` TEXT NOT NULL,
    `order_num` INT NOT NULL DEFAULT 1,
    CONSTRAINT `fk_question_quiz` FOREIGN KEY (`quiz_id`) REFERENCES `assessment_quizzes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 8: Assessment Attempts
CREATE TABLE IF NOT EXISTS `assessment_attempts` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `quiz_id` INT NOT NULL,
    `score` INT NOT NULL,
    `total_questions` INT NOT NULL,
    `percentage` FLOAT NOT NULL,
    `passed` BOOLEAN NOT NULL DEFAULT FALSE,
    `answers_json` TEXT NULL,
    `attempted_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_attempt_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_attempt_quiz` FOREIGN KEY (`quiz_id`) REFERENCES `assessment_quizzes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table 9: Certificates
CREATE TABLE IF NOT EXISTS `certificates` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `certificate_id` VARCHAR(100) NOT NULL UNIQUE,
    `user_id` INT NOT NULL,
    `course_name` VARCHAR(255) NOT NULL DEFAULT 'Linux Commands Learning Assistant — Professional Mastery',
    `issue_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `verification_hash` VARCHAR(255) NOT NULL,
    `criteria_summary_json` TEXT NOT NULL,
    `download_count` INT NOT NULL DEFAULT 0,
    INDEX `idx_cert_id` (`certificate_id`),
    CONSTRAINT `fk_cert_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
