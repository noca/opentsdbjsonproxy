opentsdbjsonproxy
=================

A http json proxy for opentsdb

This proxy is for parse the ascii output of opentsdb to json.

we occupied the 5042 port to offer same content as 4242 does in ascii, but in a json format. The query param is same as original opentsdb http api.

The original ascii query url is:
http://127.0.0.1:4242/q?start=2013/12/29-00:40:00&m=avg:rate:bandwidth%7Bhost=192.168.3.13%7C192.168.3.14,port=Ten-GigabitEthernet2/0/0,way=out%7D&ascii

The original ascii format is:

<metric> <timestamp> <value> <tagk1>=<tagv1> <tagk2>=<tagv2> ...
...


The proxy json query url is:
http://127.0.0.1:5242/q?start=2013/12/29-00:40:00&m=avg:rate:bandwidth%7Bhost=192.168.3.13%7C192.168.3.14,port=Ten-GigabitEthernet2/0/0,way=out%7D&ascii

The proxy json format is:
[
        {
                metric:<metric>,
                timestamp:<timestamp>,
                value:<value>,
                tags: [
                      <tagk1>:<tagv1>,
                      <tagk2>:<tagv2>,
                      ...
                ],
        },
        ...
]

For easy combined with charting utils like highcharts, we offer some more easy format data. With an additional parameter charttype:

highcharts1

URL:
http://211.152.118.197:5242/q?start=2013/12/29-00:40:00&m=avg:rate:bandwidth%7Bhost=192.168.3.13%7C192.168.3.14,port=Ten-GigabitEthernet2/0/0,way=out%7D&ascii&charttype=highcharts

Format:
[{
        name:<metric>{<tagk1>=<tagv1>,<tagk2>=<tagv2>,...},
        pointStart:<min_timestamp>,
        pointInterval: <(max_timestamp - min_timestamp)/data_count>,
        data : [<value1>, <value2>, ...]
},
...
]


highcharts2

URL:
http://211.152.118.197:5242/q?start=2013/12/29-00:40:00&m=avg:rate:bandwidth%7Bhost=192.168.3.13%7C192.168.3.14,port=Ten-GigabitEthernet2/0/0,way=out%7D&ascii&charttype=highcharts2

Format:
[{
        name:<metric>{<tagk1>=<tagv1>,<tagk2>=<tagv2>,...},
        data:[
                [<timestamp1>, <value1>],
                [<timestamp2>, <value2>],
                ...
        ]
},
...
]