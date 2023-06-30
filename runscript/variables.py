

from enum import Enum, IntEnum



### just for note no actual usage
class LocationEnum(IntEnum):
    KaiLeng = 1
    KwunTong = 2
    LamTin = 3
    LungFungRd = 4


class AlgoTypeEnum(IntEnum):
    Callabrate = 1
    NGA = 2
    SGA = 3
    
### loadbalancer algo
class LoadbalancerAlgo(IntEnum):
    random = 0
    roundrobin = 1
    
