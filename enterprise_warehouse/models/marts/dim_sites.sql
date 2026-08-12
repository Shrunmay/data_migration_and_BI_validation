SELECT
    {{ dbt_utils.generate_surrogate_key(['site_id']) }} AS site_key,
    site_id,
    project_name,
    region,
    project_status
FROM {{ ref('stg_sites') }}