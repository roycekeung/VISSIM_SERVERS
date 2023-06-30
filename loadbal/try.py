# #################################################################################
# #
# #   Description : start of backend server on main thread
# #
# #################################################################################

# # from app import create_app

# from que.simoptque import runque, Quebase
# import time

# # app, socketio= create_app()

# if __name__ == '__main__':


#     t1 = runque()
#     t1.start()


#     # print(id(queue))
#     Quebase.addin(1)
#     Quebase.addin(2)

#     time.sleep(60)
#     t1.stop()
#     t1.join()


#     # APP_SERVER_STATUS = [False , False, True, True, False]
#     # APP_SERVER = ["143.89.22.34:5000", "143.89.22.131:5000", "143.89.22.300:5000", "143.89.22.400:5000", "143.89.22.500:5000"]
#     # host = APP_SERVER[APP_SERVER_STATUS.index(True)]
#     # print(host)

import redis
POOL = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=POOL)

print("r.hvals('vmserv_free'): ", type(r.hvals('vmserv_free')), r.hvals('vmserv_free'))

print("all(isfree == str(0) for isfree in r.hvals('vmserv_free'): ", 
      type(all(isfree == str(0) for isfree in r.hvals('vmserv_free'))), 
           all(isfree == str(0) for isfree in r.hvals('vmserv_free')) )

test_all1 = ['1', '1', '1']
print("all(isfree == str(0) for isfree in test_all1: ", 
      type(all(isfree == str(0) for isfree in test_all1)), 
           all(isfree == str(0) for isfree in test_all1) )

test_all0 = ['0', '0', '0']
print("all(isfree == str(0) for isfree in test_all1: ", 
      type(all(isfree == str(0) for isfree in test_all0)), 
           all(isfree == str(0) for isfree in test_all0) )

## get app server keys
app_server_pool = r.hkeys("vmserv_free")

print("r.hkeys('vmserv_free'): ", type(r.hkeys('vmserv_free')), r.hkeys('vmserv_free'))

print(type(""),  "")
print(type("-1"),  "-1")
print(type(int("-1")),  int("-1"))