CREATE TABLE dim_customer (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_city VARCHAR(100),
    customer_state VARCHAR(10)
);

CREATE TABLE dim_product (
    product_id VARCHAR(50) PRIMARY KEY,
    product_category VARCHAR(100)
);

CREATE TABLE dim_date (
    date_id DATE PRIMARY KEY,
    year INT,
    month INT,
    month_name VARCHAR(20),
    year_month VARCHAR(7)
);

CREATE TABLE dim_inflation (
    inflation_id INT AUTO_INCREMENT PRIMARY KEY,
    year INT,
    month INT,
    year_month VARCHAR(7),
    inflation_rate DECIMAL(5,2)
);
