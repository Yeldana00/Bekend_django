from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet
from .models import Book
from .serializers import BooksSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BooksSerializer
    # OAuth all users can read
    permission_classes = [IsAuthenticatedOrReadOnly]
    # second lesson filtering
    # add search
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['price']
    search_fields = ['name', 'autor_name']
    ordering_fields = ['price', 'autor_name']


def auth(request):
    return render(request, 'oauth.html')


