import json
import os

from flask import make_response, request

from bot.workouts import track_workout
from bot.slash_commands.dac import update_database
from bot.slash_commands.mattend import update_mattend_modal
from bot.slash_commands.practice import submit_announcement
from bot.slash_commands.statistics import generate_statistics
from bot.routes import routes
from bot.validate_request import validate_request


@routes.route("/events", methods=["POST"])
@validate_request()
def events():
    """Dispatch workspace events sent to app's /slack/events url."""
    if request and "payload" in request.form:
        payload = json.loads(request.form["payload"])
        # submitted /practice modal
        if payload["view"]["callback_id"] == "/practice":
            submit_announcement(payload)
        # submitted from /mattend modal
        elif payload["view"]["callback_id"] == "/mattend":
            update_mattend_modal(payload)
        # submitted from /statistics modal
        elif payload["view"]["callback_id"] == "/statistics":
            generate_statistics(payload)
        # submitted from /dac modal
        elif payload["view"]["callback_id"] == "/dac":
            update_database(payload)
    elif request and "event" in request.json:
        event = request.json["event"]
        # message was posted in #workouts channel
        if (
            event["type"] == "message"
            and event["text"]
            and event["channel"] == os.getenv("WORKOUTS_CID")
        ):
            track_workout(event)
    # validates events url
    elif request and "challenge" in request.json:
        return make_response(request.json["challenge"])
    # default response
    return make_response("", 200)
