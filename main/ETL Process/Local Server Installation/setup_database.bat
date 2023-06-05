@echo off
REM Ask for username
SET /p USER=Please enter your localhost username (Default is called 'root') 
SET /p PASS=Please enter your localhost password 

REM Create the database
mysql -u %USER% -p%PASS% -e "DROP DATABASE IF EXISTS db_capstone"
mysql -u %USER% -p%PASS% -e "CREATE DATABASE db_capstone"

REM Import dump file
mysql -u %USER% -p%PASS% db_test < db_capstone_wdata_dump.sql
@ echo Database is set up!
pause

