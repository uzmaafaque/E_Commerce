USE E_COMMERCE

select * from orders  ---32,313
select * from order_item_refunds  ---1,731
select * from order_items ---40,025
select * from products  ---4
select * from website_pageviews ---11,88,124
select * from website_sessions ---4,72,871
SELECT * FROM w_sessions ---4,72,871

select TOP 1 * from orders 
select TOP 1 * from order_item_refunds  
select TOP 1 * from order_items
select TOP 1 * from products  
select TOP 1 * from website_pageviews 
select TOP 1 *  from w_sessions

------------------------------------------------------------------------------------------------
---Total Sales
SELECT 
    round(SUM(price_usd),2) AS total_sales
FROM orders;

--Net Refund
select round(SUM(refund_amount_usd),2) as Net_Refund
from order_item_refunds

--Net Revenue
SELECT 
    SUM(o.price_usd) - COALESCE(SUM(r.refund_amount_usd), 0) AS net_revenue
FROM orders o
LEFT JOIN order_item_refunds r ON o.order_id = r.order_id;

--net profit
SELECT 
    ROUND((SUM(o.price_usd) - COALESCE(SUM(r.refund_amount_usd), 0) 
    - SUM(CASE WHEN r.order_item_refund_id IS NULL THEN o.cogs_usd ELSE 0 END)),2) AS PROFIT
FROM order_items o
LEFT JOIN order_item_refunds r 
ON o.order_item_id = r.order_item_id

--Total Cost
SELECT 
    ROUND(SUM(CASE WHEN oir.order_item_refund_id IS NULL THEN oi.cogs_usd ELSE 0 END), 2) 
	AS net_cogs
FROM order_items AS oi
LEFT JOIN order_item_refunds AS oir
    ON oi.order_item_id = oir.order_item_id

----TOTAL ITEMS REFUND
SELECT COUNT(order_item_refund_id) AS total_items_refunded
FROM order_item_refunds;


--total session count
select count(website_session_id) as Total_Sessions
from w_sessions

---REPEAT SESSIONS
SELECT COUNT(*) AS repeat_sessions
FROM w_sessions
WHERE is_repeat_session = 1;

---AVERAGE ORDER VALUE
SELECT 
    ROUND(SUM(price_usd) * 1.0 / COUNT(DISTINCT order_id), 2) AS avg_order_value
FROM order_items;

---AVERAGE REVENUE PER SESSION
SELECT 
    ROUND(SUM(o.price_usd) * 1.0 / COUNT(DISTINCT ws.website_session_id), 2) AS avg_revenue_per_session
FROM w_sessions ws
LEFT JOIN orders o 
    ON ws.website_session_id = o.website_session_id;

---AVERAGE SESSION PER USER
SELECT 
    ROUND(COUNT(website_session_id) * 1.0 / COUNT(DISTINCT user_id), 2) AS avg_sessions_per_user
FROM w_sessions;


--buyer count
SELECT COUNT(DISTINCT user_id) AS buyer_count
FROM orders;

--Total Items Sold
select COUNT(order_item_id) as total_items_sold
from order_items

---profit percentage
SELECT 
    ROUND((SUM(oi.price_usd) - COALESCE(SUM(r.refund_amount_usd), 0) 
    - SUM(CASE WHEN r.order_item_refund_id IS NULL THEN oi.cogs_usd ELSE 0 END)) 
    / NULLIF(SUM(CASE WHEN r.order_item_refund_id IS NULL THEN oi.cogs_usd ELSE 0 END), 0)
    * 100, 2) AS profit_percent
FROM order_items oi
LEFT JOIN order_item_refunds r 
ON oi.order_item_id = r.order_item_id


--Average Profit per Customer
SELECT 
    ROUND((SUM(o.price_usd) - COALESCE(SUM(r.refund_amount_usd), 0)- SUM(o.cogs_usd))
	/ NULLIF(COUNT(DISTINCT o.user_id), 0),2) AS avg_profit_per_customer
FROM orders o
LEFT JOIN order_item_refunds r ON o.order_id = r.order_id;

--Repeat Buyers
SELECT COUNT(*) AS repeat_buyers
FROM (SELECT user_id
    FROM orders
    GROUP BY user_id
    HAVING COUNT(order_id) > 1
) AS repeat_users;

