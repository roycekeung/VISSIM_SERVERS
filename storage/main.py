#################################################################################
#
#   Description : start of Storage server on main thread
#
#################################################################################



from app import create_app

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--port', type=int, default=5500)


if __name__=="__main__":
    app= create_app()
    app.run(host="0.0.0.0", port=parser.port, debug=True, use_reloader=False)

