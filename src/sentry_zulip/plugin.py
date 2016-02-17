"""
sentry_zulip.plugin
~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2015 by Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
import requests
import sentry_zulip

from django import forms
from sentry.plugins.bases import notify
from sentry.http import build_session


# Project.get_full_name backported from v8.0
def get_project_full_name(project):
    if project.team.name not in project.name:
        return '%s %s' % (project.team.name, project.name)
    return project.name


class ZulipOptionsForm(notify.NotificationConfigurationForm):
    apiurl = forms.URLField(
        help_text='Your custom Zulip api URL',
        widget=forms.URLInput(attrs={'class': 'span8'}),
        initial='https://zulip.example.com/api/v1/messages'
    )
    username = forms.CharField(
        label='Bot Name',
        help_text='The name of the bot.',
        widget=forms.TextInput(attrs={'class': 'span8'}),
        initial='sentry@example.com',
        required=True
    )
    apikey = forms.CharField(
        label='Bot API Key',
        help_text='The api key of the bot (for authentication).',
        widget=forms.TextInput(attrs={'class': 'span8'}),
        required=True
    )
    stream = forms.CharField(
        label='Stream name',
        help_text='The name of the stream to post messages to.',
        widget=forms.TextInput(attrs={'class': 'span8'}),
        initial='Sentry',
        required=True
    )


class ZulipPlugin(notify.NotificationPlugin):
    author = 'Richard Murri'
    author_url = 'https://github.com/richardmurri/sentry-zulip'
    resource_links = (
        ('Bug Tracker', 'https://github.com/richardmurri/sentry-zulip/issues'),
        ('Source', 'https://github.com/richardmurri/sentry-zulip'),
    )

    title = 'Zulip'
    slug = 'zulip'
    description = 'Post notifications to a Zulip stream.'
    conf_key = 'zulip'
    version = sentry_zulip.VERSION
    project_conf_form = ZulipOptionsForm

    def is_configured(self, project):
        return all((self.get_option(k, project) for k in ('apiurl', 'username', 'apikey', 'stream')))

    def notify(self, notification):
        event = notification.event
        group = event.group
        project = group.project

        if not self.is_configured(project):
            return

        apiurl = self.get_option('apiurl', project)
        username = self.get_option('username', project).strip().encode('utf-8')
        apikey = self.get_option('apikey', project).encode('utf-8')
        stream = self.get_option('stream', project).strip().encode('utf-8')
        level = group.get_level_display()

        title = event.message_short.encode('utf-8')
        project_name = get_project_full_name(project).encode('utf-8')

        values = {
            'type': 'stream',
            'to': stream,
            'subject': title,
            'content': "[%s] **%s** %s [view](%s)" % (
                level.upper(), project_name, title, group.get_absolute_url()
            )
        }

        # Apparently we've stored some bad data from before we used `URLField`.
        apiurl = apiurl.strip(' ')

        session = build_session()
        return session.request(method='POST',
                               url=apiurl,
                               data=values,
                               auth=(username, apikey))