---TOTAL QUANTITY
SELECT SUM(items_purchased) AS QUANTITY_SOLD
FROM orders

---AVERAGE ITEMS PER ORDER
SELECT ROUND(SUM(items_purchased)/COUNT(order_id),2) AS AVERAGE_ITEMS_PER_ORDER
FROM orders


---------------------------------------------YEARLY TRENDS------------------------------------
SELECT 
	DATEPART(YEAR, O.CREATED_AT) AS YEAR_,
    ROUND(SUM(o.price_usd) - COALESCE(SUM(r.refund_amount_usd), 0),0) AS net_revenue,
	ROUND((SUM(o.price_usd) - COALESCE(SUM(r.refund_amount_usd), 0) 
    - SUM(CASE WHEN r.order_item_refund_id IS NULL THEN o.cogs_usd ELSE 0 END)),2) AS PROFIT
FROM orders o
LEFT JOIN order_item_refunds r ON o.order_id = r.order_id
GROUP BY DATEPART(YEAR, O.CREATED_AT)
ORDER BY YEAR_
    
FROM order_items o
LEFT JOIN order_item_refunds r 
ON o.order_item_id = r.order_item_id



------------- TOTAL REVENUE, TOTAL SALES AND TOTAL PROFIT by MONTH-Year WISE-----------------------
SELECT 
    DATEPART(YEAR,O.created_at) AS YEAR_,
		DATENAME(MONTH,O.created_at) AS MONTH_,
		DATEPART(MONTH,O.created_at) AS month_number,
	SUM(PRICE_USD) AS SALES,
    SUM(o.price_usd) - COALESCE(SUM(r.refund_amount_usd), 0) AS Net_Revenue,
    --SUM(o.price_usd) - COALESCE(SUM(r.refund_amount_usd), 0) - SUM(o.cogs_usd) AS net_profit
	ROUND((SUM(o.price_usd) - COALESCE(SUM(r.refund_amount_usd), 0) 
    - SUM(CASE WHEN r.order_item_refund_id IS NULL THEN o.cogs_usd ELSE 0 END)), 
	0) AS NET_PROFIT

FROM orders o
LEFT JOIN order_item_refunds r ON o.order_id = r.order_id
GROUP BY DATEPART(YEAR,O.created_at),
		DATENAME(MONTH,O.created_at),
		DATEPART(MONTH,O.created_at)
ORDER BY YEAR_,month_number;

----------------------------------------VOLUME GROWTH--------------------------------------------
SELECT DATEPART(YEAR,O.CREATED_AT) AS YEAR_,
		DATEPART(QUARTER, O.CREATED_AT) AS QUATER_,
		COUNT(DISTINCT O.ORDER_ID) AS ORDERS
FROM orders AS O
GROUP BY DATEPART(YEAR,O.CREATED_AT),
		DATEPART(QUARTER, O.CREATED_AT)
ORDER BY YEAR_ , QUATER_


SELECT DATEPART(YEAR,W.CREATED_AT) AS YEAR_,
		DATEPART(QUARTER, W.CREATED_AT) AS QUATER_,
		COUNT(DISTINCT W.website_session_id) AS SESSIONS_
FROM w_sessions AS W
GROUP BY DATEPART(YEAR,W.CREATED_AT),
		DATEPART(QUARTER, W.CREATED_AT)
ORDER BY YEAR_ , QUATER_


-----------------------------Order Count & Session Count by Year---------------------------------
-- Order Count
SELECT 
    YEAR(created_at) AS year,
    COUNT(order_id) AS order_count
FROM orders
GROUP BY YEAR(created_at)
ORDER BY year;

-- Session Count
SELECT 
    YEAR(created_at) AS year,
    COUNT(website_session_id) AS session_count
FROM w_sessions
GROUP BY YEAR(created_at)
ORDER BY year;

----Conversion Rate by Year
SELECT 
    o.order_year,
    o.order_count,
    s.session_count,
    ROUND((o.order_count * 100.0) / NULLIF(s.session_count, 0), 2) AS conversion_rate
FROM (
    SELECT YEAR(created_at) AS order_year, COUNT(*) AS order_count
    FROM orders
    GROUP BY YEAR(created_at)
) o
JOIN (
    SELECT YEAR(created_at) AS session_year, COUNT(*) AS session_count
    FROM website_sessions
    GROUP BY YEAR(created_at)
) s ON o.order_year = s.session_year
ORDER BY o.order_year;

