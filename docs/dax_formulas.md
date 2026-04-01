# 📐 DAX Formulas for Power BI Dashboard

> All DAX measures for the Sales Analytics Dashboard. Copy-paste directly into Power BI Desktop.

---

## 🎯 KPI Card Measures

### 1. Total Sales
```dax
Total Sales = 
    SUM('Sales'[Sales])
```

**Formatted as:** Currency ($), 2 decimal places

---

### 2. Total Profit
```dax
Total Profit = 
    SUM('Sales'[Profit])
```

**Formatted as:** Currency ($), 2 decimal places

---

### 3. Total Orders
```dax
Total Orders = 
    COUNTROWS('Sales')
```

**Formatted as:** Whole Number with comma separator

---

### 4. Average Order Value (AOV)
```dax
Avg Order Value = 
    DIVIDE(
        [Total Sales],
        [Total Orders],
        0
    )
```

**Formatted as:** Currency ($), 2 decimal places

---

### 5. Profit Margin %
```dax
Profit Margin % = 
    DIVIDE(
        [Total Profit],
        [Total Sales],
        0
    ) * 100
```

**Formatted as:** Percentage, 2 decimal places

---

### 6. Total Quantity Sold
```dax
Total Quantity = 
    SUM('Sales'[Quantity])
```

---

## 📈 Trend & Comparison Measures

### 7. Sales Previous Year (for YoY comparison)
```dax
Sales PY = 
    CALCULATE(
        [Total Sales],
        SAMEPERIODLASTYEAR('DateTable'[Date])
    )
```

### 8. Year-over-Year Sales Growth %
```dax
YoY Growth % = 
    VAR CurrentSales = [Total Sales]
    VAR PreviousSales = [Sales PY]
    RETURN
        DIVIDE(
            CurrentSales - PreviousSales,
            PreviousSales,
            0
        ) * 100
```

### 9. Sales Month-to-Date
```dax
Sales MTD = 
    TOTALMTD(
        [Total Sales],
        'DateTable'[Date]
    )
```

### 10. Sales Year-to-Date
```dax
Sales YTD = 
    TOTALYTD(
        [Total Sales],
        'DateTable'[Date]
    )
```

---

## 📊 Ranking & Analysis Measures

### 11. Top Category by Sales
```dax
Category Rank = 
    RANKX(
        ALL('Sales'[Category]),
        [Total Sales],
        ,
        DESC,
        Dense
    )
```

### 12. Region Sales Share %
```dax
Region Sales Share % = 
    DIVIDE(
        [Total Sales],
        CALCULATE(
            [Total Sales],
            ALL('Sales'[Region])
        ),
        0
    ) * 100
```

### 13. Running Total Sales
```dax
Running Total = 
    CALCULATE(
        [Total Sales],
        FILTER(
            ALLSELECTED('DateTable'[Date]),
            'DateTable'[Date] <= MAX('DateTable'[Date])
        )
    )
```

---

## 🔢 Conditional Formatting Measures

### 14. Profit Status (for traffic-light indicators)
```dax
Profit Status = 
    SWITCH(
        TRUE(),
        [Profit Margin %] >= 20, "High",
        [Profit Margin %] >= 10, "Medium",
        [Profit Margin %] >= 0,  "Low",
        "Loss"
    )
```

### 15. Sales Performance Indicator
```dax
Sales vs Target = 
    VAR SalesTarget = 1000000  -- Adjust target as needed
    RETURN
        DIVIDE(
            [Total Sales],
            SalesTarget,
            0
        ) * 100
```

---

## 📅 Date Table (Required for Time Intelligence)

> **Create this calculated table FIRST** — Power BI time intelligence functions require a proper date table.

```dax
DateTable = 
    ADDCOLUMNS(
        CALENDARAUTO(),
        "Year", YEAR([Date]),
        "Month Number", MONTH([Date]),
        "Month Name", FORMAT([Date], "MMMM"),
        "Month Short", FORMAT([Date], "MMM"),
        "Quarter", "Q" & QUARTER([Date]),
        "Day of Week", FORMAT([Date], "dddd"),
        "Day Number", WEEKDAY([Date], 2),
        "Year-Month", FORMAT([Date], "YYYY-MM"),
        "Is Weekend", IF(WEEKDAY([Date], 2) > 5, TRUE(), FALSE())
    )
```

> ⚠️ **Important:** After creating the DateTable, mark it as a **Date Table** in Power BI:
> - Right-click `DateTable` → **Mark as Date Table** → Select the `Date` column

---

## 🔗 Relationship Setup

After creating the DateTable, create a relationship:

| From Table | From Column | To Table | To Column | Type |
|------------|-------------|----------|-----------|------|
| Sales | Order Date | DateTable | Date | Many-to-One |

---

## 💡 Usage Tips

1. **Create a Measures Table**: Right-click in the Fields pane → "New Table" → `Measures = ROW("Empty", BLANK())`. Store all measures here for organisation.
2. **Format measures**: After creating each measure, set the format in the Modeling tab.
3. **Use DAX variables**: `VAR` / `RETURN` pattern improves readability and performance.
4. **Test incrementally**: Add one measure at a time and verify with a simple card visual.
