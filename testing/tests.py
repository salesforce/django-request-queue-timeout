import http
import logging
import math
import time
from datetime import timedelta

from django.test import SimpleTestCase, modify_settings

from freezegun import freeze_time

from rqto.middleware import logger as rqto_logger

TIMEOUT_SETTING = 60


@modify_settings(
    MIDDLEWARE={"prepend": "rqto.middleware.RequestQueueTimeoutMiddleware"}
)
class RequestQueueTimeoutMiddlewareTests(SimpleTestCase):
    """
    Django middleware class to quickly dispatch any requests that wait too long in a queue before being processed

    """

    def test_request_without_header_is_successful(self):
        response = self.request_with_request_start_header(None)
        self.assertEqual(response.status_code, http.HTTPStatus.OK)

    def test_request_without_header_does_not_log_a_warning(self):
        sentinel = "sentinel message"
        with self.assertLogs(logger=rqto_logger, level=logging.WARN) as logs:
            rqto_logger.warning(sentinel)
            self.request_with_request_start_header(None)
        self.assertEqual(len(logs.records), 1)
        self.assertEqual(logs.records[0].msg, sentinel)

    def test_request_with_invalid_header_logs_warning(self):
        with self.assertLogs(logger=rqto_logger, level=logging.WARN):
            response = self.request_with_request_start_header("notanumber")
            self.assertEqual(response.status_code, http.HTTPStatus.OK)

    def test_request_with_invalid_header_sets_request_queue_time_to_none(self):
        response = self.request_with_request_start_header("notanumber")
        self.assertEqual(response.wsgi_request.queue_time_in_seconds, None)

    def test_queue_time_added_to_request(self):
        queue_time = 10
        response = self.request_with_queue_time(10)
        self.assertAlmostEqual(
            response.wsgi_request.queue_time_in_seconds, queue_time, delta=0.001
        )

    def test_enforcement_defaults_to_30_seconds(self):
        self.check_enforcement_threshold(30)

    def test_enforcement_is_configurable_by_setting(self):
        timeout = 60
        with self.settings(REQUEST_QUEUE_TIMEOUT_IN_SECONDS=60):
            self.check_enforcement_threshold(timeout)

    def check_enforcement_threshold(self, expected_threshold):
        if not isinstance(expected_threshold, timedelta):
            expected_threshold = timedelta(seconds=expected_threshold)

        response = self.request_with_queue_time(
            expected_threshold - timedelta(milliseconds=1)
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)

        response = self.request_with_queue_time(
            expected_threshold + timedelta(milliseconds=1)
        )
        self.assertEqual(response.status_code, http.HTTPStatus.SERVICE_UNAVAILABLE)

    def request_with_request_start_header(self, request_start):
        """
        Perform a request while including a request start header

        Args:
            request_start: header value to include; use `None` to omit the header
        """

        if request_start is None:
            return self.client.get("/")
        else:
            return self.client.get("/", HTTP_X_REQUEST_START=str(request_start))

    def request_with_queue_time(self, simulated_queue_time):
        """
        Perform a request while simulating a specified queue time

        Args:
            simulated_queue_time: amount of time request spent in queue; accepts either a number (in seconds) or a
                `datetime.timedelta`

        """
        if not isinstance(simulated_queue_time, timedelta):
            simulated_queue_time = timedelta(seconds=simulated_queue_time)

        with freeze_time() as frozen_time:
            request_start = math.floor(
                time.time() * 1000
            )  # convert seconds to milliseconds for header
            frozen_time.tick(delta=simulated_queue_time)
            return self.request_with_request_start_header(request_start)
