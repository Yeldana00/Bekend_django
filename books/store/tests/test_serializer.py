from unittest import TestCase

from store.models import Book
from store.serializers import BooksSerializer


class BookSerializerTestCase(TestCase):
    def test_ok(self):
        book_1 = Book.objects.create(name='Test book 1', price=1515, autor_name='Yeldana Kenges')
        book_2 = Book.objects.create(name='Test book 2', price=2000, autor_name='Aizat Kenges')
        data = BooksSerializer([book_1, book_2], many=True).data
        expected_data = [
            {
                'id': book_1.id,
                'name': 'Test book 1',
                'price': '1515.00',
                'autor_name': 'Yeldana Kenges'
            },
            {
                'id': book_2.id,
                'name': 'Test book 2',
                'price': '2000.00',
                'autor_name': 'Aizat Kenges'
            },
        ]
        self.assertEqual(expected_data, data)
