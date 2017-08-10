class VersaoRegistroService(object):

    @staticmethod
    def desativa_versao_registro(model, **query_args):
        registros = model.objects.filter(**query_args)

        if len(registros) > 0:
            for registro in registros:
                registro.set_status("I")
                registro.save()
        return True

    @staticmethod
    def get_versao_registro(model, **query_args):
        registros = model.objects.filter(**query_args).order_by('-data_hora')

        if len(registros) == 1:
            return registros[0]
        else:
            return False
