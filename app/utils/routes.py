from flask_restx import Api


def run_once(func):
    def wrapper(*args, **kwargs):
        assert wrapper.has_run == False

        wrapper.has_run = True
        return func(*args, **kwargs)

    wrapper.has_run = False
    return wrapper


@run_once
def add_routes(app):

    api = Api(
        version="1.0",
        title="tea42",
        # prefix="/sw",
        contact_email="tea42fourtwo@gmail.com",
        # doc=False,  # swagger 표시 안하겠당!
    )

    api.init_app(app)

    from ..user import userController

    # from ..tea import teaController
    from ..history import historyController
    from ..chat import chatController
    from ..oauth import kakaoController

    api.add_namespace(userController.ns)
    # api.add_namespace(teaController.ns)
    api.add_namespace(historyController.ns)
    api.add_namespace(chatController.ns)
    api.add_namespace(kakaoController.ns)
