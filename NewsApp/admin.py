from django.contrib import admin
from .models import SearchQueries,Review

class SearchQueriesAdmin(admin.ModelAdmin):
    list_display = ('user', 'keyword', 'positive_articles', 'neutral_articles', 'negative_articles', 'search_date')
    search_fields = ('user__username', 'keyword')
    list_filter = ('search_date',)

admin.site.register(SearchQueries, SearchQueriesAdmin)
admin.site.register(Review)
