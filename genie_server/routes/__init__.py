from . import (
    base_routes, view_routes, write_routes,
    loop_auto, loop_prediction, loop_gti,
    loop_learning, loop_system, loop_final, loop_auto_gti,
    mvrv_routes   # ← 🔥 여기 추가!
)

def register_routes(app):
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
        mvrv_routes,   # ← 🔥 여기도 추가!
    ]:
        app.register_blueprint(module.bp)
