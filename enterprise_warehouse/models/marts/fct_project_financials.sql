WITH logistics AS (
    SELECT * FROM `enterprise-migration-portfolio.raw_erp_data.Rental_Logistics`
),
financials AS (
    SELECT * FROM `enterprise-migration-portfolio.raw_erp_data.Project_Financials`
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['f.RecordID']) }} AS financial_record_key,
    {{ dbt_utils.generate_surrogate_key(['l.SiteID']) }} AS site_key,
    {{ dbt_utils.generate_surrogate_key(['l.SupplierID']) }} AS supplier_key,
    l.LogisticsID AS logistics_id,
    l.EquipmentType AS equipment_type,
    CAST(l.OrderDate AS DATE) AS order_date,
    l.DeliveryDelayWeeks AS delivery_delay_weeks,
    f.BilledAmount AS billed_amount,
    f.ctd_pct_budget AS cost_to_date_pct_budget
FROM financials f
-- STRICT ARCHITECTURE: INNER JOIN strictly drops orphaned financial 
-- records whose logistics data was quarantined by Great Expectations upstream.
INNER JOIN logistics l 
    ON f.LogisticsID = l.LogisticsID