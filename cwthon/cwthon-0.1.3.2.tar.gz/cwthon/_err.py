class CwthonError(Exception):
    """
    Cwthon固有のエラーが起きた際にraiseするクラス
    """
    def __init__(self, message):
        self.message = message