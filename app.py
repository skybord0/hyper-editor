from flask import Flask, render_template

from config import Config
from routes.upload_routes import upload_bp
from routes.tools_routes import tools_bp
from routes.conversion_routes import conversion_bp
from routes.download_routes import download_bp
from routes.history_routes import history_bp
from routes.pdf_editor_routes import pdf_editor_bp
from routes.word_editor_routes import word_editor_bp


def create_app():
    app = Flask(__name__)

    # Load application configuration
    app.config.from_object(Config)

    # Register application blueprints
    app.register_blueprint(upload_bp)
    app.register_blueprint(tools_bp)
    app.register_blueprint(conversion_bp)
    app.register_blueprint(word_editor_bp)
    app.register_blueprint(pdf_editor_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(download_bp)

    @app.get("/api/health")
    def health():
        return {"success": True, "application": "HYPER EDITOR"}

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/converter")
    def converter():
        return render_template("converter.html")

    @app.route("/tools")
    def tools():
        return render_template("tools.html")

    @app.route("/history")
    def history():
        return render_template("history.html")

    @app.route("/about")
    def about():
        return render_template("about.html")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )