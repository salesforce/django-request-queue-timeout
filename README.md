# Django-Request-Queue-Timeout

This package provides a Django middleware class to quickly dispatch any requests that wait too long in a queue before being processed.

This is useful in environments like Heroku, where traffic spikes can result in requests remaining in the queue well beyond the [30 second limit](https://devcenter.heroku.com/articles/http-routing#timeouts) the Heroku router enforces before giving up on the request.  With this middleware in place, applications recover much more quickly by not wasting time processing requests for which clients have already received a server error response. 

## Requirements

* Python >= 3.6
* Django >= 2.2

## Installation

Install from git

    pip install git+<git address>#egg=django-request-queue-timeout
    
Install from [PyPI](https://pypi.org/)

    pip install django-request-queue-timeout  # Not yet published to PyPI

Add to `MIDDLEWARE` list in settings file as the first item:

```python
MIDDLEWARE = (
    'rqto.middleware.RequestQueueTimeoutMiddleware'
    ...
)
```

## Configuration

When installed, the middleware checks each incoming request for a [`X-REQUEST-START` header](https://devcenter.heroku.com/articles/http-routing#heroku-headers) value indicating when the request started (in milliseconds since the unix epoch).  If the request has queued too long before being processed a `503 Service Unavailable` response is generated.

The timeout is 30 seconds by default, but can be configured to a different value by providing a Django setting:

```python
REQUEST_QUEUE_TIMEOUT_IN_SECONDS = 60  # configure a 60 second request queue timeout
```

## See Also
- [Request Timeout | Heroku Dev Center](https://devcenter.heroku.com/articles/request-timeout)
