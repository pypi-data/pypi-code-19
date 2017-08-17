import pandas as pd

def load_mock_customer():
    """Return dataframes of mock customer data"""

    customers_df = pd.DataFrame({"id": [1, 2],
                             "zip_code": ["60091", "02139"]})

    sessions_df = pd.DataFrame({"id": [1, 2, 3],
                                "customer_id": [1, 2, 1],
                                "session_start": [pd.Timestamp("2017-02-22"),
                                                  pd.Timestamp("2016-12-22"),
                                                  pd.Timestamp("2017-01-12")],
                                "session_duration":[12.3, 33, 43]})

    transactions_df = pd.DataFrame({"id": [1, 2, 3, 4, 5, 6],
                                    "session_id": [1, 2, 1, 3, 4, 5],
                                    "product_id": [1, 2, 1, 2, 3, 1],
                                    "amount": [100.40, 20.63, 33.32, 13.12, 67.22, 1.00],
                                    "transaction_time": pd.date_range(start="10:00", periods=6, freq="10s")})

    products_df = pd.DataFrame({"id": [1, 2, 3],
                                "brand": ["a", "b", "a"]})

    return {"customers": customers_df,
            "sessions": sessions_df,
            "transactions": transactions_df,
            "products": products_df}
