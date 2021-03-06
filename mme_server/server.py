"""
This is a minimum working example of a Matchmaker Exchange server.
It is intended strictly as a useful reference, and should not be
used in a production setting.
"""

from __future__ import with_statement, division, unicode_literals

import logging

from flask import Flask, request, after_this_request, jsonify
from flask_negotiate import consumes, produces

from .models import MatchRequest
from .schemas import validate_request, validate_response, ValidationError


API_MIME_TYPE = 'application/vnd.ga4gh.matchmaker.v1.0+json'

# Global flask application
app = Flask(__name__)
# Logger
logger = logging.getLogger(__name__)


@app.route('/match', methods=['POST'])
@consumes(API_MIME_TYPE, 'application/json')
@produces(API_MIME_TYPE)
def match():
    """Return patients similar to the query patient"""

    @after_this_request
    def add_header(response):
        response.headers['Content-Type'] = API_MIME_TYPE
        return response

    logger.info("Getting flask request data")
    request_json = request.get_json(force=True)

    logger.info("Validate request syntax")
    try:
        validate_request(request_json)
    except ValidationError as e:
        response = jsonify(message='Request does not conform to API specification:\n{}'.format(e))
        response.status_code = 422
        return response

    logger.info("Parsing query")
    request_obj = MatchRequest.from_api(request_json)

    logger.info("Finding similar patients")
    response_obj = request_obj.match(n=5)

    logger.info("Serializing response")
    response_json = response_obj.to_api()

    logger.info("Validate response syntax")
    try:
        validate_response(response_json)
    except ValidationError as e:
        # log to console and return response anyway
        logger.error('Response does not conform to API specification:\n{}'.format(e))

    return jsonify(response_json)

