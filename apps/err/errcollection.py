#################################################################################
#
#   Description : cutomized errors
#
#################################################################################


### datetime
class DatetimeInThePastError(Exception):
    """Raised when the input datetime is in the past"""
    pass


### operation on user database
class UserInActiveError(Exception):
    """Raised when user r still in active"""
    pass

### operation on storage database
class StorageTypeExistError(Exception):
    """Raised when storage action type have already exist, cant be chnaged"""
    pass



### operation on task database
class TaskIsRunningError(Exception):
    """Raised when task r still running in app servers"""
    pass

### operation on LocationEnum database
class LocationIsInUseError(Exception):
    """Raised when location is in use in the task list, plz delete the tasks first"""
    pass

### operation on LocationEnum database
class TypeIsInUseError(Exception):
    """Raised when type is in use in the task list, plz delete the tasks first"""
    pass

