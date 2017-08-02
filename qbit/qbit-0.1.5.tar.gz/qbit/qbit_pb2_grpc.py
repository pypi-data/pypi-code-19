import grpc
from grpc.framework.common import cardinality
from grpc.framework.interfaces.face import utilities as face_utilities

import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import qbit_pb2 as qbit__pb2
import google.protobuf.empty_pb2 as google_dot_protobuf_dot_empty__pb2
import qbit_pb2 as qbit__pb2
import google.protobuf.empty_pb2 as google_dot_protobuf_dot_empty__pb2
import qbit_pb2 as qbit__pb2
import google.protobuf.empty_pb2 as google_dot_protobuf_dot_empty__pb2


class QbitStub(object):

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.CompareMolecule = channel.unary_unary(
        '/qbit.services.Qbit/CompareMolecule',
        request_serializer=qbit__pb2.CompareRequest.SerializeToString,
        response_deserializer=qbit__pb2.ComparisonResult.FromString,
        )
    self.Hobo2Qubo = channel.unary_unary(
        '/qbit.services.Qbit/Hobo2Qubo',
        request_serializer=qbit__pb2.BinaryPolynomial.SerializeToString,
        response_deserializer=qbit__pb2.BinaryPolynomial.FromString,
        )
    self.SolveQubo = channel.unary_unary(
        '/qbit.services.Qbit/SolveQubo',
        request_serializer=qbit__pb2.QuboRequest.SerializeToString,
        response_deserializer=qbit__pb2.QuboResponse.FromString,
        )
    self.ListOperations = channel.unary_unary(
        '/qbit.services.Qbit/ListOperations',
        request_serializer=qbit__pb2.ListOperationsRequest.SerializeToString,
        response_deserializer=qbit__pb2.ListOperationsResponse.FromString,
        )
    self.GetOperation = channel.unary_unary(
        '/qbit.services.Qbit/GetOperation',
        request_serializer=qbit__pb2.GetOperationRequest.SerializeToString,
        response_deserializer=qbit__pb2.Operation.FromString,
        )
    self.GetOperationToWorkOn = channel.unary_unary(
        '/qbit.services.Qbit/GetOperationToWorkOn',
        request_serializer=qbit__pb2.GetOperationToWorkOnRequest.SerializeToString,
        response_deserializer=qbit__pb2.Operation.FromString,
        )
    self.CancelOperation = channel.unary_unary(
        '/qbit.services.Qbit/CancelOperation',
        request_serializer=qbit__pb2.CancelOperationRequest.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
    self.CompleteOperation = channel.unary_unary(
        '/qbit.services.Qbit/CompleteOperation',
        request_serializer=qbit__pb2.CompleteOperationRequest.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )
    self.ErrorOperation = channel.unary_unary(
        '/qbit.services.Qbit/ErrorOperation',
        request_serializer=qbit__pb2.ErrorOperationRequest.SerializeToString,
        response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
        )


class QbitServicer(object):

  def CompareMolecule(self, request, context):
    """Compare moleculer similarity.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def Hobo2Qubo(self, request, context):
    """Converts HOBO to a QUBO representation.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def SolveQubo(self, request, context):
    """Supports SQA, Tabu, Fujitsu, PTICM, PathRelinking, MultiTabu solvers.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ListOperations(self, request, context):
    """rpc Quadprog(QuadprogRequest) returns (QuadprogResponse) {};
    rpc AsyncQuadprog(QuadprogRequest) returns (Operation) {};
    rpc AsyncLpProblem(LpProblemRequest) returns (Operation) {};

    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetOperation(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetOperationToWorkOn(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def CancelOperation(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def CompleteOperation(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def ErrorOperation(self, request, context):
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_QbitServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'CompareMolecule': grpc.unary_unary_rpc_method_handler(
          servicer.CompareMolecule,
          request_deserializer=qbit__pb2.CompareRequest.FromString,
          response_serializer=qbit__pb2.ComparisonResult.SerializeToString,
      ),
      'Hobo2Qubo': grpc.unary_unary_rpc_method_handler(
          servicer.Hobo2Qubo,
          request_deserializer=qbit__pb2.BinaryPolynomial.FromString,
          response_serializer=qbit__pb2.BinaryPolynomial.SerializeToString,
      ),
      'SolveQubo': grpc.unary_unary_rpc_method_handler(
          servicer.SolveQubo,
          request_deserializer=qbit__pb2.QuboRequest.FromString,
          response_serializer=qbit__pb2.QuboResponse.SerializeToString,
      ),
      'ListOperations': grpc.unary_unary_rpc_method_handler(
          servicer.ListOperations,
          request_deserializer=qbit__pb2.ListOperationsRequest.FromString,
          response_serializer=qbit__pb2.ListOperationsResponse.SerializeToString,
      ),
      'GetOperation': grpc.unary_unary_rpc_method_handler(
          servicer.GetOperation,
          request_deserializer=qbit__pb2.GetOperationRequest.FromString,
          response_serializer=qbit__pb2.Operation.SerializeToString,
      ),
      'GetOperationToWorkOn': grpc.unary_unary_rpc_method_handler(
          servicer.GetOperationToWorkOn,
          request_deserializer=qbit__pb2.GetOperationToWorkOnRequest.FromString,
          response_serializer=qbit__pb2.Operation.SerializeToString,
      ),
      'CancelOperation': grpc.unary_unary_rpc_method_handler(
          servicer.CancelOperation,
          request_deserializer=qbit__pb2.CancelOperationRequest.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
      'CompleteOperation': grpc.unary_unary_rpc_method_handler(
          servicer.CompleteOperation,
          request_deserializer=qbit__pb2.CompleteOperationRequest.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
      'ErrorOperation': grpc.unary_unary_rpc_method_handler(
          servicer.ErrorOperation,
          request_deserializer=qbit__pb2.ErrorOperationRequest.FromString,
          response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'qbit.services.Qbit', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
