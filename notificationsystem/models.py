from django.db import models


class Notification(models.Model):
    """When an event happens, a notification is created.
    When a notification is created, the pre_save signal must go look for
    the relevant NotifyOnEvent instances and save the emails it will need
    to send out.
    """
    created_at = models.DateTimeField(null=True, blank=True, default=None)
    sent_at = models.DateTimeField(null=True, blank=True, default=None)
    send = models.BooleanField(default=True)
    event = models.ForeignKey('events.Event')
    region = models.CharField(null=False, blank=False, max_length=50)
    subject = models.CharField(max_length=400)
    body = models.TextField()
    html = models.TextField()
    emails = models.TextField()
    downtime = models.DecimalField(max_digits=5, decimal_places=2,
                                   default=None, null=True)
    
    @property
    def list_emails(self):
        return [e for e in self.emails.split(',') if e]
    
    def build_email_data(self):
        self.subject = "%s is back!" % target_name
        self.body = render_to_string('notificationsystem/notification_body.txt', context)
        self.html = render_to_string('notificationsystem/notification_body.html', context)
    
    def save(self, *args, **kwargs):
        if not self.id:
            self._retrieve_emails()
        
        super(Notification, self).save(*args, **kwargs)
    
    def _notify_emails(self, region):
        notify = NotifyOnEvent.objects.filter(region=region)
                    
        if notify:
            notify = notify[0]
        else:
            notify = []
        
        return notify

    def _retrieve_emails(self):
        notifications = []
        
        notifications.append(self._notify_emails(self.region))
        
        notification_emails = [n.list_emails for n in notifications if n != []]
        
        emails = []
        for email in itertools.chain(*notification_emails):
            if email not in emails:
                emails.append(email)
        
        self.emails = ','.join(emails)
        
        now = datetime.datetime.now()
        for notification in notifications:
            if notification != []:
                notification.last_notified = now
                notification.save()


class NotifyOnEvent(models.Model):
    '''Aggregation for all users who asked to be notified about an specific
    region
    '''
    created_at = models.DateTimeField(null=True, blank=True, default=None)
    last_notified = models.DateTimeField(null=True, blank=True, default=None)
    region = models.CharField(null=False, blank=False, max_length=50)
    emails = models.TextField()
    
    @property
    def list_emails(self):
        return self.emails.split(',')
    
    def add_email(self, email):
        list_emails = self.list_emails
        if email not in list_emails:
            list_emails.append(email)
            self.emails = ','.join(list_emails)
            return True
        return False
    
    def remove_email(self, email):
        list_emails = self.list_emails
        if email in list_emails:
            list_emails.remove(email)
            self.emails = ','.join(list_emails)
            return True
        return False
    
    @staticmethod
    def can_unsubscribe(email, region):
        instance = NotifyOnEvent.objects.filter(region=region)
        if instance and email in instance.list_emails:
            return True
        return False
    
    @staticmethod
    def subscribe(user, region):
        instance = NotifyOnEvent.objects.filter(region=region)
        if not instance:
            instance = NotifyOnEvent()
        
        list_emails = instance.list_emails
        if email not in list_emails:
            profile = user.profile
            
            subs_ids = profile.list_subscriptions_ids
            subs_ids.append(instance.id)
            profile.subscriptions = ','.join(subs_ids)
            profile.save()
            
            # Adding subscriber's email to NotifyOnEvent instance
            list_emails.append(email)
            instance.emails = ','.join(list_emails)
            instance.save()
        
        return True
    
    @staticmethod
    def unsubscribe(email, region):
        instance = NotifyOnEvent.objects.filter(region=region)
        list_emails = instance.list_emails
        if instance and (email in list_emails):
            # Removing the NotifyOnEvent id from subscriber's instance
            user = User.objects.get(email=email)
            profile = user.profile
            
            subs_ids = profile.list_subscriptions_ids
            subs_ids.remove(instance.id)
            profile.subscriptions = ','.join(subs_ids)
            profile.save()
            
            # Removing subscriber's email from NotifyOnEvent instance
            if len(list_emails) == 1:
                instance.delete()
            else:
                list_emails.remove(email)
                instance.emails = ','.join(list_emails)
                instance.save()
            
            return True
        return False
    
    def __unicode__(self):
        return '%s - %s' % (self.region,
                            'notified on %s' % self.last_notified \
                                if self.last_notified else 'not notified')

