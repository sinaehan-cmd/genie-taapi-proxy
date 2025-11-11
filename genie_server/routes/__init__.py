from . import (
    base_routes, view_routes, write_routes,
    loop_auto, loop_prediction, loop_gti,
    loop_learning, loop_system, loop_final, loop_auto_gti
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
    ]:
        app.register_blueprint(module.bp)
