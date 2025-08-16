CREATE DATABASE loan_default;

USE loan_default;

CREATE TABLE loan_applications (
    age INT,
    income int,
    loanAmount int,
    creditScore INT,
    monthsEmployed INT,
    interestRate float,
    dtiRatio float,
    loanTerm INT ,
    prediction TINYINT(1)
);


show tables;

SELECT *
FROM loan_applications;