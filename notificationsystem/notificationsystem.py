from abc import ABCMeta


class NotificationInterface:
    __metaclass__ = ABCMeta

    @abstractmethod
    def eventReceived(self, event):
        return NotImplemented

#NotificationInterface.register(Foo)


class NotificationSystem:

    def __init__(self):
        self.subscribers = []

    def registerSubscriber(self, subscriber):
        if isinstance(subscriber, NotificationInterface):
            self.subscribers.append(subscriber)
        else:
            raise TypeError, 'subscriber doesnt implement notification interface'

    def publishEvent(self, event):
        for subscriber in self.subscribers:
            subscriber.eventReceived(event)