-------------------------------------Revenue per Session--------------------------------------
SELECT 
    ROUND(SUM(o.price_usd) / COUNT(ws.website_session_id), 2) AS revenue_per_session,

FROM orders o
JOIN w_sessions ws ON o.website_session_id = ws.website_session_id;


-----------------------------------QUATERLY Revenue per Session--------------------------------
WITH orders_quarter AS (
    SELECT 
        DATEPART(YEAR, created_at) AS order_year,
        DATEPART(QUARTER, created_at) AS order_quarter,
        SUM(price_usd) AS total_revenue
    FROM orders
    GROUP BY DATEPART(YEAR, created_at), DATEPART(QUARTER, created_at)
),
sessions_quarter AS (
    SELECT 
        DATEPART(YEAR, created_at) AS session_year,
        DATEPART(QUARTER, created_at) AS session_quarter,
        COUNT(*) AS total_sessions
    FROM website_sessions
    GROUP BY DATEPART(YEAR, created_at), DATEPART(QUARTER, created_at)
)
SELECT 
    o.order_year,
    o.order_quarter,
    o.total_revenue,
    s.total_sessions,
    ROUND(o.total_revenue / NULLIF(s.total_sessions, 0), 2) AS revenue_per_session
FROM orders_quarter o
JOIN sessions_quarter s 
    ON o.order_year = s.session_year AND o.order_quarter = s.session_quarter
ORDER BY o.order_year, o.order_quarter;


--------------------------------MONTHLY TREND BY UTM CAMPAIGN-----------------------------------
--BRAND
SELECT 
    FORMAT(O.created_at, 'yyyy-MM') AS month,
    COUNT(order_id) AS brand_order_count
FROM orders AS O
JOIN w_sessions AS W
ON O.website_session_id = W.website_session_id
WHERE LOWER(utm_campaign) LIKE '%brand%'
GROUP BY FORMAT(O.created_at, 'yyyy-MM')
ORDER BY month;

--NON BRAND
SELECT 
    FORMAT(O.created_at, 'yyyy-MM') AS month,
    COUNT(order_id) AS brand_order_count
FROM orders AS O
JOIN w_sessions AS W
ON O.website_session_id = W.website_session_id
WHERE LOWER(utm_campaign) NOT LIKE '%brand%'
GROUP BY FORMAT(O.created_at, 'yyyy-MM')
ORDER BY month;


--------------------MONTHLY CONVERSION RATE FROM /products PAGE TO ORDERS-----------------------
SELECT
    DATEPART(YEAR, WS.created_at) AS YEAR_,
	DATEPART(MONTH, WS.created_at) AS MONTH_,
    COUNT(DISTINCT pv.website_session_id) AS Session_Count,
    COUNT(DISTINCT o.order_id) AS Order_Count,
    ISNULL(ROUND(
        COUNT(DISTINCT o.order_id) * 100.0 / NULLIF(COUNT(DISTINCT pv.website_session_id), 0),
        2
    ), 0) AS Conversion_Rate
FROM w_sessions ws
JOIN website_pageviews pv
ON pv.website_session_id = ws.website_session_id
LEFT JOIN orders o
ON pv.website_session_id = o.website_session_id
WHERE pv.pageview_url = '/products'
GROUP BY DATEPART(YEAR, WS.created_at),
			DATEPART(MONTH, WS.created_at) 
ORDER BY MONTH_,YEAR_;

------------------------------MONTHLY ORDERS BY DEVICE TYPE-------------------------------------
--MOBILE
SELECT DATEPART(YEAR,O.created_at) AS YEAR_,
		DATEPART(MONTH,O.created_at) AS MONTH_,
		COUNT(O.order_id) AS NO_OF_ORDERS
FROM orders AS O
JOIN w_sessions AS W
ON O.website_session_id = W.website_session_id
WHERE W.device_type LIKE 'mobile'
GROUP BY W.device_type,DATEPART(MONTH,O.created_at),
		DATEPART(YEAR,O.created_at)
ORDER BY  YEAR_,MONTH_

