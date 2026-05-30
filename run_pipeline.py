from extraction.customers_extractor import (
    fetch_all_customers,
    save_customers
)

print("Starting Enterprise ETL Pipeline")


def run_pipeline():

    # Customers Extraction
    customers = fetch_all_customers()

    save_customers(customers)

    print("Customers Extraction Completed")

    # Charges Extraction
    import extraction.charges_extractor

    print("Charges Extraction Completed")

    # Payments Extraction
    import extraction.payments_extractor

    print("Payments Extraction Completed")

    print("Pipeline Completed Successfully")


if __name__ == "__main__":

    run_pipeline()