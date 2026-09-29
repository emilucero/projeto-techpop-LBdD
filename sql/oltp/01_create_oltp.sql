-- =============================================
-- TECHPOP - OLTP (SISTEMA FATORV)
-- SCRIPT DDL - CRIAÇÃO DAS TABELAS
-- =============================================
-- Fonte: DDL fornecido pelo professor
-- Banco: techpop_oltp
-- =============================================

-- public.categories definition
CREATE TABLE IF NOT EXISTS public.categories (
    category_id serial4 NOT NULL,
    category_name varchar(100) NULL,
    CONSTRAINT categories_pkey PRIMARY KEY (category_id)
);

-- public.customers definition
CREATE TABLE IF NOT EXISTS public.customers (
    customer_id serial4 NOT NULL,
    customer_name varchar(100) NULL,
    email varchar(100) NULL,
    state varchar(2) NULL,
    CONSTRAINT customers_pkey PRIMARY KEY (customer_id)
);

-- public.sellers definition
CREATE TABLE IF NOT EXISTS public.sellers (
    seller_id serial4 NOT NULL,
    seller_name varchar(100) NULL,
    email varchar(100) NULL,
    state varchar(2) NULL,
    tx_commission int4 NULL,
    CONSTRAINT sellers_pkey PRIMARY KEY (seller_id)
);

-- public.suppliers definition
CREATE TABLE IF NOT EXISTS public.suppliers (
    supplier_id serial4 NOT NULL,
    supplier_name varchar(100) NULL,
    email varchar(100) NULL,
    state varchar(50) NULL,
    CONSTRAINT suppliers_pkey PRIMARY KEY (supplier_id)
);

-- public.products definition
CREATE TABLE IF NOT EXISTS public.products (
    product_id serial4 NOT NULL,
    product_name varchar(100) NULL,
    category_id int4 NULL,
    price numeric NULL,
    supplier_id int4 NULL,
    CONSTRAINT products_pkey PRIMARY KEY (product_id),
    CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(category_id),
    CONSTRAINT products_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(supplier_id)
);

-- public.sales definition
CREATE TABLE IF NOT EXISTS public.sales (
    sales_id serial4 NOT NULL,
    "date" date NULL,
    customer_id int4 NULL,
    seller_id int4 NULL,
    total_price numeric NULL,
    CONSTRAINT sales_pkey PRIMARY KEY (sales_id),
    CONSTRAINT sales_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(customer_id),
    CONSTRAINT sales_seller_id_fkey FOREIGN KEY (seller_id) REFERENCES public.sellers(seller_id)
);

-- public.sales_items definition
CREATE TABLE IF NOT EXISTS public.sales_items (
    item_id serial4 NOT NULL,
    sales_id int4 NOT NULL,
    product_id int4 NULL,
    quantity int4 NULL,
    price numeric NULL,
    CONSTRAINT sales_items_pkey PRIMARY KEY (item_id, sales_id),
    CONSTRAINT sales_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(product_id),
    CONSTRAINT sales_items_sales_id_fkey FOREIGN KEY (sales_id) REFERENCES public.sales(sales_id)
);
