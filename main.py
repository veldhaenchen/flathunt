##
# Startup file for Google Cloud deployment
##

from flathunter.web import app

if __name__ == '__main__':
    # This is only used when running locally
    app.run(host='127.0.0.1', port=8080, debug=True)