--DESKTOP
SELECT DATEPART(YEAR,O.created_at) AS YEAR_,
		DATEPART(MONTH,O.created_at) AS MONTH_,
		COUNT(O.order_id) AS NO_OF_ORDERS
FROM orders AS O
JOIN w_sessions AS W
ON O.website_session_id = W.website_session_id
WHERE W.device_type LIKE 'desktop'
GROUP BY W.device_type,DATEPART(MONTH,O.created_at),
		DATEPART(YEAR,O.created_at)
ORDER BY  YEAR_,MONTH_

------------------------MONTHLY REVENUE , MARGIN, SALES TREND BY PRODUCT------------------------

---The Forever Love Bear
SELECT 
    DATEPART(YEAR, o.created_at) AS year_,
    DATENAME(MONTH, o.created_at) AS month_,
    DATEPART(MONTH, o.created_at) AS month_number,
    p.product_name,
    SUM(o.items_purchased) AS total_units_sold,
    SUM(o.price_usd) AS total_revenue,
	ROUND((SUM(o.price_usd) - COALESCE(SUM(oir.refund_amount_usd), 0) 
    - SUM(CASE WHEN oir.order_item_refund_id IS NULL THEN o.cogs_usd ELSE 0 END)),2) AS PROFIT
    --ROUND(SUM(CASE WHEN oir.order_item_refund_id IS NULL THEN oi.cogs_usd ELSE 0 END), 2) AS total_cost

FROM orders o
JOIN products p 
    ON o.primary_product_id = p.product_id 
JOIN order_items oi 
    ON o.order_id = oi.order_id
LEFT JOIN order_item_refunds oir 
    ON oi.order_item_id = oir.order_item_id

WHERE p.product_name LIKE 'The Forever Love Bear'

GROUP BY 
    DATEPART(YEAR, o.created_at),
    DATEPART(MONTH, o.created_at),
    DATENAME(MONTH, o.created_at),
    p.product_name

ORDER BY 
    year_, month_number, p.product_name;


----The Original Mr. Fuzzy
SELECT 
    DATEPART(YEAR, o.created_at) AS year_,
    DATENAME(MONTH, o.created_at) AS month_,
    DATEPART(MONTH, o.created_at) AS month_number,
    p.product_name,
    SUM(o.items_purchased) AS total_units_sold,
    SUM(o.price_usd) AS total_revenue,
	ROUND((SUM(o.price_usd) - COALESCE(SUM(oir.refund_amount_usd), 0) 
    - SUM(CASE WHEN oir.order_item_refund_id IS NULL THEN o.cogs_usd ELSE 0 END)),2) AS PROFIT
    --ROUND(SUM(CASE WHEN oir.order_item_refund_id IS NULL THEN oi.cogs_usd ELSE 0 END), 2) AS total_cost

FROM orders o
JOIN products p 
    ON o.primary_product_id = p.product_id 
JOIN order_items oi 
    ON o.order_id = oi.order_id
LEFT JOIN order_item_refunds oir 
    ON oi.order_item_id = oir.order_item_id

WHERE p.product_name LIKE 'The Original Mr. Fuzzy'

GROUP BY 
    DATEPART(YEAR, o.created_at),
    DATEPART(MONTH, o.created_at),
    DATENAME(MONTH, o.created_at),
    p.product_name

ORDER BY 
    year_, month_number, p.product_name;

--The Birthday Sugar Panda
SELECT 
    DATEPART(YEAR, o.created_at) AS year_,
    DATENAME(MONTH, o.created_at) AS month_,
    DATEPART(MONTH, o.created_at) AS month_number,
    p.product_name,
    SUM(o.items_purchased) AS total_units_sold,
    SUM(o.price_usd) AS total_revenue,
	ROUND((SUM(o.price_usd) - COALESCE(SUM(oir.refund_amount_usd), 0) 
    - SUM(CASE WHEN oir.order_item_refund_id IS NULL THEN o.cogs_usd ELSE 0 END)),2) AS PROFIT
    --ROUND(SUM(CASE WHEN oir.order_item_refund_id IS NULL THEN oi.cogs_usd ELSE 0 END), 2) AS total_cost

FROM orders o
JOIN products p 
    ON o.primary_product_id = p.product_id 
JOIN order_items oi 
    ON o.order_id = oi.order_id
LEFT JOIN order_item_refunds oir 
    ON oi.order_item_id = oir.order_item_id

