# 🛠️ Step-by-Step Power BI Dashboard Instructions

> Complete guide to building the Sales Analytics Dashboard from scratch in Power BI Desktop.

---

## Prerequisites

| Requirement | Version | Download |
|-------------|---------|----------|
| Power BI Desktop | Latest | [Download](https://powerbi.microsoft.com/desktop/) |
| Python 3.8+ | 3.8+ | [Download](https://python.org) |
| Cleaned Dataset | — | Run `data_cleaning.py` first |

---

## Phase 1: Data Import & Preparation

### Step 1 — Import the Cleaned CSV

1. Open **Power BI Desktop**
2. Click **Home** → **Get Data** → **Text/CSV**
3. Browse to: `data/cleaned_sales_data.csv`
4. In the preview window, verify:
   - Column headers are detected correctly
   - Data types look reasonable
5. Click **Transform Data** (do NOT click "Load" yet)

### Step 2 — Verify Data Types in Power Query

In the Power Query Editor:

| Column | Set Type To |
|--------|-------------|
| Order Date | Date |
| Ship Date | Date |
| Sales | Decimal Number |
| Profit | Decimal Number |
| Quantity | Whole Number |
| Unit Price | Decimal Number |
| Shipping Cost | Decimal Number |
| Discount | Decimal Number |
| Profit Margin (%) | Decimal Number |
| Year | Whole Number |
| Month | Whole Number |

1. Select each column → **Transform** tab → **Data Type** → choose correct type
2. Click **Close & Apply**

### Step 3 — Create the Date Table

1. Go to **Modeling** tab → **New Table**
2. Paste the DateTable DAX formula from `docs/dax_formulas.md`
3. Right-click the new `DateTable` → **Mark as Date Table** → Select `Date`
4. In the **Model** view, drag `Sales[Order Date]` to `DateTable[Date]` to create a relationship

---

## Phase 2: Create DAX Measures

### Step 4 — Create a Measures Table

1. **Modeling** → **New Table**
2. Enter: `Measures = ROW("Empty", BLANK())`
3. This gives you a dedicated table for all your measures

### Step 5 — Add KPI Measures

For each measure below, right-click the **Measures** table → **New Measure** → paste the DAX:

1. **Total Sales** = `SUM('Sales'[Sales])`
2. **Total Profit** = `SUM('Sales'[Profit])`
3. **Total Orders** = `COUNTROWS('Sales')`
4. **Avg Order Value** = `DIVIDE([Total Sales], [Total Orders], 0)`
5. **Profit Margin %** = `DIVIDE([Total Profit], [Total Sales], 0) * 100`
6. **Total Quantity** = `SUM('Sales'[Quantity])`

> 💡 See `docs/dax_formulas.md` for all formulas with formatting instructions.

---

## Phase 3: Dashboard Layout Design

### Step 6 — Set Up the Canvas

1. Go to **View** tab → set **Page size** to `16:9` (default)
2. Set **Canvas background**:
   - Color: `#0D1117` (dark theme) or `#F8F9FA` (light theme)
   - Transparency: `0%`
3. Add a **Text Box** at the top:
   - Text: `📊 Sales Analytics Dashboard`
   - Font: Segoe UI, 24pt, Bold, White

### Step 7 — Dashboard Header Area

Add a **Rectangle** shape across the top:
- Width: Full page width
- Height: ~80px
- Fill: Linear gradient `#667EEA` → `#764BA2`
- Place the title text box inside this rectangle

---

## Phase 4: Add KPI Cards

### Step 8 — Total Sales Card

1. Click **Visualizations** → **Card** visual
2. Drag `[Total Sales]` to the **Fields** well
3. Format:
   - **Callout Value**: Font 28pt, Bold, Color `#2ECC71`
   - **Category Label**: "Total Sales", Font 11pt, Color `#AAAAAA`
   - **Background**: `#1A1F2E`, rounded corners 10px
   - **Border**: 1px `#2D3748`
4. Size: ~200px × 120px

### Step 9 — Total Profit Card

1. Duplicate the Sales card (Ctrl+C → Ctrl+V)
2. Replace field with `[Total Profit]`
3. Change callout color to `#3498DB`
4. Update label to "Total Profit"

### Step 10 — Total Orders Card

1. Duplicate again
2. Replace field with `[Total Orders]`
3. Change callout color to `#E74C3C`
4. Update label to "Total Orders"

### Step 11 — Avg Order Value Card (Bonus)

1. Duplicate again
2. Replace field with `[Avg Order Value]`
3. Change callout color to `#F39C12`
4. Update label to "Avg Order Value"

> 📐 **Layout**: Arrange all 4 cards in a horizontal row below the header.

---

## Phase 5: Add Visualizations

### Step 12 — Sales Trend Line Chart

1. Add a **Line Chart** visual
2. Configure:
   - **X-Axis**: `DateTable[Date]` (set to Month level)
   - **Y-Axis**: `[Total Sales]`
   - **Legend**: `Sales[Category]` (optional, for multi-line)
3. Format:
   - Title: "📈 Sales Trend Over Time"
   - Line width: 3px
   - Data colors: Use a gradient palette
   - Background: `#1A1F2E`
   - Grid lines: Subtle `#2D3748`
4. Size: ~50% page width × 250px

### Step 13 — Profit by Category Bar Chart

1. Add a **Clustered Bar Chart** visual
2. Configure:
   - **Y-Axis**: `Sales[Category]`
   - **X-Axis**: `[Total Profit]`
3. Format:
   - Title: "💰 Profit by Category"
   - Data colors: Custom per bar
     - Technology: `#667EEA`
     - Furniture: `#764BA2`
     - Office Supplies: `#2ECC71`
     - Clothing: `#F39C12`
   - Background: `#1A1F2E`
   - Data labels: ON
4. Size: ~25% page width × 250px

### Step 14 — Region-wise Sales (Donut Chart)

1. Add a **Donut Chart** visual
2. Configure:
   - **Legend**: `Sales[Region]`
   - **Values**: `[Total Sales]`
3. Format:
   - Title: "🌎 Sales by Region"
   - Colors:
     - West: `#667EEA`
     - East: `#2ECC71`
     - Central: `#F39C12`
     - South: `#E74C3C`
   - Inner radius: 60%
   - Detail labels: Show percentage
   - Background: `#1A1F2E`
4. Size: ~25% page width × 250px

### Step 15 — Sales by Sub-Category (Treemap)

1. Add a **Treemap** visual
2. Configure:
   - **Category**: `Sales[Sub-Category]`
   - **Values**: `[Total Sales]`
3. Format:
   - Title: "🏷️ Sales by Sub-Category"
   - Data labels: ON with values
   - Background: `#1A1F2E`
4. Size: ~50% page width × 200px

### Step 16 — Monthly Profit Trend (Area Chart)

1. Add an **Area Chart** visual
2. Configure:
   - **X-Axis**: `DateTable[Year-Month]`
   - **Y-Axis**: `[Total Profit]`
3. Format:
   - Title: "📉 Monthly Profit Trend"
   - Fill opacity: 40%
   - Line color: `#2ECC71`
   - Background: `#1A1F2E`
4. Size: ~50% page width × 200px

---

## Phase 6: Add Filters / Slicers

### Step 17 — Date Range Slicer

1. Add a **Slicer** visual
2. Drag `DateTable[Date]` to the **Field** well
3. Click the dropdown arrow → select **Between** (range slider)
4. Format:
   - Style: Slider
   - Background: `#1A1F2E`
   - Font color: White
5. Position: Top-right area of dashboard

### Step 18 — Category Slicer

1. Add a **Slicer** visual
2. Drag `Sales[Category]` to the **Field** well
3. Format:
   - Style: **Dropdown** or **Tile**
   - Selection: Multi-select enabled
   - Background: `#1A1F2E`
5. Position: Right sidebar or below header

### Step 19 — Region Slicer

1. Add a **Slicer** visual
2. Drag `Sales[Region]` to the **Field** well
3. Format same as Category slicer
4. Position: Next to Category slicer

---

## Phase 7: Final Polish

### Step 20 — Theme & Formatting

1. **View** → **Themes** → **Browse for themes**
2. Or manually set a consistent dark theme:
   - Background: `#0D1117`
   - Card backgrounds: `#1A1F2E`
   - Text: `#FFFFFF` (primary), `#AAAAAA` (secondary)
   - Accent colors: `#667EEA`, `#2ECC71`, `#E74C3C`, `#F39C12`

### Step 21 — Add Interactivity

1. Select each visual → **Format** → **Edit interactions**
2. Set cross-filtering: When you click a bar, it filters all other visuals
3. Add **Tooltips**: Hover info showing Sales, Profit, Margin %

### Step 22 — Mobile Layout (Optional)

1. **View** → **Mobile Layout**
2. Drag visuals to rearrange for phone view
3. Prioritize: KPI Cards → Trend Chart → Slicers

### Step 23 — Save & Publish

1. **File** → **Save As** → `Sales_Analytics_Dashboard.pbix`
2. To publish: **Home** → **Publish** → Select a workspace
3. Share the dashboard link with stakeholders

---

## 📋 Final Dashboard Layout Reference

```
┌─────────────────────────────────────────────────────────────┐
│  📊 Sales Analytics Dashboard          [Date] [Cat] [Region]│
├──────────┬──────────┬──────────┬──────────┬─────────────────┤
│  Total   │  Total   │  Total   │   Avg    │                 │
│  Sales   │  Profit  │  Orders  │  AOV     │                 │
│ $X.XXM   │ $X.XXM   │  X,XXX   │  $XXX    │                 │
├────────────────────────────────┬─────────┬──────────────────┤
│                                │  Profit │  Sales by        │
│  📈 Sales Trend Over Time      │  by     │  Region          │
│       (Line Chart)             │Category │  (Donut)         │
│                                │ (Bar)   │                  │
├────────────────────────────────┴─────────┴──────────────────┤
│  🏷️ Sales by Sub-Category      │  📉 Monthly Profit Trend   │
│       (Treemap)                │       (Area Chart)         │
└─────────────────────────────────────────────────────────────┘
```

---

## ⏱️ Estimated Time

| Phase | Time |
|-------|------|
| Data Import | 5 min |
| DAX Measures | 15 min |
| KPI Cards | 10 min |
| Visualizations | 25 min |
| Slicers & Filters | 10 min |
| Polish & Formatting | 15 min |
| **Total** | **~80 min** |
