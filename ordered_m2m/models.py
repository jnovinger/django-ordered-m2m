import simplejson

from django.db import models
from django.utils.lru_cache import lru_cache


class OrderedM2M(models.Model):
    _ordered_m2m_ordering = models.TextField(blank=True)

    class Meta:
        abstract = True

    @lru_cache(maxsize=128)
    def _get_filtered_m2m(self, m2m_field):
        return m2m_field.through.objects.filter(
            **{m2m_field.query_field_name: self}).exists()

    @lru_cache(maxsize=20)
    def _get_ordered_m2m_for(self, attr_name):
        print('_get_ordered_m2m_for_{} running'.format(attr_name))
        m2m_field = getattr(self, attr_name)
        m2m = m2m_field.all()
        order = self._ordered_m2m_ordering
        if self._get_filtered_m2m(m2m_field):
            if order:
                json = simplejson.loads(order)
                attr_ordering = json.get(attr_name, None)
                if attr_ordering:
                    m2m = {m.id: m for m in m2m}
                    # ordered_m2m = []
                    # for pk in attr_ordering:
                    #     ordered_m2m += [obj for obj in m2m if obj.pk == pk]
                    ordered_m2m = [m2m[pk] for pk in attr_ordering]
                    ordered_m2m.extend(obj for obj in m2m.itervalues() if obj not in ordered_m2m)
                    return ordered_m2m

            # For consistency, return it as a list
            return list(m2m)
