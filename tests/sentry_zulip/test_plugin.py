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
        self.plugin.set_option('apiurl', 'http://example.com/zulip', self.project)
        self.plugin.set_option('username', 'bot@example.com', self.project)
        self.plugin.set_option('apikey', 'testkey', self.project)
        self.plugin.set_option('stream', 'Sentry', self.project)

        group = self.create_group(message='Hello world', culprit='foo.bar')
        event = self.create_event(group=group, message='Hello world')

        rule = Rule.objects.create(project=self.project, label='my rule')

        notification = Notification(event=event, rule=rule)

        with self.options({'system.url-prefix': 'http://example.com'}):
            self.plugin.notify(notification)

        req = responses.calls[0].request
        assert req.url == 'http://example.com/zulip'
        data = parse_qs(req.body)
        assert data['content'][0] == '[ERROR] **foo Bar** Hello world [view](http://example.com/baz/bar/issues/1/)'
        assert data['to'][0] == 'Sentry'
        assert data['subject'][0] == 'Hello world'
        assert data['type'][0] == 'stream'
