from django.db.models import Count, Case, When, Avg
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from books.store.permissions import IsOwnerOrStaffOrReadOnly
from .models import Book, UserBookRelation
from .serializers import BooksSerializer, UserBookRelationSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            # rating
            rating=Avg('userbookrelation__rate')
        ).order_by('id')
    serializer_class = BooksSerializer
    # OAuth all users can read
    # permission_classes = [IsAuthenticatedOrReadOnly]
    # add permission
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    # second lesson filtering
    # add search
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['price']
    search_fields = ['name', 'autor_name']
    ordering_fields = ['price', 'autor_name']

# permissions
    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        serializer.save()


class UserBookRelationView(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated] # должен быть авторизованным
    queryset = UserBookRelation.objects.all()
    serializer_class = UserBookRelationSerializer
    # чисто для удобства
    lookup_field = 'book'

    def get_object(self):
        obj, _ = UserBookRelation.objects.get_or_create(user=self.request.user,
                                                        book_id=self.kwargs['book'])
        return obj

# auth
def auth(request):
    return render(request, 'oauth.html')


