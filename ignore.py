from flask import Flask, Response, redirect, request, url_for, render_template, after_this_request
app = Flask(__name__)


@app.route('/test')
def test():
    return app.send_static_file('callback.html')

if __name__ == "__main__":
    app.run()