WHERE p.product_name LIKE 'The Birthday Sugar Panda'

GROUP BY 
    DATEPART(YEAR, o.created_at),
    DATEPART(MONTH, o.created_at),
    DATENAME(MONTH, o.created_at),
    p.product_name

ORDER BY 
    year_, month_number, p.product_name;


----The Hudson River Mini bear
SELECT 
    DATEPART(YEAR, o.created_at) AS year_,
    DATENAME(MONTH, o.created_at) AS month_,
    DATEPART(MONTH, o.created_at) AS month_number,
    p.product_name,
    SUM(o.items_purchased) AS total_units_sold,
    SUM(o.price_usd) AS total_revenue,
	ROUND((SUM(o.price_usd) - COALESCE(SUM(oir.refund_amount_usd), 0) 
    - SUM(CASE WHEN oir.order_item_refund_id IS NULL THEN o.cogs_usd ELSE 0 END)),2) AS PROFIT
    --ROUND(SUM(CASE WHEN oir.order_item_refund_id IS NULL THEN oi.cogs_usd ELSE 0 END), 2) AS total_cost

FROM orders o
JOIN products p 
    ON o.primary_product_id = p.product_id 
JOIN order_items oi 
    ON o.order_id = oi.order_id
LEFT JOIN order_item_refunds oir 
    ON oi.order_item_id = oir.order_item_id

WHERE p.product_name LIKE 'The Hudson River Mini bear'

GROUP BY 
    DATEPART(YEAR, o.created_at),
    DATEPART(MONTH, o.created_at),
    DATENAME(MONTH, o.created_at),
    p.product_name

ORDER BY 
    year_, month_number, p.product_name;

---------------------------QUATERLY GROWTH BY CHANNEL-------------------------------------------
--gsearch nonbrand
SELECT
    DATEPART(YEAR, o.created_at) AS year_,
    DATEPART(QUARTER, o.created_at) AS QUATER_,
    w.utm_source,w.utm_campaign,
    COUNT(o.order_id) AS total_orders
FROM orders o
JOIN w_sessions w 
ON o.website_session_id = w.website_session_id
WHERE utm_source LIKE 'gsearch' and utm_campaign like 'nonbrand'
GROUP BY DATEPART(YEAR , o.created_at),DATEPART(QUARTER , o.created_at),
    w.utm_source,w.utm_campaign
ORDER BY  year_, QUATER_

--gsearch brand
SELECT
    DATEPART(YEAR, o.created_at) AS year_,
    DATEPART(QUARTER, o.created_at) AS QUATER_,
    w.utm_source,w.utm_campaign,
    COUNT(o.order_id) AS total_orders
FROM orders o
JOIN w_sessions w 
ON o.website_session_id = w.website_session_id
WHERE utm_source LIKE 'gsearch' and utm_campaign like 'brand'
GROUP BY DATEPART(YEAR , o.created_at),DATEPART(QUARTER , o.created_at),
    w.utm_source,w.utm_campaign
ORDER BY year_, QUATER_

---bsearch brand
SELECT
    DATEPART(YEAR, o.created_at) AS year_,
    DATEPART(QUARTER, o.created_at) AS QUATER_,
    w.utm_source,w.utm_campaign,
    COUNT(o.order_id) AS total_orders
FROM orders o
JOIN w_sessions w 
ON o.website_session_id = w.website_session_id
WHERE utm_source LIKE 'bsearch' and utm_campaign like 'brand'
GROUP BY DATEPART(YEAR , o.created_at),DATEPART(QUARTER , o.created_at),
    w.utm_source, w.utm_campaign
ORDER BY year_, QUATER_

---bsearch nonbrand
SELECT
    DATEPART(YEAR, o.created_at) AS year_,
    DATEPART(QUARTER, o.created_at) AS QUATER_,
    w.utm_source,w.utm_campaign,
    COUNT(o.order_id) AS total_orders
FROM orders o
JOIN w_sessions w 
ON o.website_session_id = w.website_session_id
WHERE utm_source LIKE 'bsearch' and utm_campaign like 'nonbrand'
GROUP BY DATEPART(YEAR , o.created_at),DATEPART(QUARTER , o.created_at),
    w.utm_source, w.utm_campaign
ORDER BY  year_, QUATER_