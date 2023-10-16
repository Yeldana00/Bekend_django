import json

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BooksSerializer


class BooksApiTestCase(APITestCase):

    def setUp(self):
        # create user
        self.user = User.objects.create(username='test_username')
        self.book_1 = Book.objects.create(name='Test book 1', price=1515.00, autor_name='Yeldana Kenges',
                                          owner=self.user)
        self.book_2 = Book.objects.create(name='Yeldana book', price=1515.00, autor_name='Aizat Kenges')
        self.book_3 = Book.objects.create(name='Test book 2', price=1000.00, autor_name='Alikhan Serikuly')

    def test_get(self):
        url = reverse('book-list')
        response = self.client.get(url)
        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            # rating
            rating=Avg('userbookrelation__rate')
        ).order_by('id')
        serializer_data = BooksSerializer(books, many=True).data
        # without annotate
        # serializer_data = BooksSerializer([self.book_1, self.book_2, self.book_3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)


# Filter Search Order
    def test_get_filter(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'price': 1515.00})
        books = Book.objects.filter(id__in=[self.book_1.id, self.book_2.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            # rating
            rating=Avg('userbookrelation__rate')
        ).order_by('id')
        serializer_data = BooksSerializer(books, many=True).data
        # without annotate
        # serializer_data = BooksSerializer([self.book_2, self.book_3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'search': 'Yeldana'})
        books = Book.objects.filter(id__in=[self.book_1.id, self.book_2.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            # rating
            rating=Avg('userbookrelation__rate')
        ).order_by('id')
        serializer_data = BooksSerializer(books, many=True).data
        # without annotate
        # serializer_data = BooksSerializer([self.book_1, self.book_2], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_ordering(self):
        url = reverse('book-list')
        response = self.client.get(url, data={'ordering': 'autor_name'})
        books = Book.objects.filter(id__in=[self.book_2.id,self.book_3.id, self.book_1.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            # rating
            rating=Avg('userbookrelation__rate')
        ).order_by('id')
        serializer_data = BooksSerializer(books, many=True).data
        # without annotate
        # serializer_data = BooksSerializer([self.book_2, self.book_3, self.book_1], many=True).data
        print(response.data)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

# CRUD
    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse('book-list')
        data = {
                    "name": "Python 3",
                    "price": "3500.00",
                    "autor_name": "Azat Yaakov"
                }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.post(url, data=json_data,
                                    content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        print(Book.objects.all().count())
        # check count books
        self.assertEqual(4, Book.objects.all().count())
        # permissions
        self.assertEqual(self.user, Book.objects.last().owner)

    def test_update(self):
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
                    "name": self.book_1.name,
                    "price": 3000.00,
                    "autor_name": self.book_1.autor_name
                }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(3000, self.book_1.price)


# Permissions
    def test_update_not_owner(self):
        self.user2 = User.objects.create(username='test_username2')
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
                "name": self.book_1.name,
                "price": 3000.00,
                "autor_name": self.book_1.autor_name
            }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(1515, self.book_1.price)

    def test_update_not_owner_but_staff(self):
        self.user2 = User.objects.create(username='test_username2',
                                         is_staff=True)
        url = reverse('book-detail', args=(self.book_1.id,))
        data = {
                "name": self.book_1.name,
                "price": 3000.00,
                "autor_name": self.book_1.autor_name
            }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.book_1.refresh_from_db()
        self.assertEqual(3000, self.book_1.price)


# Testing like and bookmarks
class BooksRelationTestCase(APITestCase):

    def setUp(self):
        # create user
        self.user = User.objects.create(username='test_username')
        self.user2 = User.objects.create(username='test_username2')
        self.book_1 = Book.objects.create(name='Test book 1', price=1515.00, autor_name='Yeldana Kenges',
                                          owner=self.user)
        self.book_2 = Book.objects.create(name='Yeldana book', price=1000.00, autor_name='Aizat Kenges')
        self.book_3 = Book.objects.create(name='Test book 2', price=1000.00, autor_name='Alikhan Serikuly')

    def test_like(self):
        # patch edit one feature
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {
                "like": True
            }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.like)

        # bookmarks
        data = {
                "in_bookmarks": True
            }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertTrue(relation.in_bookmarks)

# rating
    def test_rate(self):
        # patch edit one feature
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {
                "rate": 3
            }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(user=self.user,
                                                book=self.book_1)
        self.assertEqual(3, relation.rate)


    def test_rate_wrong(self):
        # patch edit one feature
        url = reverse('userbookrelation-detail', args=(self.book_1.id,))

        data = {
                "rate": 6
            }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
        response = self.client.patch(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)
#        relation = UserBookRelation.objects.get(user=self.user,
#                                               book=self.book_1)
#        self.assertEqual(3, relation.rate)
