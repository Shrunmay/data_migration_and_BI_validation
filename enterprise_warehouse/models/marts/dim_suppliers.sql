SELECT
    {{ dbt_utils.generate_surrogate_key(['supplier_id']) }} AS supplier_key,
    supplier_id,
    vendor_name,
    supplier_risk_score
FROM {{ ref('stg_suppliers') }}