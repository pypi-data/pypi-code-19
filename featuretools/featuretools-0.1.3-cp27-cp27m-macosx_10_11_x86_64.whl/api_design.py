import pandas as pd
from featuretools import dfs
# {
#   entity_id: (entity_dataframe, id_variable, time_index),
#   entity_id_2: (entity_dataframe_2, id_variable_2, time_index_2),
# }
#

cards_df = pd.DataFrame({"id": [1, 2, 3]})
transactions_df = pd.DataFrame({"id": [1, 2, 3, 4, 5, 6],
                                "card_id": [1, 2, 1, 3, 4, 5],
                                "transaction_time": [10, 12, 15, 20, 21, 20],
                                "fraud": [True, False, True, False, True, True]})
entities = {
        "cards" : (card_df, "id"),
        "transactions" : (transactions_df, "id", "transaction_time")
}


#
#[(parent_entity_id, parent_variable_id, child_entity_id, child_variable_id),
#   ...]
#
relationships = [("cards", "id", "transactions", "card_id")]


# make features for 3 cards at the corresponding times
calc_time_df = pd.DataFrame({"instance_id": [1, 2, 3],
                             "time": [10, 12, 15]})



#
#  API ideas for actually calling dfs
#



# cutoff times per instance
feature_matrix, features = dfs(entities=e_sampled,
                               relationships=relationships,
                               prediction_entitiy="transactions",
                               cutoff_time=cutoff_times_df)

# same cutoff every intance
feature_matrix, features = dfs(entities=e_sampled,
                               relationships=relationships,
                               prediction_entitiy="transactions",
                               instance_ids=[1,2,3],
                               cutoff_time="2017-04-29")

# cutoff time is now
feature_matrix, features = dfs(entities=e_sampled,
                               relationships=relationships,
                               prediction_entitiy="transactions",
                               instance_ids=[1,2,3])


## all parameteres
feature_matrix, features = dfs(entities=e_sampled,
                               relationships=relationships,
                               prediction_entitiy="transactions",
                               cutoff_time=cutoff_times_df,
                               agg_primitives=[],
                               trans_primitives=[],
                               max_depth=2,
                               allowed_paths=None,
                               ignore_entities=None,
                               ignore_variables=None,
                               seed_features=None)


# e_sampled = ft.our_basic_sampler(entities, relationships, n=100, entitiy= "cards")
#
