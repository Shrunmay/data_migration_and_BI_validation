SELECT
    CAST(SiteID AS INT64) AS site_id,
    CAST(ProjectName AS STRING) AS project_name,
    CAST(Region AS STRING) AS region,
    CAST(Status AS STRING) AS project_status
FROM `enterprise-migration-portfolio.raw_erp_data.Sites`