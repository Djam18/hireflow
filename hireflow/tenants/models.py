from django.db import models


class Company(models.Model):
    """Multi-tenant company model — each company is an isolated tenant."""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'companies'

    def __str__(self):
        return self.name
