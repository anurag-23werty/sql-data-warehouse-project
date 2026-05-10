import os
from pathlib import Path
from datetime import datetime

import psycopg2
from dotenv import load_dotenv


# =========================
# Load environment variables
# =========================
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


# =========================
# File mapping
# =========================
BASE_DIR = Path(__file__).resolve().parent

FILES = [
    (
        BASE_DIR / "datasets/source_crm/cust_info.csv",
        "bronze.crm_cust_info"
    ),
    (
        BASE_DIR / "datasets/source_crm/prd_info.csv",
        "bronze.crm_prd_info"
    ),
    (
        BASE_DIR / "datasets/source_crm/sales_details.csv",
        "bronze.crm_sales_details"
    ),
    (
        BASE_DIR / "datasets/source_erp/CUST_AZ12.csv",
        "bronze.erp_cust_az12"
    ),
    (
        BASE_DIR / "datasets/source_erp/LOC_A101.csv",
        "bronze.erp_loc_a101"
    ),
    (
        BASE_DIR / "datasets/source_erp/PX_CAT_G1V2.csv",
        "bronze.erp_px_cat_g1v2"
    ),
]


# =========================
# Logging helper
# =========================
def log_etl(cur, process_name, table_name, status,
            rows_loaded=None, error_message=None):

    cur.execute("""
        INSERT INTO public.etl_log
        (
            process_name,
            table_name,
            end_time,
            status,
            rows_loaded,
            error_message
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        process_name,
        table_name,
        datetime.now(),
        status,
        rows_loaded,
        error_message
    ))


# =========================
# Main loader
# =========================
def load_bronze():

    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False

    cur = conn.cursor()

    try:
        for file_path, table_name in FILES:

            print(f"\nLoading -> {table_name}")

            try:
                # truncate table
                cur.execute(f"TRUNCATE TABLE {table_name};")

                # copy csv
                with open(file_path, "r", encoding="utf-8") as f:
                    cur.copy_expert(
                        f"""
                        COPY {table_name}
                        FROM STDIN
                        WITH (
                            FORMAT CSV,
                            HEADER TRUE
                        )
                        """,
                        f
                    )

                # count rows
                cur.execute(f"SELECT COUNT(*) FROM {table_name};")
                row_count = cur.fetchone()[0]

                # log success
                log_etl(
                    cur,
                    "bronze_load",
                    table_name,
                    "success",
                    row_count,
                    None
                )

                conn.commit()

                print(f"✓ Loaded {row_count} rows")

            except Exception as e:
                conn.rollback()

                log_etl(
                    cur,
                    "bronze_load",
                    table_name,
                    "failed",
                    None,
                    str(e)
                )

                conn.commit()

                print(f"✗ Failed: {e}")

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    load_bronze()
# if permission is given by OS:(decomment it)
# CREATE OR REPLACE PROCEDURE load_bronze()
# LANGUAGE plpgsql
# AS $$
# BEGIN
#     -- =========================
#     -- CRM CUSTOMER INFO
#     -- =========================
#     TRUNCATE TABLE bronze.crm_cust_info;

#     COPY bronze.crm_cust_info
#     FROM '/Users/anurag_77y/anaconda_projects/sql-data-warehouse-project/datasets/source_crm/cust_info.csv'
#     DELIMITER ','
#     CSV HEADER;

#     RAISE NOTICE 'crm_cust_info loaded';


#     -- =========================
#     -- CRM PRODUCT INFO
#     -- =========================
#     TRUNCATE TABLE bronze.crm_prd_info;

#     COPY bronze.crm_prd_info
#     FROM '/Users/anurag_77y/anaconda_projects/sql-data-warehouse-project/datasets/source_crm/prd_info.csv'
#     DELIMITER ','
#     CSV HEADER;

#     RAISE NOTICE 'crm_prd_info loaded';


#     -- =========================
#     -- CRM SALES DETAILS
#     -- =========================
#     TRUNCATE TABLE bronze.crm_sales_details;

#     COPY bronze.crm_sales_details
#     FROM '/Users/anurag_77y/anaconda_projects/sql-data-warehouse-project/datasets/source_crm/sales_details.csv'
#     DELIMITER ','
#     CSV HEADER;

#     RAISE NOTICE 'crm_sales_details loaded';


#     -- =========================
#     -- ERP CUSTOMER
#     -- =========================
#     TRUNCATE TABLE bronze.erp_cust_az12;

#     COPY bronze.erp_cust_az12
#     FROM '/Users/anurag_77y/anaconda_projects/sql-data-warehouse-project/datasets/source_erp/CUST_AZ12.csv'
#     DELIMITER ','
#     CSV HEADER;

#     RAISE NOTICE 'erp_cust_az12 loaded';


#     -- =========================
#     -- ERP LOCATION
#     -- =========================
#     TRUNCATE TABLE bronze.erp_loc_a101;

#     COPY bronze.erp_loc_a101
#     FROM '/Users/anurag_77y/anaconda_projects/sql-data-warehouse-project/datasets/source_erp/LOC_A101.csv'
#     DELIMITER ','
#     CSV HEADER;

#     RAISE NOTICE 'erp_loc_a101 loaded';


#     -- =========================
#     -- ERP PRODUCT CATEGORY
#     -- =========================
#     TRUNCATE TABLE bronze.erp_px_cat_g1v2;

#     COPY bronze.erp_px_cat_g1v2
#     FROM '/Users/anurag_77y/anaconda_projects/sql-data-warehouse-project/datasets/source_erp/PX_CAT_G1V2.csv'
#     DELIMITER ','
#     CSV HEADER;

#     RAISE NOTICE 'erp_px_cat_g1v2 loaded';


#     RAISE NOTICE 'Bronze layer fully loaded';

# END;
# $$;
