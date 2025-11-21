# genie_server/routes/__init__.py

from . import (
    base_routes, view_routes, write_routes,
    loop_auto, loop_prediction, loop_gti,
    loop_learning, loop_system, loop_final,
    loop_auto_gti, mvrv_routes
)

# indicator routes – 모듈이 아니라 블루프린트(bp)만 가져옴
from .indicator_routes import bp as bp_indicator


def register_routes(app):
    # 다른 라우트 모듈들 등록
    for module in [
        base_routes,
        view_routes,
        write_routes,
        loop_auto,
        loop_prediction,
        loop_gti,
        loop_learning,
        loop_system,
        loop_final,
        loop_auto_gti,
        mvrv_routes,
    ]:
        app.register_blueprint(module.bp)

    # indicator는 개별 등록
    app.register_blueprint(bp_indicator)
