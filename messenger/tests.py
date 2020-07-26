from django.test import TestCase
from django.contrib.auth.models import User
from .models import Thread, Message


# Create your tests here.
class ThreadTestCase(TestCase):

    def setUp(self) -> None:
        self.user_one = User.objects.create_user('user1', None, 'test1321')
        self.user_two = User.objects.create_user('user2', None, 'test1321')
        self.user_three = User.objects.create_user('user3', None, 'test1321')

        self.thread = Thread.objects.create()

    def test_users_to_thread(self):
        self.thread.users.add(self.user_one, self.user_two)
        self.assertEqual(len(self.thread.users.all()), 2)

    def test_filter_thread_by_users(self):
        self.thread.users.add(self.user_one, self.user_two)
        threads = Thread.objects.filter(users=self.user_one).filter(users=self.user_two)
        self.assertEqual(self.thread, threads[0])

    def test_filter_non_existent_thread(self):
        threads = Thread.objects.filter(users=self.user_one).filter(users=self.user_two)
        self.assertEqual(len(threads), 0)

    def test_add_messages_to_thread(self):
        self.thread.users.add(self.user_one, self.user_two)
        message_one = Message.objects.create(user=self.user_one, content="Buenas")
        message_two = Message.objects.create(user=self.user_two, content="Hola")
        self.thread.messages.add(message_one, message_two)
        self.assertEqual(len(self.thread.messages.all()), 2)

        for message in self.thread.messages.all():
            print("({}): {}".format(message.user, message.content))

    def test_add_message_from_user_not_in_thread(self):
        self.thread.users.add(self.user_one, self.user_two)
        message_one = Message.objects.create(user=self.user_one, content="Buenas")
        message_two = Message.objects.create(user=self.user_two, content="Hola")
        message_three = Message.objects.create(user=self.user_three, content="Holi")
        self.thread.messages.add(message_one, message_two, message_three)
        self.assertEqual(len(self.thread.messages.all()), 2)

    def test_find_thread_with_custom_manager(self):
        self.thread.users.add(self.user_one, self.user_two)
        thread = Thread.objects.find(self.user_one, self.user_two)
        self.assertEqual(self.thread, thread)

    def test_find_or_create_thread_with_custom_manager(self):
        self.thread.users.add(self.user_one, self.user_two)
        thread = Thread.objects.find_or_create(self.user_one, self.user_two)
        self.assertEqual(self.thread, thread)
        thread = Thread.objects.find_or_create(self.user_one, self.user_three)
        self.assertIsNotNone(thread)
