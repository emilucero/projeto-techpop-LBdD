-- =============================================
-- TECHPOP - OLTP (SISTEMA FATORV)
-- SCRIPT DML - CARGA DOS DADOS
-- =============================================
-- Fonte: DML fornecido pelo professor
-- Banco: techpop_oltp
-- =============================================

-- Inserts para a tabela public.categories
INSERT INTO public.categories (category_name) VALUES 
('Electronics'), ('Clothing'), ('Books'), ('Home Appliances'),
('Toys'), ('Furniture'), ('Sports'), ('Beauty'), ('Food');

-- Inserts para a tabela public.customers
INSERT INTO public.customers (customer_name, email, state) VALUES 
('John Doe', 'john@example.com', 'CA'),
('Jane Smith', 'jane@example.com', 'NY'),
('Michael Johnson', 'michael@example.com', 'TX'),
('Emily Davis', 'emily@example.com', 'FL'),
('David Brown', 'david@example.com', 'WA'),
('Robert Miller', 'robert@example.com', 'CA'),
('Mary Wilson', 'mary@example.com', 'TX'),
('Sarah Martinez', 'sarah@example.com', 'NY'),
('James Taylor', 'james@example.com', 'FL');

-- Inserts para a tabela public.sellers
INSERT INTO public.sellers (seller_name, email, state, tx_commission) VALUES 
('Best Electronics', 'best@example.com', 'CA', 10),
('Fashion House', 'fashion@example.com', 'NY', 12),
('Book Emporium', 'books@example.com', 'TX', 15),
('Tech Universe', 'tech@example.com', 'CA', 11),
('Style Center', 'style@example.com', 'FL', 13),
('Furniture Haven', 'furniture@example.com', 'WA', 14),
('Sports Emporium', 'sports@example.com', 'CA', 10),
('Beauty Trends', 'beauty@example.com', 'NY', 12),
('Food Paradise', 'food@example.com', 'TX', 15);

-- Inserts para a tabela public.suppliers
INSERT INTO public.suppliers (supplier_name, email, state) VALUES 
('Tech Supplies Inc.', 'tech@example.com', 'CA'),
('Fashion Trends Ltd.', 'fashiontrends@example.com', 'NY'),
('Book Haven', 'bookhaven@example.com', 'TX'),
('Appliance World', 'appliances@example.com', 'FL'),
('Toy Kingdom', 'toys@example.com', 'CA'),
('Furniture Warehouse', 'furniture@example.com', 'WA'),
('Sports Suppliers', 'sports@example.com', 'TX'),
('Beauty Supplies', 'beauty@example.com', 'NY'),
('Food Distributors', 'food@example.com', 'FL');

-- Inserts para a tabela public.products
INSERT INTO public.products (product_name, category_id, price, supplier_id) VALUES 
('Smartphone', 1, 800.00, 1),
('Jeans', 2, 50.00, 2),
('Mystery Novel', 3, 20.00, 3),
('Microwave Oven', 4, 150.00, 4),
('Remote Control Car', 5, 30.00, 5),
('Office Chair', 6, 120.00, 6),
('Basketball', 7, 25.00, 7),
('Lipstick', 8, 10.00, 8),
('Pizza', 9, 12.00, 9);

-- Inserts para a tabela public.sales
INSERT INTO public.sales ("date", customer_id, seller_id, total_price) VALUES 
('2023-05-15', 1, 1, 700.00),
('2023-05-15', 2, 2, 70.00),
('2023-05-15', 3, 3, 180.00),
('2023-05-15', 4, 4, 250.00),
('2023-05-15', 5, 5, 90.00),
('2022-08-20', 6, 6, 480.00),
('2022-08-20', 7, 7, 160.00),
('2022-08-20', 8, 8, 150.00),
('2022-08-20', 9, 9, 36.00);

-- Inserts para a tabela public.sales_items
INSERT INTO public.sales_items (item_id, sales_id, product_id, quantity, price) VALUES 
(1, 1, 1, 1, 800.00),
(2, 1, 2, 2, 50.00),
(1, 2, 6, 1, 120.00),
(2, 2, 7, 3, 25.00),
(3, 2, 8, 2, 10.00),
(4, 2, 9, 3, 12.00),
(5, 2, 1, 1, 15.00),
(1, 3, 2, 2, 22.00),
(2, 3, 3, 1, 8.00),
(1, 4, 7, 1, 25.00),
(2, 4, 8, 2, 20.00),
(3, 4, 9, 1, 15.00),
(4, 4, 1, 2, 12.00),
(1, 5, 3, 1, 50.00),
(1, 6, 8, 1, 30.00),
(2, 6, 9, 2, 40.00),
(3, 6, 1, 1, 50.00),
(1, 7, 4, 1, 25.00),
(2, 7, 5, 2, 20.00),
(3, 7, 6, 1, 15.00),
(4, 7, 7, 2, 12.00),
(1, 8, 9, 1, 45.00),
(2, 8, 1, 2, 35.00),
(1, 9, 5, 1, 38.00),
(2, 9, 6, 2, 45.00),
(3, 9, 7, 1, 52.00),
(4, 9, 8, 2, 60.00),
(5, 9, 9, 3, 72.00);
