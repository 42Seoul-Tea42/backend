def run_once(func):
    def wrapper(*args, **kwargs):
        assert wrapper.has_run == False

        wrapper.has_run = True
        return func(*args, **kwargs)

    wrapper.has_run = False
    return wrapper


@run_once
def add_routes(app):

    from ..user.userController import bp_user
    from ..history.historyController import bp_history
    from ..chat.chatController import bp_chat
    from ..oauth.kakaoController import bp_kakao

    app.register_blueprint(bp_user)
    app.register_blueprint(bp_history)
    app.register_blueprint(bp_chat)
    app.register_blueprint(bp_kakao)
