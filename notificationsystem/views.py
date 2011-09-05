#!/usr/bin/env python

from gui.decorators import staff_member_required

from notificationsystem.models import *

def subscribe_to_region(request, region):
    pass

@staff_member_required
def check_notifications(request):
    """This method calls out the tasks to send notifications.
    Since it is a cron called view, there is a timeout, so we might want to
    make sure we never get more notifications than we can handle within that
    timeframe.
    """
    notifications = Notification.objects.filter(sent_at=None, send=True).order_by('-created_at')
    
    for notification in notifications:
        # Create the notification queue
        not_key = CHECK_NOTIFICATION_KEY % notification.id
        if memcache.get(not_key, False):
            # This means that we still have a processing task for this host
            # TODO: Check if the amount of retries is too high, and if it is
            #       then create an event to sinalize that there is an issue
            #       with this host.
            logging.critical('Task %s is still processing...' %
                                (CHECK_NOTIFICATION_KEY % notification.id))
            continue
        
        try:
            task_name = 'check_notification_%s_%s' % (notification.id, uuid.uuid4())
            task = taskqueue.add(url='/cron/send_notification_task/%s' % notification.id,
                                 name= task_name, queue_name='cron')
            if task is None:
                logging.critical("!!!! TASK IS NONE! %s " % task_name)
            memcache.set(not_key, task)
            
        except taskqueue.TaskAlreadyExistsError, e:
            logging.info('Task is still running for module %s: %s' % \
                 (module.name,'/cron/create_notification_queue/%s' % notification.id))
    
    return HttpResponse("OK")

@staff_member_required
def send_notification_task(request, notification_id):
    """This task will send out the notifications
    """
    notification = Notification.objects.get(pk=notification_id)
    notification.build_email_data()
    
    sent = send_mail(notification.site_config.notification_sender,
                     notification.site_config.notification_to,
                     bcc=notification.list_emails,
                     reply_to=notification.site_config.notification_reply_to,
                     subject=notification.subject,
                     body=notification.body,
                     html=notification.html)
    
    notification.sent_at = datetime.datetime.now()
    notification.save()
    
    memcache.delete(CHECK_NOTIFICATION_KEY % notification.id)
    return HttpResponse("OK")
