from django.contrib import admin
from .models import CustomUser, Challenge, Hint, Submission , UserHint
# Register your models here.

admin.site.register(CustomUser)
@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_filter = ('is_visible','author')  # Replace with actual fields to filter by
# Removed redundant registration of Challenge model
admin.site.register(Hint)
admin.site.register(UserHint)
from django.contrib import admin
from django.utils.html import format_html
from .models import Submission

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "challenge",
        "submission_time",
        "status_indicator",
    )

    list_filter = (
        "is_correct",
        "is_false",
        "challenge",
        "user",
        "submission_time",
    )

    search_fields = (
        "user__username",
        "challenge__title",
        "challenge__author__username",
    )

    readonly_fields = ("submission_time",)

    def status_indicator(self, obj):
        if obj.is_correct:
            return format_html('<span style="color: #22c55e; font-weight:600;">✔ Correct</span>')
        if obj.is_false:
            return format_html('<span style="color: #ef4444; font-weight:600;">✘ Wrong</span>')
        return format_html('<span style="color:#6b7280;">Pending</span>')

    status_indicator.short_description = "Status"
