from flask import request
from flask_jwt_extended import jwt_required

from restapi.app import create_app

app = create_app()


@app.app.before_request
def before_request_func():
    @jwt_required()
    def check_jwt():
        pass

    if not request.full_path.startswith('/v2/ui') and not request.full_path == '/v2/openapi.json?':
        check_jwt()


if __name__ == "__main__":
    app.run(port=8080, debug=True)
