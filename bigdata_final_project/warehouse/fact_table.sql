CREATE TABLE fact_sales (
    order_id VARCHAR(50),
    customer_id VARCHAR(50),
    product_id VARCHAR(50),
    date_id DATE,
    inflation_id INT,

    price DECIMAL(10,2),
    freight_value DECIMAL(10,2),
    total_payment DECIMAL(10,2),
    delivery_days INT,

    PRIMARY KEY (order_id, product_id)
);
