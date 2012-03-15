import logging
from django.db.utils import DEFAULT_DB_ALIAS
from django.db import connections
from django.utils.importlib import import_module

class BatchPool(object):
    def __init__(self, size, batch_size):
        self.max_size = size
        self.max_batch_size = batch_size

        self.reset()

    def reset(self):
        self.pool = []
        self.pool_size = 0
        self.batches_sizes = []

    def append(self, instance, raw=False):
        if raw:
            groups = []
        else:
            groups = instance.get_parents_cascade()
        groups.append({instance.__class__: None})

        for idx, group in enumerate(groups):
            try:
                self.pool[idx]
            except IndexError:
                self.pool.append([])
                self.batches_sizes.append(0)

            for cls, field in group.items():
                self.pool[idx].append((instance, cls, field, raw))

            group_len = len(group)
            self.pool_size += group_len
            self.batches_sizes[idx] += group_len

    def is_full(self):
        if self.pool_size >= self.max_size:
            return True
        for batch_size in self.batches_sizes:
            if batch_size >= self.max_batch_size:
                return True
        return False

    def reverse(self):
        self.pool.reverse()

    def __iter__(self):
        return iter(self.pool)

class BatchQueryStub(object):
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def save(self, instance, **kwargs):
        instance.save(**kwargs)

    def delete(self, instance, **kwargs):
        instance.delete(**kwargs)

    def flush(self):
        pass

class BatchQuery(object):
    compiler = 'SQLBatchCompiler'

    def __init__(self, pool_size=None, batch_size=None,
                 save_pool_size=None, save_batch_size=None,
                 delete_pool_size=None, delete_batch_size=None,
                 using=DEFAULT_DB_ALIAS, **kwargs):
        self.using = using
        self.connection = connections[using]
#        self.compiler = self.connection.ops.compiler(self.compiler)(self, self.connection, using,
#                                                                    **kwargs)
        self.compiler = getattr(
                import_module("common.batch_db_ops"), 'SQLBatchCompiler'
            )(self, self.connection, using)
        pool_size = pool_size or 500
        batch_size = batch_size or 500

#        pool_size = pool_size or self.connection.features.batch_pool_size
#        batch_size = batch_size or self.connection.features.batch_size

        save_pool_size = save_pool_size or pool_size
        save_batch_size = save_batch_size or batch_size
        self.save_pool = BatchPool(size=save_pool_size, batch_size=save_batch_size)

        delete_pool_size = delete_pool_size or pool_size
        delete_batch_size = delete_batch_size or batch_size
        self.delete_pool = BatchPool(size=delete_pool_size, batch_size=delete_batch_size)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.flush()

    def save(self, instance, using=None, raw=False, **kwargs):
#        instance.pre_save(instance.__class__, raw=raw, using=self.using)
        self.save_pool.append(instance, raw=raw)
        if self.save_pool.is_full():
            self.flush_saves()

    def delete(self, instance, using=None, **kwargs):
#        instance.pre_delete(instance.__class__, using=self.using)
        self.delete_pool.append(instance)
        if self.delete_pool.is_full():
            self.flush_deletes()

    def flush_saves(self):
        logging.debug("Flushing writes")
        for instance_cls_field_raw_list in self.save_pool:
            instance_cls_values_raw_list = []
            for instance, cls, field, raw in instance_cls_field_raw_list:
                values = []
                for local_field in cls._meta.local_fields:
                    if raw:
#                        value = getattr(self, local_field.attname)
                        value = getattr(instance, local_field.attname)
                    else:
                        value = local_field.pre_save(instance, not instance._entity_exists)
                    value = local_field.get_db_prep_save(value, connection=self.connection)
                    values.append((local_field, value))
                instance_cls_values_raw_list.append((instance, cls, values, raw))

            pk_vals = self.compiler.batch_save(instance_cls_values_raw_list)

            for (instance, cls, field, raw), pk_val in zip(instance_cls_field_raw_list, pk_vals):
                setattr(instance, cls._meta.pk.attname, pk_val)

                if field:
                    setattr(instance, field.attname, instance._get_pk_val(cls._meta))

                created = (not instance._entity_exists)
                instance._entity_exists = True
#                instance.post_save(cls, created=created, raw=raw,
#                                   using=self.using)
        self.save_pool.reset()

    def flush_deletes(self):
        self.save_pool.reverse()
        for instance_cls_field_raw_list in self.delete_pool:
            instance_cls_list = [(instance, cls) for instance, cls, field, raw
                            in instance_cls_field_raw_list]
            self.compiler.batch_delete(instance_cls_list)

            for instance, cls, field, _ in instance_cls_field_raw_list:
                setattr(instance, cls._meta.pk.attname, None)
                instance._entity_exists = False

                if field:
                    setattr(self, field.attname, None)

#                instance.post_delete(instance.__class__, using=self.using)
        self.delete_pool.reset()

    def flush(self):
        self.flush_saves()
        self.flush_deletes()
