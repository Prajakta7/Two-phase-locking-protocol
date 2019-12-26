-- phpMyAdmin SQL Dump
-- version 4.8.5
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 26, 2019 at 12:30 AM
-- Server version: 10.1.38-MariaDB
-- PHP Version: 7.1.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `project1`
--

-- --------------------------------------------------------

--
-- Table structure for table `locktable`
--

CREATE TABLE `locktable` (
  `item` varchar(20) NOT NULL,
  `state` varchar(20) NOT NULL,
  `Tid_holding` varchar(20) NOT NULL,
  `Tid_waiting` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `locktable`
--

INSERT INTO `locktable` (`item`, `state`, `Tid_holding`, `Tid_waiting`) VALUES
('Y', 'Unlocked', '', ''),
('Z', 'Unlocked', '', ''),
('X', 'Unlocked', '', '');

-- --------------------------------------------------------

--
-- Table structure for table `transaction`
--

CREATE TABLE `transaction` (
  `Tid` varchar(10) NOT NULL,
  `Ttimestamp` int(20) NOT NULL,
  `TStatus` varchar(15) NOT NULL,
  `Items` varchar(18) NOT NULL,
  `Operation` varchar(17) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `transaction`
--

INSERT INTO `transaction` (`Tid`, `Ttimestamp`, `TStatus`, `Items`, `Operation`) VALUES
('T1', 1, 'commited', '', ''),
('T2', 2, 'commited', '', 'r2(Y);w2(Y);r2(X)'),
('T3', 3, 'Aborted', '', '');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
