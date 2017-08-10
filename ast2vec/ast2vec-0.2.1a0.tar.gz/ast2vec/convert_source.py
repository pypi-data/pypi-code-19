import sys

import asdf
from bblfsh.github.com.bblfsh.sdk.protocol.generated_pb2 import ParseResponse
from modelforge import merge_strings

model = asdf.open(sys.argv[1])
model.tree["uasts"] = merge_strings([
    ParseResponse.FromString(i).uast.SerializeToString() for i in model.tree["uasts"]])
model.write_to(sys.argv[1])
