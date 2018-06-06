from . import application


@application.route('/')
def index():
	return '', 200
