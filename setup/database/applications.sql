SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";
CREATE TABLE `applications` (`id` int(10) UNSIGNED NOT NULL, `name` varchar(128) COLLATE utf8_unicode_ci NOT NULL, `path` varchar(512) COLLATE utf8_unicode_ci NOT NULL, `description` varchar(8192) COLLATE utf8_unicode_ci DEFAULT NULL, `group_identifier` varchar(32) COLLATE utf8_unicode_ci NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
ALTER TABLE `applications` ADD PRIMARY KEY (`id`);
ALTER TABLE `applications` MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;
