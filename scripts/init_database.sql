/*
=============================================================
Create Database and Schemas
=============================================================
Script Purpose:
    Creates the 'datawarehouse' database and
    creates bronze, silver, and gold schemas.
=============================================================
*/

-- Drop database if exists
DROP DATABASE IF EXISTS datawarehouse;

-- Create database
CREATE DATABASE datawarehouse;
--connect datawarehouse
-- Create Schemas
CREATE SCHEMA bronze;

CREATE SCHEMA silver;

CREATE SCHEMA gold;


