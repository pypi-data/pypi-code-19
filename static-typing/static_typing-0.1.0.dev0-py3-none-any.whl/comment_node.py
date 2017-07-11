
import typing as t

import typed_ast.ast3

class Comment(typed_ast.ast3.Expr):

    def __init__(self, comment: t.Union[typed_ast.ast3.AST, str]):
        if isinstance(comment, str):
            comment=typed_ast.ast3.Str(s=comment)
        super().__init__(value=comment)
