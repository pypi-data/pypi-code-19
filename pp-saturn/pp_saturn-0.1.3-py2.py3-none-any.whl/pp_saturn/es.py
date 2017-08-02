def base_parcel_query_json(organization_id_list, start_date=None, end_date=None, search_string=None):
    q = {
        'query': {
            'bool': {
                "must": [
                    {
                        "has_child" : {
                            "type" : "ParcelOrganization",
                            "query" : {
                                "terms" : {
                                    "organization_id" : organization_id_list
                                }
                            }
                        }
                    },
                ]
            }
        },
    }

    if start_date and end_date:
        q['query']['bool']['must'].append({
            'range': {
                'picked_up_date': {
                    'gte': start_date,
                    'lte': end_date
                }
            }
        })

    if search_string:
        q['query']['bool']['must'].append({
            "bool": {
                "should" : [
                    {'simple_query_string': {
                        "query": search_string,
                        "fields": ['parcel_id', 'parcel_received_by', 'parcel_sub_parcel', 'parcel_to_name_carrier',
                                   'carrier.name', 'last_event.event_type_master_data.display_name']
                    }},
                    {"has_child" : {
                        "type" : "ParcelOrganization",
                        "query" : {
                            'simple_query_string': {
                                "query": search_string,
                                "fields": ['carrier_reference', 'customer_code', 'customer_name', 'customer_add_name', 
                                           'parcel_alias', 'parcel_alias_2', 'parcel_to_name_customer', 'parcel_user_tag',
                                           'parcel_order_code', 'order_tracking_id', 'parcel_to_name_customer', 'parcel_user_tag']
                            },
                        }
                    }}
                ]
            }
        })

    return q
