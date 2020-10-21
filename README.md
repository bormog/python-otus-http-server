## Python HTTP Server

### Что делает
- Умеет понимать GET, HEAD запросы
- Отдавать файлы из DOCUMENT_ROOT
- На все остальные запросы возвращает 400 Bad Request, 405 Method Not Allowed, 404 Not Found в зависимости от ситуации
- Масштабироваться на несколько воркеров

### Принцип работы
- На старте заранее создаются N воркеров (threading.Thread), которые слушают очередь (queue.Queue)
- Сервер складывает коннекшены в очередь, которую в свою очередь разгребают воркеры
- Воркер вызывает HTTPHandler, который умеет распарсить инфо в HTTPRequest и сформировать HTTPResponse

### Как запускать
``` sh
python -a HOST -p PORT -w NUM WORKERS -b BACKLOG -d DOCUMENTROOT httpd.py
```

#### Опции
- -a - host, default = 127.0.0.1
- -p - port, default = 8080
- -w - num of workers, default = 20
- -b - queue size for each worker, default = 10
- -d - document root, default = static

### Нагрузочное тестирование

``` sh
ab -n 50000 -c 100 -r http://127.0.0.1:8080/

This is ApacheBench, Version 2.3 <$Revision: 1843412 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient)
Completed 5000 requests
Completed 10000 requests
Completed 15000 requests
Completed 20000 requests
Completed 25000 requests
Completed 30000 requests
Completed 35000 requests
Completed 40000 requests
Completed 45000 requests
Completed 50000 requests
Finished 50000 requests


Server Software:        Python
Server Hostname:        127.0.0.1
Server Port:            8080

Document Path:          /
Document Length:        1013 bytes

Concurrency Level:      100
Time taken for tests:   46.244 seconds
Complete requests:      50000
Failed requests:        0
Total transferred:      58150000 bytes
HTML transferred:       50650000 bytes
Requests per second:    1081.23 [#/sec] (mean)
Time per request:       92.487 [ms] (mean)
Time per request:       0.925 [ms] (mean, across all concurrent requests)
Transfer rate:          1228.00 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0  41.3      0    9227
Processing:     8   92 475.4     55    9285
Waiting:        1   85 451.6     52    9279
Total:         11   92 477.2     55    9285

Percentage of the requests served within a certain time (ms)
  50%     55
  66%     58
  75%     60
  80%     63
  90%     73
  95%     81
  98%     94
  99%    113
 100%   9285 (longest request)
```