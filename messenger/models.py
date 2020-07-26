from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed


# Create your models here.
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created']


class ThreadManager(models.Manager):

    def find(self, user_one, user_two):
        queryset = self.filter(users=user_one).filter(users=user_two)
        if len(queryset) > 0:
            return queryset[0]
        return None

    def find_or_create(self, user_one, user_two):
        thread = self.find(user_one, user_two)
        if thread is None:
            thread = Thread.objects.create()
            thread.users.add(user_one, user_two)
        return thread


class Thread(models.Model):
    users = models.ManyToManyField(User, related_name='threads')
    messages = models.ManyToManyField(Message)
    updated = models.DateTimeField(auto_now=True)
    objects = ThreadManager()

    class Meta:
        ordering = ['-updated']


def messages_changed(sender, **kwargs):
    instance = kwargs.pop("instance", None)
    action = kwargs.pop("action", None)
    pk_set = kwargs.pop("pk_set", None)
    print(instance, action, pk_set)

    false_pk_set = set()
    if action is "pre_add":
        for msg_pk in pk_set:
            msg = Message.objects.get(pk=msg_pk)
            if msg.user not in instance.users.all():
                print("Upps, ({}) no forma parte del hilo".format(msg.user))
                false_pk_set.add(msg_pk)

    # Se buscarian los mensajes que no son parte del hilo
    pk_set.difference_update(false_pk_set)

    #Force update saving
    instance.save()


m2m_changed.connect(messages_changed, sender=Thread.messages.through)
