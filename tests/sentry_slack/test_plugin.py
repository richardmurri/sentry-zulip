from __future__ import absolute_import

import responses

from exam import fixture
from sentry.models import Rule
from sentry.plugins import Notification
from sentry.testutils import TestCase
from sentry.utils import json
from urlparse import parse_qs

from sentry_zulip.plugin import ZulipPlugin


class ZulipPluginTest(TestCase):
    @fixture
    def plugin(self):
        return ZulipPlugin()

    @responses.activate
    def test_simple_notification(self):
        responses.add('POST', 'http://example.com/zulip')
        self.plugin.set_option('webhook', 'http://example.com/zulip', self.project)

        group = self.create_group(message='Hello world', culprit='foo.bar')
        event = self.create_event(group=group, message='Hello world')

        rule = Rule.objects.create(project=self.project, label='my rule')

        notification = Notification(event=event, rule=rule)

        with self.options({'system.url-prefix': 'http://example.com'}):
            self.plugin.notify(notification)

        request = responses.calls[0].request
        payload = json.loads(parse_qs(request.body)['payload'][0])
        assert payload == {
            'parse': 'none',
            'username': 'Sentry',
            'attachments': [
                {
                    'color': '#f43f20',
                    'fields': [
                        {
                            'short': False,
                            'value': 'foo.bar',
                            'title': 'Culprit',
                        },
                        {
                            'short': True,
                            'value': 'foo Bar',
                            'title': 'Project'
                        },
                    ],
                    'fallback': '[foo Bar] Hello world',
                    'title': 'Hello world',
                    'title_link': 'http://example.com/baz/bar/issues/1/',
                },
            ],
        }
