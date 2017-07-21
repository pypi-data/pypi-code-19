from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from api.models import Snippet
from api.serializers import SnippetSerializer, UserSerializer
# APIView modules
from rest_framework.views import APIView
from django.http import Http404
#-----
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.contrib.auth.models import User
from rest_framework import generics
from api.permissions import IsOwnerOrReadOnly
# from django.shortcuts import render
#from django.http import HttpResponse, JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework.renderers import JSONRenderer
# from rest_framework.parsers import JSONParser

# Create your views here

# class based views


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

#-----

class SnippetList(generics.ListCreateAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class SnippetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                                IsOwnerOrReadOnly,)


#--- class bases biew
# class SnippetList(APIView):
#     """
#     List Classes
#     """
#     authentication_classes = (SessionAuthentication, BasicAuthentication)
#     permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
#
#     def get(self, request, format=None):
#         serializer = SnippetSerializer(Snippet.objects.all(), many=True)
#         return Response(serializer.data)
#
#     def post(self, request, format=None):
#         serializer = SnippetSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)

# class SnippetDetail(APIView):
#     """
#     details
#     """
#
#     permission_classes = (permissions.IsAuthenticatedOrReadOnly,
#                             IsOwnerOrReadOnly,)
#
#     def get_object(self, pk):
#         try:
#             return Snippet.objects.get(id=pk)
#         except Snippet.DoesNotExist:
#             raise Http404
#
#     def get(self, request, pk, format=None):
#         snippet = self.get_object(pk)
#         serializer = SnippetSerializer(snippet)
#         return Response(serializer.data)
#
#     def delete(self, request, pk, format=None):
#         snippet = self.get_object(pk)
#         snippet.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
#
#     def put(self, request, pk, format=None):
#         snippet = self.get_object(pk)
#         serializer = SnippetSerializer(snippet, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#-----------------
# @api_view(['GET', 'POST'])
# def snippet_list(request, format=None):
#     """
#     get list
#     """
#     if request.method == "GET":
#           serializer = SnippetSerializer(Snippet.objects.all(), many=True)
#           return Response(serializer.data)
#
#     elif request.method == "POST":
#         serializer = SnippetSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['GET', 'PUT', 'DELETE'])
# def snippet_detail(request, pk, formt=None):
#     """
#     get details
#     """
#     try:
#         snippet = Snippet.objects.get(id=pk)
#     except Snippet.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#         # return HttpResponse(status=404)
#
#
#     if request.method == "GET":
#         serializer = SnippetSerializer(snippet)
#         return Response(serializer.data)
#
#     elif request.method == "PUT":
#         serializer = SnippetSerializer(snippet, request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     elif request.method == "DELETE":
#         snippet.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

    #-----------------

# @csrf_exempt
# def snippet_list(request):
#     """
#     List all snippets
#     """
#     if request.method == "GET":
#         serializer = SnippetSerializer(Snippet.objects.all(), many=True)
#         # content = JSONRenderer().render(serializer.data)
#         return JsonResponse(serializer.data, safe=False)
#
#     elif request.method == "POST":
#         data = JSONParser().parse(request)
#         serializer = SnippetSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data, status=201)
#         return JsonResponse(serializer.errors, status=400)
#
#
# @csrf_exempt
# def snippet_detail(request, pk):
#     """
#     retrive snippet
#     """
#     try:
#         snippet = Snippet.objects.get(id=pk)
#     except Snippet.DoesNotExist:
#         return HttpResponse(status=404)
#
#     if request.method=="GET":
#         serializer = SnippetSerializer(snippet)
#         # content = JSONRenderer().render(serializer.data)
#         return JsonResponse(serializer.data)
#
#     elif request.method=="PUT":
#         data = JSONParser().parse(request)
#         serializer = SnippetSerializer(snippet, data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data)
#         return JsonResponse(serializer.errors, status=400)
#
#     elif request.method=="DELETE":
#         snippet.delete()
#         return HttpResponse(status=204)
