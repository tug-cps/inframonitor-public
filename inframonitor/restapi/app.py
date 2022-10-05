import logging
import os

import connexion
from connexion.resolver import MethodViewResolver
from connexion.security.security_handler_factory import AbstractSecurityHandlerFactory
from flask import redirect
from flask_jwt_extended import JWTManager

# Workaround, disable connexion security and let jwt extended handle it
AbstractSecurityHandlerFactory.verify_security = lambda cls, auth_funcs, function: function
logging.basicConfig(level=logging.INFO)


def decode_token(token):
    # Dummy method, auth is done via flask jwt extended
    return {}


def create_app():
    connexion_app = connexion.FlaskApp(__name__, specification_dir='openapi/')

    app = connexion_app.app

    # Bugfix - Redirect to url with trailing slash to work with `app.url_map.strict_slashes = False`
    @app.route('/v2/ui')
    def ui():
        return redirect('/v2/ui/', code=302)

    @app.route('/')
    def root():
        return redirect('/v2/ui/', code=302)

    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "123456790")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
    app.config["JWT_TOKEN_LOCATIONS"] = ['headers']
    JWTManager(app)

    app.url_map.strict_slashes = False
    connexion_app.add_api('swagger.yaml',
                          resolver=MethodViewResolver('restapi.api'),
                          pythonic_params=True,
                          strict_validation=True,
                          validate_responses=True
                          )
    return connexion_app


if __name__ == "__main__":
    create_app().run(port=8080, debug=True)
