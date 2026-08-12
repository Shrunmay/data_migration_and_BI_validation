SELECT
    CAST(SupplierID AS INT64) AS supplier_id,
    CAST(VendorName AS STRING) AS vendor_name,
    CAST(BaseRiskScore AS FLOAT64) AS supplier_risk_score
FROM `enterprise-migration-portfolio.raw_erp_data.Suppliers`