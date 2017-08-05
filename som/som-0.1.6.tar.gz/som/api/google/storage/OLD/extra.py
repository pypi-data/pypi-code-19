
def cursor_paging(client):
    # [START cursor_paging]

    def get_one_page_of_tasks(cursor=None):
        query = client.query(kind='Task')
        query_iter = query.fetch(start_cursor=cursor, limit=5)
        page = next(query_iter.pages)

        tasks = list(page)
        next_cursor = query_iter.next_page_token

        return tasks, next_cursor
    # [END cursor_paging]

    page_one, cursor_one = get_one_page_of_tasks()
    page_two, cursor_two = get_one_page_of_tasks(cursor=cursor_one)
    return page_one, cursor_one, page_two, cursor_two





def transactional_single_entity_group_read_only(client):
    client.put_multi([
        datastore.Entity(key=client.key('TaskList', 'default')),
        datastore.Entity(key=client.key('TaskList', 'default', 'Task', 1))
    ])

    # [START transactional_single_entity_group_read_only]
    with client.transaction():
        task_list_key = client.key('TaskList', 'default')

        task_list = client.get(task_list_key)

        query = client.query(kind='Task', ancestor=task_list_key)
        tasks_in_list = list(query.fetch())

        return task_list, tasks_in_list
    # [END transactional_single_entity_group_read_only]


def namespace_run_query(client):
    # Create an entity in another namespace.
    task = datastore.Entity(
        client.key('Task', 'sample-task', namespace='google'))
    client.put(task)

    # [START namespace_run_query]
    # All namespaces
    query = client.query(kind='__namespace__')
    query.keys_only()

    all_namespaces = [entity.key.id_or_name for entity in query.fetch()]

    # Filtered namespaces
    start_namespace = client.key('__namespace__', 'g')
    end_namespace = client.key('__namespace__', 'h')
    query = client.query(kind='__namespace__')
    query.key_filter(start_namespace, '>=')
    query.key_filter(end_namespace, '<')

    filtered_namespaces = [entity.key.id_or_name for entity in query.fetch()]
    # [END namespace_run_query]

    return all_namespaces, filtered_namespaces




def property_run_query(client):
    # Create the entity that we're going to query.
    upsert(client)

    # [START property_run_query]
    query = client.query(kind='__property__')
    query.keys_only()

    properties_by_kind = defaultdict(list)

    for entity in query.fetch():
        kind = entity.key.parent.name
        property_ = entity.key.name

        properties_by_kind[kind].append(property_)
    # [END property_run_query]

    return properties_by_kind


def property_by_kind_run_query(client):
    # Create the entity that we're going to query.
    upsert(client)

    # [START property_by_kind_run_query]
    ancestor = client.key('__kind__', 'Task')
    query = client.query(kind='__property__', ancestor=ancestor)

    representations_by_property = {}

    for entity in query.fetch():
        property_name = entity.key.name
        property_types = entity['property_representation']

        representations_by_property[property_name] = property_types
    # [END property_by_kind_run_query]

    return representations_by_property


def eventual_consistent_query(client):
    # [START eventual_consistent_query]
    # Read consistency cannot be specified in google-cloud-python.
    # [END eventual_consistent_query]
    pass


def main(project_id):
    client = datastore.Client(project_id)

    for name, function in globals().iteritems():
        if name in ('main', 'defaultdict') or not callable(function):
            continue

        print(name)
        pprint(function(client))
        print('\n-----------------\n')



