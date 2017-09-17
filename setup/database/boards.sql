SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";
CREATE TABLE `boards` (`id` int(10) UNSIGNED NOT NULL, `display_name` varchar(128) COLLATE utf8_unicode_ci NOT NULL, `internal_name` varchar(128) COLLATE utf8_unicode_ci NOT NULL, `flash_program` varchar(16) COLLATE utf8_unicode_ci NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
ALTER TABLE `boards` ADD PRIMARY KEY (`id`);
ALTER TABLE `boards` MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;
