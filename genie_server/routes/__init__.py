from . import (
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
)

# indicator / dominance는 블루프린트만 직접 가져옴
from .indicator_routes import bp as bp_indicator
from .dominance_routes import bp as bp_dominance


def register_routes(app):
    """모든 Blueprint를 Flask 앱에 등록"""

    # 1) 일반 라우트 모듈들 — 모듈 안에 bp 존재
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
        if hasattr(module, "bp"):
            app.register_blueprint(module.bp)

    # 2) 개별 Blueprint 등록 — indicator / dominance
    app.register_blueprint(bp_indicator)
    app.register_blueprint(bp_dominance)
