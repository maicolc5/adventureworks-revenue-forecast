
    
SELECT
        DATEFROMPARTS(YEAR(soh.OrderDate), MONTH(soh.OrderDate), 1) AS fecha,
        MONTH(soh.OrderDate) as [month], 
        CASE
            WHEN soh.OnlineOrderFlag = 1 THEN 'online'
            ELSE 'reseller'
            END AS channel,
        COUNT(DISTINCT soh.SalesOrderID) AS orders,
        SUM(sod.LineTotal) AS revenue,
        SUM(sod.OrderQty) as unit_qty,
        COUNT(DISTINCT soh.CustomerID) as customers,
        count( distinct( OrderDate)) as active_days,
        min(OrderDate) as first_order_date,
        max(OrderDate) as last_order_date
    FROM Sales.SalesOrderHeader AS soh
        JOIN Sales.SalesOrderDetail AS sod
        ON soh.SalesOrderID = sod.SalesOrderID
    GROUP BY
        DATEFROMPARTS(YEAR(soh.OrderDate), MONTH(soh.OrderDate), 1),
        soh.OnlineOrderFlag,  MONTH(soh.OrderDate)
    ORDER BY
        fecha,
        channel

/*
 select /* sod.SalesOrderID, CustomerID, sum(OrderQty) as qty*/   *  FROM Sales.SalesOrderHeader soh
        JOIN Sales.SalesOrderDetail sod ON soh.SalesOrderID = sod.SalesOrderID
        where DATEFROMPARTS(YEAR(soh.OrderDate), MONTH(soh.OrderDate), 1) = '2024-03-01' and soh.OnlineOrderFlag = 0
      --  group by sod.SalesOrderID, CustomerID
      */

