# Create your views here.
from django.db.models.loading import get_model
from datetime import datetime
from google.appengine.api import datastore
from google.appengine.api.datastore import Put, Delete
from common.batch_db_ops import BatchOperation
from django.http import HttpResponse
from video.models import SOURCE_TYPE_YOUTUBE

class mem(object):
    """Global AppEngine datastore operations counters"""
    put_count = 0
    delete_count = 0


def new_put(entities, **kwargs):
    mem.put_count += 1
    return Put(entities, **kwargs)


def new_delete(keys, **kwargs):
    mem.delete_count += 1
    return Delete(keys, **kwargs)


def batch(request):
    mem.put_count = 0
    mem.delete_count = 0

    datastore.Put = new_put
    datastore.Delete = new_delete

    Post = get_model("video", "Post")
    Video = get_model("video", "Video")

    with BatchOperation() as q:
        videos = []
        posts = []
        how_many = 1000
        for i in xrange(how_many):
            p = Post()
            p.source_type = SOURCE_TYPE_YOUTUBE
            p.description = "Description of post %d" % i
            p.original_id = "j3r4r34_%d" % i
            p.publish_time = datetime.now()
            q.save(p, raw=True)
            posts.append(p)

            v = Video()
            v.source_type = SOURCE_TYPE_YOUTUBE
            v.original_id = "n4kjrn34k_%d" % i
            v.publish_time = datetime.now()
            v.top_post = p
            q.save(v, raw=True)
            videos.append(v)

    return HttpResponse("%d videos & %d posts added, number of actual puts: %d" % (how_many, how_many, mem.put_count))



def batch2(request):
    mem.put_count = 0
    mem.delete_count = 0

    datastore.Put = new_put
    datastore.Delete = new_delete

    Post = get_model("video", "Post")
    Video = get_model("video", "Video")

    q = BatchOperation()
    videos = []
    posts = []
    how_many = 100
    for i in xrange(how_many):
        p = Post()
        p.source_type = SOURCE_TYPE_YOUTUBE
        p.description = "Description of post %d" % i
        p.original_id = "j3r4r34_%d" % i
        p.publish_time = datetime.now()
        q.save(p, raw=True)
        posts.append(p)

        v = Video()
        v.source_type = SOURCE_TYPE_YOUTUBE
        v.original_id = "n4kjrn34k_%d" % i
        v.publish_time = datetime.now()
        v.top_post = p
        q.save(v, raw=True)
#        q.save(v)
        videos.append(v)

    q.flush()

    for i, v in enumerate(videos):
        v.top_post = posts[i]
        q.save(v, raw=True)
#        q.save(v)

    q.flush()
    
    return HttpResponse("Batch v2: no with: %d videos & %d posts added, number of actual puts: %d" % (how_many, how_many, mem.put_count))

