def transform_mlc_resource(result_tuple):
    result, verb = result_tuple
    if result is None:
        return result
    if verb:
        return result
    return {
        'Subscription': result.id.split('/')[2],
        'Resource Group': result.id.split('/')[4],
        'Cluster Name': result.name,
        'Created On': result.created_on,
        'Provisioning State': result.provisioning_state,
        'Location': result.location,
        'Cluster Size': result.container_service.agent_count
        # ''
    }


def transform_mlc_resource_list(result):
    return [transform_mlc_resource((obj, False)) for obj in result]

