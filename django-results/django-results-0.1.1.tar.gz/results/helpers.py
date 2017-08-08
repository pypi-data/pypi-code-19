from django.apps import apps


def get_does_not_exist_model(e):
    # 从ObjectDoesNotExist错误中查出找不到的model类型
    for model in apps.get_models():
        if model.DoesNotExist == e.__class__:
            return model
    return None
