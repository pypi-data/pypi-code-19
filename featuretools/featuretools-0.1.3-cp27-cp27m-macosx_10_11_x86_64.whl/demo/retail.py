import featuretools as ft


def load_retail(id='demo_retail_data', nrows=None):
    '''
    Returns the retail entityset example

    Args:
        id (str):  id to assign to EntitySet
        nrows (int):  number of rows to load of item_purchases
            entity. If None, load all.

    Examples:

        .. ipython::
            :verbatim:

            In [1]: import featuretools as ft

            In [2]: es = ft.demo.load_retail()

            In [3]: es
            Out[3]:
            Entityset: demo_retail_data
              Entities:
                invoices (shape = [25900, 3])
                items (shape = [4070, 3])
                customers (shape = [4373, 3])
                item_purchases (shape = [541909, 6])

        Load in subset of data

        .. ipython::
            :verbatim:

            In [2]: es = ft.demo.load_retail(nrows=1000)

            In [3]: es
            Out[3]:
            Entityset: demo_retail_data
              Entities:
                invoices (shape = [66, 3])
                items (shape = [590, 3])
                customers (shape = [49, 3])
                item_purchases (shape = [1000, 6])

    '''
    es = ft.EntitySet(id)
    csv = "s3://featuretools-static/uk_online_retail.csv"
    es.entity_from_csv("item_purchases",
                       csv_path=csv,
                       id_variable="item_purchase_id",
                       make_id_variable=True,
                       time_index="InvoiceDate",
                       nrows=nrows,
                       parse_date_cols=["InvoiceDate"])

    es.normalize_entity(new_entity_id="items",
                        base_entity_id="item_purchases",
                        id_variable="StockCode",
                        additional_variables=["Description"])

    es.normalize_entity(new_entity_id="invoices",
                        base_entity_id="item_purchases",
                        id_variable="InvoiceNo",
                        additional_variables=["CustomerID","Country"])

    es.normalize_entity(new_entity_id="customers",
                        base_entity_id="invoices",
                        id_variable="CustomerID",
                        additional_variables=["Country"])


    return es
