

class CustomIDGenerator(object):

    def __init__(self, custom_id_collection):
        self._custom_id_collection = custom_id_collection

    async def generate(self, collection_name):
        custom_id = (await self._custom_id_collection.find_and_modify(
            query={'_id': collection_name},
            update={'$inc': {'custom_id': 1}},
            upsert=True,
            new=True
        )).get('custom_id', 0)

        return custom_id