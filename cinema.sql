-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 01, 2026 at 06:26 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `cinema`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `admin_id` int(30) NOT NULL,
  `admin_name` varchar(100) NOT NULL,
  `password` varchar(50) NOT NULL,
  `role` varchar(20) NOT NULL,
  `status` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`admin_id`, `admin_name`, `password`, `role`, `status`) VALUES
(3, 'admin1', 'admin1_aacinema', 'Admin', 'Active'),
(4, 'admin2', 'admin2_aacinema', 'Admin', 'Active');

-- --------------------------------------------------------

--
-- Table structure for table `bookings`
--

CREATE TABLE `bookings` (
  `booking_id` int(11) NOT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `show_id` int(11) DEFAULT NULL,
  `seat_id` int(11) DEFAULT NULL,
  `booking_date` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `bookings`
--

INSERT INTO `bookings` (`booking_id`, `customer_id`, `show_id`, `seat_id`, `booking_date`) VALUES
(142, 151, 1, 7, '2026-07-31 11:02:43'),
(143, 151, 1, 8, '2026-07-31 11:02:43'),
(144, 152, 1, 12, '2026-07-31 11:09:25'),
(145, 152, 1, 13, '2026-07-31 11:09:25'),
(146, 153, 2, 22, '2026-07-31 11:30:27'),
(147, 153, 2, 23, '2026-07-31 11:30:27'),
(148, 154, 1, 2, '2026-07-31 11:41:47'),
(149, 154, 1, 3, '2026-07-31 11:41:47');

-- --------------------------------------------------------

--
-- Table structure for table `customers`
--

CREATE TABLE `customers` (
  `customer_id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `customers`
--

INSERT INTO `customers` (`customer_id`, `name`, `email`, `phone`) VALUES
(151, 'kavya sathsarani', 'ksd@gmail.com', '0123654789'),
(152, 'kavindu sathsara', 'dsk@gmail.com', '0456321789'),
(153, 'nilupa chandani', 'ncw@gmail.com', '025413687'),
(154, 'chanaka dissanayaka', 'cd@gmail.com', '0741258963');

-- --------------------------------------------------------

--
-- Table structure for table `movies`
--

CREATE TABLE `movies` (
  `movie_id` int(11) NOT NULL,
  `title` varchar(100) DEFAULT NULL,
  `genre` varchar(50) DEFAULT NULL,
  `duration` varchar(100) DEFAULT NULL,
  `language` varchar(30) DEFAULT NULL,
  `release_date` date DEFAULT NULL,
  `poster` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `movies`
--

INSERT INTO `movies` (`movie_id`, `title`, `genre`, `duration`, `language`, `release_date`, `poster`) VALUES
(1, 'Avatar: The Way of Water', 'Sci-Fi', '3h 12min', 'English', '2026-07-16', 'avatar2.JPEG'),
(2, 'Spider-Man: No Way Home', 'Action', '2h 28min', 'English', '2026-07-17', 'spiderman.JPEG'),
(3, 'Inside Out 2', 'Animation', '1h 36min', 'English', '2026-07-14', 'insideout2.JPEG'),
(4, 'Mission Impossible - Dead Reckoning', 'Action', '2h 43min', 'English', '2026-07-12', 'mission_impossible.JPEG'),
(5, 'Kung Fu Panda 4', 'Animation', '1h 34min', 'English', '2026-07-08', 'kungfupanda4.JPEG'),
(6, 'The Lion King', 'Adventure', '1h 58min', 'English', '2026-07-19', 'lionking.JPEG');

-- --------------------------------------------------------

--
-- Table structure for table `payments`
--

CREATE TABLE `payments` (
  `payment_id` int(11) NOT NULL,
  `booking_id` int(11) DEFAULT NULL,
  `customer_id` int(11) NOT NULL,
  `amount` decimal(8,2) DEFAULT NULL,
  `payment_date` date NOT NULL,
  `payment_method` varchar(30) DEFAULT NULL,
  `payment_status` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `payments`
--

INSERT INTO `payments` (`payment_id`, `booking_id`, `customer_id`, `amount`, `payment_date`, `payment_method`, `payment_status`) VALUES
(32, 143, 151, 1600.00, '0000-00-00', 'Credit / Debit Card', 'Completed'),
(33, 145, 152, 1800.00, '0000-00-00', 'Credit / Debit Card', 'Completed'),
(34, 149, 154, 1600.00, '2026-07-31', 'Credit / Debit Card', 'Completed');

-- --------------------------------------------------------

--
-- Table structure for table `seats`
--

CREATE TABLE `seats` (
  `seat_id` int(11) NOT NULL,
  `theater_id` int(11) DEFAULT NULL,
  `seat_number` varchar(10) DEFAULT NULL,
  `seat_type` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `seats`
--

INSERT INTO `seats` (`seat_id`, `theater_id`, `seat_number`, `seat_type`) VALUES
(1, 101, 'A1', 'ODC'),
(2, 101, 'A2', 'ODC'),
(3, 101, 'A3', 'ODC'),
(4, 101, 'A4', 'ODC'),
(5, 101, 'A5', 'ODC'),
(6, 101, 'A6', 'ODC'),
(7, 101, 'A7', 'ODC'),
(8, 101, 'A8', 'ODC'),
(9, 101, 'A9', 'ODC'),
(10, 101, 'A10', 'ODC'),
(11, 101, 'A11', 'BALCONY'),
(12, 101, 'A12', 'BALCONY'),
(13, 101, 'A13', 'BALCONY'),
(14, 101, 'A14', 'BALCONY'),
(15, 101, 'A15', 'BALCONY'),
(16, 101, 'A16', 'BALCONY'),
(17, 101, 'A17', 'BALCONY'),
(18, 101, 'A18', 'BALCONY'),
(19, 101, 'A19', 'BALCONY'),
(20, 101, 'A20', 'BALCONY'),
(21, 102, 'B1', 'ODC'),
(22, 102, 'B2', 'ODC'),
(23, 102, 'B3', 'ODC'),
(24, 102, 'B4', 'ODC'),
(25, 102, 'B5', 'ODC'),
(26, 102, 'B6', 'ODC'),
(27, 102, 'B7', 'ODC'),
(28, 102, 'B8', 'ODC'),
(29, 102, 'B9', 'ODC'),
(30, 102, 'B10', 'ODC'),
(31, 102, 'B11', 'BALCONY'),
(32, 102, 'B12', 'BALCONY'),
(33, 102, 'B13', 'BALCONY'),
(34, 102, 'B14', 'BALCONY'),
(35, 102, 'B15', 'BALCONY'),
(36, 102, 'B16', 'BALCONY'),
(37, 102, 'B17', 'BALCONY'),
(38, 102, 'B18', 'BALCONY'),
(39, 102, 'B19', 'BALCONY'),
(40, 102, 'B20', 'BALCONY'),
(41, 103, 'C1', 'ODC'),
(42, 103, 'C2', 'ODC'),
(43, 103, 'C3', 'ODC'),
(44, 103, 'C4', 'ODC'),
(45, 103, 'C5', 'ODC'),
(46, 103, 'C6', 'ODC'),
(47, 103, 'C7', 'ODC'),
(48, 103, 'C8', 'ODC'),
(49, 103, 'C9', 'ODC'),
(50, 103, 'C10', 'ODC'),
(51, 103, 'C11', 'BALCONY'),
(52, 103, 'C12', 'BALCONY'),
(53, 103, 'C13', 'BALCONY'),
(54, 103, 'C14', 'BALCONY'),
(55, 103, 'C15', 'BALCONY'),
(56, 103, 'C16', 'BALCONY'),
(57, 103, 'C17', 'BALCONY'),
(58, 103, 'C18', 'BALCONY'),
(59, 103, 'C19', 'BALCONY'),
(60, 103, 'C20', 'BALCONY'),
(61, 104, 'D1', 'ODC'),
(62, 104, 'D2', 'ODC'),
(63, 104, 'D3', 'ODC'),
(64, 104, 'D4', 'ODC'),
(65, 104, 'D5', 'ODC'),
(66, 104, 'D6', 'ODC'),
(67, 104, 'D7', 'ODC'),
(68, 104, 'D8', 'ODC'),
(69, 104, 'D9', 'ODC'),
(70, 104, 'D10', 'ODC'),
(71, 104, 'D11', 'BALCONY'),
(72, 104, 'D12', 'BALCONY'),
(73, 104, 'D13', 'BALCONY'),
(74, 104, 'D14', 'BALCONY'),
(75, 104, 'D15', 'BALCONY'),
(76, 104, 'D16', 'BALCONY'),
(77, 104, 'D17', 'BALCONY'),
(78, 104, 'D18', 'BALCONY'),
(79, 104, 'D19', 'BALCONY'),
(80, 104, 'D20', 'BALCONY'),
(81, 105, 'E1', 'ODC'),
(82, 105, 'E2', 'ODC'),
(83, 105, 'E3', 'ODC'),
(84, 105, 'E4', 'ODC'),
(85, 105, 'E5', 'ODC'),
(86, 105, 'E6', 'ODC'),
(87, 105, 'E7', 'ODC'),
(88, 105, 'E8', 'ODC'),
(89, 105, 'E9', 'ODC'),
(90, 105, 'E10', 'ODC'),
(91, 105, 'E11', 'BALCONY'),
(92, 105, 'E12', 'BALCONY'),
(93, 105, 'E13', 'BALCONY'),
(94, 105, 'E14', 'BALCONY'),
(95, 105, 'E15', 'BALCONY'),
(96, 105, 'E16', 'BALCONY'),
(97, 105, 'E17', 'BALCONY'),
(98, 105, 'E18', 'BALCONY'),
(99, 105, 'E19', 'BALCONY'),
(100, 105, 'E20', 'BALCONY'),
(101, 106, 'F1', 'ODC'),
(102, 106, 'F2', 'ODC'),
(103, 106, 'F3', 'ODC'),
(104, 106, 'F4', 'ODC'),
(105, 106, 'F5', 'ODC'),
(106, 106, 'F6', 'ODC'),
(107, 106, 'F7', 'ODC'),
(108, 106, 'F8', 'ODC'),
(109, 106, 'F9', 'ODC'),
(110, 106, 'F10', 'ODC'),
(111, 106, 'F11', 'BALCONY'),
(112, 106, 'F12', 'BALCONY'),
(113, 106, 'F13', 'BALCONY'),
(114, 106, 'F14', 'BALCONY'),
(115, 106, 'F15', 'BALCONY'),
(116, 106, 'F16', 'BALCONY'),
(117, 106, 'F17', 'BALCONY'),
(118, 106, 'F18', 'BALCONY'),
(119, 106, 'F19', 'BALCONY'),
(120, 106, 'F20', 'BALCONY');

-- --------------------------------------------------------

--
-- Table structure for table `showtimes`
--

CREATE TABLE `showtimes` (
  `show_id` int(11) NOT NULL,
  `movie_id` int(11) DEFAULT NULL,
  `theater_id` int(11) DEFAULT NULL,
  `show_date` date DEFAULT NULL,
  `show_time` time DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `showtimes`
--

INSERT INTO `showtimes` (`show_id`, `movie_id`, `theater_id`, `show_date`, `show_time`) VALUES
(1, 1, 101, '2026-07-20', '09:00:00'),
(2, 2, 102, '2026-07-20', '13:00:00'),
(3, 3, 103, '2026-07-20', '17:00:00'),
(4, 4, 104, '2026-07-21', '10:00:00'),
(5, 5, 105, '2026-07-21', '15:00:00'),
(6, 6, 106, '2026-07-22', '19:00:00');

-- --------------------------------------------------------

--
-- Table structure for table `theaters`
--

CREATE TABLE `theaters` (
  `theater_id` int(11) NOT NULL,
  `theater_name` varchar(100) DEFAULT NULL,
  `location` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `theaters`
--

INSERT INTO `theaters` (`theater_id`, `theater_name`, `location`) VALUES
(101, 'Liberty Cinema', 'Colombo'),
(102, 'Savoy Cinema', 'Maradana'),
(103, 'Scope Cinema', 'Colombo City Centre'),
(104, 'Majestic Cineplex', 'Bambalapitiya'),
(105, 'CCC Multiplex', 'Colombo 5'),
(106, 'DCC Cinema', 'Colombo 2');

-- --------------------------------------------------------

--
-- Table structure for table `ticket`
--

CREATE TABLE `ticket` (
  `seat_type` varchar(30) NOT NULL,
  `price` decimal(10,0) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `ticket`
--

INSERT INTO `ticket` (`seat_type`, `price`) VALUES
('ODC', 800),
('BALCONY', 900);

-- --------------------------------------------------------

--
-- Table structure for table `upcomingmovies`
--

CREATE TABLE `upcomingmovies` (
  `title` varchar(100) NOT NULL,
  `duration` varchar(100) NOT NULL,
  `language` varchar(30) NOT NULL,
  `release_date` date NOT NULL,
  `poster` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `upcomingmovies`
--

INSERT INTO `upcomingmovies` (`title`, `duration`, `language`, `release_date`, `poster`) VALUES
('Minions and Monsters', '1h 30min', 'English', '2026-08-12', 'minions.JPEG'),
('Toy Story 5', '1h 45min', 'English', '2026-08-17', 'toystory5.JPEG'),
('Moana', '1h 36min', 'English', '2026-08-14', 'moana.JPEG'),
('Shreck 5', '1h 50min', 'English', '2026-08-12', 'shreck5.JPEG'),
('Frozen 3', '1h 58min', 'English', '2026-08-08', 'frozen3.JPEG'),
('Eka Thamai Meka', '1h 45min', 'Sinhala', '2016-08-19', 'ekathamaimeka.JPEG');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `admin`
--
ALTER TABLE `admin`
  ADD PRIMARY KEY (`admin_id`);

--
-- Indexes for table `bookings`
--
ALTER TABLE `bookings`
  ADD PRIMARY KEY (`booking_id`),
  ADD KEY `customer_id` (`customer_id`),
  ADD KEY `show_id` (`show_id`),
  ADD KEY `seat_id` (`seat_id`);

--
-- Indexes for table `customers`
--
ALTER TABLE `customers`
  ADD PRIMARY KEY (`customer_id`);

--
-- Indexes for table `movies`
--
ALTER TABLE `movies`
  ADD PRIMARY KEY (`movie_id`);

--
-- Indexes for table `payments`
--
ALTER TABLE `payments`
  ADD PRIMARY KEY (`payment_id`),
  ADD KEY `booking_id` (`booking_id`);

--
-- Indexes for table `seats`
--
ALTER TABLE `seats`
  ADD PRIMARY KEY (`seat_id`),
  ADD KEY `theater_id` (`theater_id`);

--
-- Indexes for table `showtimes`
--
ALTER TABLE `showtimes`
  ADD PRIMARY KEY (`show_id`),
  ADD KEY `movie_id` (`movie_id`),
  ADD KEY `theater_id` (`theater_id`);

--
-- Indexes for table `theaters`
--
ALTER TABLE `theaters`
  ADD PRIMARY KEY (`theater_id`);

--
-- Indexes for table `ticket`
--
ALTER TABLE `ticket`
  ADD PRIMARY KEY (`price`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bookings`
--
ALTER TABLE `bookings`
  MODIFY `booking_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=158;

--
-- AUTO_INCREMENT for table `customers`
--
ALTER TABLE `customers`
  MODIFY `customer_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=163;

--
-- AUTO_INCREMENT for table `movies`
--
ALTER TABLE `movies`
  MODIFY `movie_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `payments`
--
ALTER TABLE `payments`
  MODIFY `payment_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=43;

--
-- AUTO_INCREMENT for table `seats`
--
ALTER TABLE `seats`
  MODIFY `seat_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=121;

--
-- AUTO_INCREMENT for table `showtimes`
--
ALTER TABLE `showtimes`
  MODIFY `show_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `theaters`
--
ALTER TABLE `theaters`
  MODIFY `theater_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=107;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `bookings`
--
ALTER TABLE `bookings`
  ADD CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customers` (`customer_id`),
  ADD CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`show_id`) REFERENCES `showtimes` (`show_id`),
  ADD CONSTRAINT `bookings_ibfk_3` FOREIGN KEY (`seat_id`) REFERENCES `seats` (`seat_id`);

--
-- Constraints for table `payments`
--
ALTER TABLE `payments`
  ADD CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`booking_id`);

--
-- Constraints for table `seats`
--
ALTER TABLE `seats`
  ADD CONSTRAINT `seats_ibfk_1` FOREIGN KEY (`theater_id`) REFERENCES `theaters` (`theater_id`);

--
-- Constraints for table `showtimes`
--
ALTER TABLE `showtimes`
  ADD CONSTRAINT `showtimes_ibfk_1` FOREIGN KEY (`movie_id`) REFERENCES `movies` (`movie_id`),
  ADD CONSTRAINT `showtimes_ibfk_2` FOREIGN KEY (`theater_id`) REFERENCES `theaters` (`theater_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
