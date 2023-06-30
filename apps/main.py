#################################################################################
#
#   Description : start of que server on sub thread
#
#################################################################################

from app import create_app, get_RunCal

import threading

import asyncio
        
        
if __name__ == '__main__':
        
    compute = get_RunCal()
    app = create_app()
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5600, debug=True, use_reloader=False)).start()
    asyncio.run(compute.start())
    # compute.start()

