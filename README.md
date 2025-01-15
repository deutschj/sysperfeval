### Tracing select statement process with strace

To find out which systemcalls are done when a postgres select statement happens, I used strace. I'm planning to later measure the IO latency during a query using the systemcalls, that are called during execution of the select statement.

I created a table with 500 000 lines and used the following select statement:

`SELECT * FROM table_name;`

Using strace on the postgresql parent PID yielded the following results:

`strace -f -e trace=all -p $(pgrep postgres | head -n1)`

The preadv() systemcalls are visible; I'll try to use these for IO read latency measurement.

### Instrumenting USDT's to measure query latency

PostgreSQL provides USDT's if compiled with the according flag (--enable-dtrace). Because postgres was running in a container here, I had to get the correct container's PID and access the USDT's via the /proc directory:

```text
bpftrace -l usdt:/proc/3878649/root/usr/lib/postgresql/17/bin/postgres:*
usdt:/proc/3878649/root/usr/lib/postgresql/17/bin/postgres:postgresql:buffer__checkpoint__done
usdt:/proc/3878649/root/usr/lib/postgresql/17/bin/postgres:postgresql:buffer__checkpoint__start
usdt:/proc/3878649/root/usr/lib/postgresql/17/bin/postgres:postgresql:buffer__checkpoint__sync__start
usdt:/proc/3878649/root/usr/lib/postgresql/17/bin/postgres:postgresql:buffer__extend__done
usdt:/proc/3878649/root/usr/lib/postgresql/17/bin/postgres:postgresql:buffer__extend__start
usdt:/proc/3878649/root/usr/lib/postgresql/17/bin/postgres:postgresql:buffer__flush__done
usdt:/proc/3878649/root/usr/lib/postgresql/17/bin/postgres:postgresql:buffer__flush__start
usdt:/proc/3878649/root/usr/lib/postgresql/17/bin/postgres:postgresql:buffer__read__done
usdt:/proc/3878649/root/usr/lib/postgresql/17/bin/postgres:postgresql:buffer__read__start
usdt:/proc/3878649/root/usr/lib/postgresql/17/bin/postgres:postgresql:buffer__sync__done
usdt:/proc/3878649/root/usr/lib/postgresql/17/bin/postgres:postgresql:buffer__sync__start
usdt:/proc/3878649/root/usr/lib/postgresql/17/bin/postgres:postgresql:buffer__sync__written
usdt:/proc/3878649/root/usr/lib/postgresql/17/bin/postgres:postgresql:checkpoint__done
usdt:/proc/3878649/root/usr/lib/postgresql/17/bin/postgres:postgresql:checkpoint__start
usdt:/proc/3878649/root/usr/lib/postgresql/17/bin/postgres:postgresql:clog__checkpoint__done
[...]
```

Calculating time between the `postgres:postgresql:query__start` and `postgres:postgresql:query__done` probes:

```text
bpftrace usdt_test.bt
Attaching 4 probes...
PostgreSQL statement execution analyzer.
Time in microseconds (us).
pid   :Phase      :time to phase :time in phase : query
------|-----------|--------------|--------------|------
[4034334]Query start:              :              : vacuum pgbench_branches
[4034334]Query done : (       414) :           414: vacuum pgbench_branches
[4034334]Query start:              :              : vacuum pgbench_tellers
[4034334]Query done : (       157) :           157: vacuum pgbench_tellers
[4034334]Query start:              :              : truncate pgbench_history
[4034334]Query done : (       981) :           981: truncate pgbench_history
[4034335]Query start:              :              : SELECT * FROM pgbench_accounts;
[4034335]Query done : (    211722) :        211722: SELECT * FROM pgbench_accounts;
[4034335]Query start:              :              : SELECT * FROM pgbench_accounts;
[4034335]Query done : (    205086) :        205086: SELECT * FROM pgbench_accounts;
[4034335]Query start:              :              : SELECT * FROM pgbench_accounts;
[4034335]Query done : (    202960) :        202960: SELECT * FROM pgbench_accounts;
[4034335]Query start:              :              : SELECT * FROM pgbench_accounts;
[4034335]Query done : (    201454) :        201454: SELECT * FROM pgbench_accounts;
[4034335]Query start:              :              : SELECT * FROM pgbench_accounts;
[4034335]Query done : (    213973) :        213973: SELECT * FROM pgbench_accounts;
[4034335]Query start:              :              : SELECT * FROM pgbench_accounts;
[4034335]Query done : (    194772) :        194772: SELECT * FROM pgbench_accounts;
[4034335]Query start:              :              : SELECT * FROM pgbench_accounts;
[4034335]Query done : (    202489) :        202489: SELECT * FROM pgbench_accounts;
[4034335]Query start:              :              : SELECT * FROM pgbench_accounts;
[4034335]Query done : (    201386) :        201386: SELECT * FROM pgbench_accounts;
[4034335]Query start:              :              : SELECT * FROM pgbench_accounts;
[4034335]Query done : (    209295) :        209295: SELECT * FROM pgbench_accounts;
[4034335]Query start:              :              : SELECT * FROM pgbench_accounts;
[4034335]Query done : (    202439) :        202439: SELECT * FROM pgbench_accounts;
[4034335]Query start:              :              : SELECT * FROM pgbench_accounts;
[4034335]Query done : (    191400) :        191400: SELECT * FROM pgbench_accounts;
[4034335]Query start:              :              : SELECT * FROM pgbench_accounts;
[4034335]Query done : (    208308) :        208308: SELECT * FROM pgbench_accounts;
[4034335]Query start:              :              : SELECT * FROM pgbench_accounts;
[4034335]Query done : (    195276) :        195276: SELECT * FROM pgbench_accounts;
[4034335]Query start:              :              : SELECT * FROM pgbench_accounts;
[4034335]Query done : (    201337) :        201337: SELECT * FROM pgbench_accounts;
[4034335]Query start:              :              : SELECT * FROM pgbench_accounts;
[4034335]Query done : (    204130) :        204130: SELECT * FROM pgbench_accounts;
[4034335]Query start:              :              : SELECT * FROM pgbench_accounts;
[4034335]Query done : (    201296) :        201296: SELECT * FROM pgbench_accounts;
[4034335]Query start:              :              : SELECT * FROM pgbench_accounts;
[4034335]Query done : (    201408) :        201408: SELECT * FROM pgbench_accounts;
[4034335]Query start:              :              : SELECT * FROM pgbench_accounts;
[4034335]Query done : (    202892) :        202892: SELECT * FROM pgbench_accounts;
[4034335]Query start:              :              : SELECT * FROM pgbench_accounts;
[4034335]Query done : (    197219) :        197219: SELECT * FROM pgbench_accounts;
[4034335]Query start:              :              : SELECT * FROM pgbench_accounts;
[4034335]Query done : (    202364) :        202364: SELECT * FROM pgbench_accounts;
[4034490]Query start:              :              : -- ping
[4034490]Query done : (        47) :            47: -- ping
```

I executed the same select statement 20 times using pgbench, which can be seen here. Latency is about 200ms on average.

Important: when using the local-volume-provisioner, there are no block devices created. Instead, directory-based volumes are used -> we have to trace systemcalls like read() or write() instead of using block tracepoints. --> wrong, there was just no IO because the DB was too small

# Local-Path storage provider
##### using PG17, cache enabled

#### Analysis
* time from clone() to wait4() is not IO latency but just process runtime (one might consider that query latency).
* time to complete preadv() operations as seen in the strace for the child process that postgres spawns (child process runs the queries) would be IO latency

### How much of the query time is spent on IO? Whats the IO latency?
Postgres 17 with cache enabled:
Running 10 queries and tracing block IO latency per PID:

```console
Attaching 4 probes...
Monitoring pgbench for I/O latency...
^CAverage latency: 898204 ns


@io_count: 53843
@pgbench_pid: 1541677
@timestamps[8388640, 4262560]: 2963643001510604
@timestamps[8388608, 228280328]: 2963651301372539
@timestamps[8388608, 233921464]: 2963710553624990
@timestamps[8388608, 225983536]: 2963712750546513
@timestamps[8388608, 225983568]: 2963712750569761
@timestamps[8388608, 227793984]: 2963745635807680
@timestamps[8388608, 226132544]: 2963760159075657
@timestamps[8388608, 226135688]: 2963760164017068
@timestamps[8388640, 3444424]: 2963774559032762
@total_latency_ns: 48362020827

@usecs:
[64, 128)            452 |                                                    |
[128, 256)         12703 |@@@@@@@@@@@@@@@@@@@@@@@@                            |
[256, 512)          4931 |@@@@@@@@@                                           |
[512, 1K)          26867 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[1K, 2K)            8169 |@@@@@@@@@@@@@@@                                     |
[2K, 4K)             651 |@                                                   |
[4K, 8K)              49 |                                                    |
[8K, 16K)             11 |                                                    |
[16K, 32K)             2 |                                                    |
[32K, 64K)             6 |                                                    |
[64K, 128K)            1 |                                                    |
[128K, 256K)           0 |                                                    |
[256K, 512K)           0 |                                                    |
[512K, 1M)             0 |                                                    |
[1M, 2M)               0 |                                                    |
[2M, 4M)               0 |                                                    |
[4M, 8M)               1 |                                                    |
```

REDO for postgres 16

TODO add histogram

Per query total (accumulated) IO latency was 4836ms. The queries had run times of avg. 16 seconds (see pgbench output).
That means per query, 4836ms were spent in IO block operations, whereas the rest of the query runtime was spent elsewhere. This could include waiting and scheduling times (CPU as well), time to receive data from the cache, ...

This might mean that the application is not IO-bound. I took a look into htop and saw that while the select statements are executed, postgres constantly shows a CPU usage of >95% -> the application is probably CPU-bound instead.

In general IO latency was around 900ns on average.

```
$ pgbench -f /var/lib/postgresql/data/test.sql -h localhost -d app -U app -t 10 -c 1
Password:
pgbench (17.0 (Debian 17.0-1.pgdg110+1))
starting vacuum...end.
transaction type: /var/lib/postgresql/data/test.sql
scaling factor: 1
query mode: simple
number of clients: 1
number of threads: 1
maximum number of tries: 1
number of transactions per client: 10
number of transactions actually processed: 10/10
number of failed transactions: 0 (0.000%)
latency average = 15949.566 ms
initial connection time = 7.142 ms
tps = 0.062698 (without initial connection time)
```

Postgres 17 Cache enabled:
Measuring time it takes to complete preadv() operations (strace of the postgres process running the queries yielded, that this syscall was used):
```console
@hist:
[1]                   27 |                                                    |
[2, 4)               421 |                                                    |
[4, 8)               684 |                                                    |
[8, 16)            87581 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@               |
[16, 32)          120006 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[32, 64)            6083 |@@                                                  |
[64, 128)          19000 |@@@@@@@@                                            |
[128, 256)         13893 |@@@@@@                                              |
[256, 512)          2537 |@                                                   |
[512, 1K)            639 |                                                    |
[1K, 2K)             559 |                                                    |
[2K, 4K)              66 |                                                    |
[4K, 8K)              14 |                                                    |
[8K, 16K)             10 |                                                    |
```

No clear Bi-Modal distribution, supposedly 1-32us is reading data from cache and 64-512us are slower operations reading data from the disk.

#### How much time is spent on preadv() operations?

I ran the query 10 times and measured the time that was spent in preadv() oeprations overall (accumulated per query):

```console
@io_latency[3816425]: 316308
@io_latency[3817355]: 316955
@io_latency[3814594]: 360429
@io_latency[3817830]: 430263
@io_latency[3815002]: 438407
@io_latency[3815930]: 442812
@io_latency[3816797]: 452999
@io_latency[3815387]: 518351
@io_latency[3814077]: 538984
@io_latency[3813414]: 701048

@us:
[2, 4)                 8 |                                                    |
[4, 8)               108 |                                                    |
[8, 16)            55346 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[16, 32)           51286 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@    |
[32, 64)            1849 |@                                                   |
[64, 128)          13255 |@@@@@@@@@@@@                                        |
[128, 256)          3962 |@@@                                                 |
[256, 512)           880 |                                                    |
[512, 1K)            244 |                                                    |
[1K, 2K)             116 |                                                    |
[2K, 4K)               5 |                                                    |
[4K, 8K)               2 |                                                    |
```

The time spent in preadv() syscalls ranged from 316ms to 701ms, whereas the time spent in block IO operations amounted to ~4800ms. This meant that there is probably asynchronous IO being used, and that preadv() operations often don't lead to a block for the full duration of a block IO operation (therefore the differing values).

Postgres 17 uses vectored IO (clustering multiple pread64() syscalls into one preadv() syscall which might be harder to debug), so I decided to switch to Postgres 16.

## using PG16, with async IO

Postgres 16 with AIO enabled: measuring time to complete pread64() syscalls:

```console
@io_latency[3427879]: 997574
@io_latency[3425873]: 1013732
@io_latency[3426775]: 1104702
@io_latency[3428305]: 1117097
@io_latency[3426293]: 1136607
@io_latency[3425221]: 1158294
@io_latency[3427377]: 1178957
@io_latency[3424745]: 1195139
@io_latency[3428845]: 1209701
@io_latency[3424223]: 1470620

@us:
[0]                  180 |                                                    |
[1]              3273009 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[2, 4)            732028 |@@@@@@@@@@@                                         |
[4, 8)             40709 |                                                    |
[8, 16)            10482 |                                                    |
[16, 32)            1380 |                                                    |
[32, 64)             985 |                                                    |
[64, 128)          23941 |                                                    |
[128, 256)         16977 |                                                    |
[256, 512)          1004 |                                                    |
[512, 1K)            328 |                                                    |
[1K, 2K)             120 |                                                    |
[2K, 4K)              22 |                                                    |
[4K, 8K)               8 |                                                    |
[8K, 16K)              4 |                                                    |
[16K, 32K)             0 |                                                    |
[32K, 64K)             1 |                                                    |
```

In PG16, per query (process), around 1100ms of the query time are spent in pread64() operations. Whereas around 4800ms are spent in block IO operations -> probably Asynchronous IO is happening. preadv() may again not always block for the full duration that disk I/O takes to complete. TODO add link to other section ?

For testing purposes I then disabled the use of asynchronous IO, which can be forced by using the debug parameter `debug_direct_io`.

Disabling asynchronous IO made the application IO-bound:
* query took a lot longer
* in iostat, 100% IO usage and IO wait of around 20% can be observed

Reduced the DB size as queries took a lot longer when using direct IO.

## using PG16, with direct IO

#### Query duration (USDTs):

```console
[3942982]Query done : (        64) :            64: -- ping
[3942899]Query done : (   7802983) :       7802983: SELECT * FROM pgbench_accounts;
[3942899]Query start:              :              : SELECT * FROM pgbench_accounts;
[3943335]Query start:              :              : -- ping
[3943335]Query done : (        42) :            42: -- ping
[3942899]Query done : (   7850340) :       7850340: SELECT * FROM pgbench_accounts;
[3942899]Query start:              :              : SELECT * FROM pgbench_accounts;
[3943598]Query start:              :              : -- ping
[3943598]Query done : (        53) :            53: -- ping
[3942899]Query done : (   7974342) :       7974342: SELECT * FROM pgbench_accounts;
[3942899]Query start:              :              : SELECT * FROM pgbench_accounts;
[3942899]Query done : (   7663468) :       7663468: SELECT * FROM pgbench_accounts;
[3942899]Query start:              :              : SELECT * FROM pgbench_accounts;
[3943847]Query start:              :              : -- ping
[3943847]Query done : (        53) :            53: -- ping
[3942899]Query done : (   7979018) :       7979018: SELECT * FROM pgbench_accounts;
[3942899]Query start:              :              : SELECT * FROM pgbench_accounts;
[3944089]Query start:              :              : -- ping
[3944089]Query done : (        42) :            42: -- ping
[3942899]Query done : (   7980232) :       7980232: SELECT * FROM pgbench_accounts;
[3942899]Query start:              :              : SELECT * FROM pgbench_accounts;
[3944387]Query start:              :              : -- ping
[3944387]Query done : (        78) :            78: -- ping
[3942899]Query done : (   7723262) :       7723262: SELECT * FROM pgbench_accounts;
[3942899]Query start:              :              : SELECT * FROM pgbench_accounts;
[3944648]Query start:              :              : -- ping
[3944648]Query done : (        40) :            40: -- ping
[3942899]Query done : (   7600260) :       7600260: SELECT * FROM pgbench_accounts;
[3942899]Query start:              :              : SELECT * FROM pgbench_accounts;
[3944994]Query start:              :              : -- ping
[3944994]Query done : (       100) :           100: -- ping
[3942899]Query done : (   7856708) :       7856708: SELECT * FROM pgbench_accounts;
[3942899]Query start:              :              : SELECT * FROM pgbench_accounts;
[3942899]Query done : (   7791054) :       7791054: SELECT * FROM pgbench_accounts;
[3945259]Query start:              :              : -- ping
```
Average query duration was 7822,166 ms.

#### Block IO latency
Measuring block IO latency, I executed the select statement 10 times here:

```console
Attaching 4 probes...
Monitoring postgres block I/O latency...
Average latency: 144032 ns

@io_count: 411020
@pg_pid: 3854574

@total_latency_ns: 59200377302
@usecs:
[64, 128)          57168 |@@@@@@@@                                            |
[128, 256)        351301 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[256, 512)          1975 |                                                    |
[512, 1K)            386 |                                                    |
[1K, 2K)             152 |                                                    |
[2K, 4K)              37 |                                                    |
[4K, 8K)               0 |                                                    |
[8K, 16K)              0 |                                                    |
[16K, 32K)             3 |                                                    |
```

In contrast to PG17, when using PG16 with direct IO, block IO operations accounted for most of the query response time. Block IO operations took mostly around 128-256 ms and overall accounted for 5920 ms of time spent in IO on average (= 75% of the 7822 ms query response time).

#### IO time occupied by pread64() syscalls

Accumulating time spent in pread64() syscalls:

```console
@io_latency[3958941]: 61766041

@us:
[64, 128)          20004 |@@                                                  |
[128, 256)        388333 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[256, 512)          2841 |                                                    |
[512, 1K)            937 |                                                    |
[1K, 2K)             228 |                                                    |
[2K, 4K)              57 |                                                    |
[4K, 8K)               9 |                                                    |
```

Here ~6176ms were spent in pread64() syscalls, which is slightly more than the time spent in block IO operations. This makes sense, as the time spent in the syscall does not only include the block IO operation, but also IO waiting times, ... TODO

In contrast to when I used PG17 with AIO enabled, (there time in preadv syscalls amounted to way less than the time in block IO operations), when using direct IO, the time spent in pread64() syscalls does match up with the time spent in block IO operations.
After some more investigation on how the preadv() syscall works, I figured that it can initiate multiple read operations in order to read into multiple buffers. This is often used to achieve asynchronous IO in threaded applications (because the main thread can still perform other operations while IO is running)
**--> Using preadv, the IO operations may continue running in the background after block IO operations have been initiated (but not finished yet)**

## IOps

As a second metric I looked at IOps. To measure them for the postgres processes I counted read and write syscalls:

Postgres 17 with AIO enabled:
```console
Parent 'postgres' IOPS: 0
Parent 'postgres' IOPS: 1200
Parent 'postgres' IOPS: 2428
Parent 'postgres' IOPS: 2407
Parent 'postgres' IOPS: 2344
Parent 'postgres' IOPS: 2713
Parent 'postgres' IOPS: 2628
Parent 'postgres' IOPS: 2440
Parent 'postgres' IOPS: 2501
Parent 'postgres' IOPS: 2612
Parent 'postgres' IOPS: 2399Parent 'postgres' IOPS: 1749
Parent 'postgres' IOPS: 0
Parent 'postgres' IOPS: 0
```

Plotting data as a histogram: ![Histogram of IOps distribution](results/local-path/iops_pg17_aio.png)

## PG16 with direct IO enabled

IOps observed when using direct IO in PG16 are higher, as the AIO in PG17 clusters multiple pread64() syscalls into one preadv() syscall. Also they're higher mostly because I enabled direct IO, which minimizes caching effects.
Script output:

```console
Attaching 4 probes...
Parent 'postgres' IOPS: 5436
Parent 'postgres' IOPS: 5375
Parent 'postgres' IOPS: 5708
Parent 'postgres' IOPS: 5756
Parent 'postgres' IOPS: 3491
Parent 'postgres' IOPS: 5374
Parent 'postgres' IOPS: 5101
Parent 'postgres' IOPS: 5081
Parent 'postgres' IOPS: 5409
Parent 'postgres' IOPS: 5540
Parent 'postgres' IOPS: 5421
Parent 'postgres' IOPS: 5435
Parent 'postgres' IOPS: 3892
```

![IOps distribution histogram, PG16, 1 client](results/local-path/iops_pg16_dio_1.png)

The count of pread64() and pwrite64() syscalls matched up with the outputs of `iostat -sx 1` as well:
```console
avg-cpu:  %user   %nice %system %iowait  %steal   %idle
           7.56    0.00    6.30   18.14    0.00   68.01

Device             tps      kB/s    rqm/s   await aqu-sz  areq-sz  %util
sda            5690.00  45828.00   221.00    0.15   0.84     8.05 100.00
sdb               0.00      0.00     0.00    0.00   0.00     0.00   0.00
sdc               2.00      8.00     0.00    0.50   0.00     4.00   0.40
```

Although disk usage is 100%, no high IO latency can be observed (avg. between 128 and 256 microseconds). Performance of the query is therefore being limited by IOps, and the block IO operations themselves don't experience any high latencies - as these are sequential reads and the disk can handle them efficiently.

IO latency and IOps seem to stay the same when I increased the database size (by 200%) - so probably query runtime is limited by the disk's capacity of performing read operations, IOps.

When increasing the number of clients in pgbench (to 10), IOps increased because queries were now run by multiple clients in parallel. However IO latency stayed the same:

![IOps distribution histogram, PG16, 10 clients](results/local-path/iops_pg16_dio_10.png)

For reference: testing disk IOps and IO latency with fio (running with 1 client) delivers similar results, although IO latency is a bit higher:

```text
lat (usec): min=291, max=11703, avg=494.78, stdev=199.89
read: IOPS=2015, BW=15.7MiB/s (16.5MB/s)(945MiB/60001msec)
```

The higher latency is explained by postgres partially reading data from the OS cache (as I didn't clear the OS cache after every time running the experiment, frequently accessed data will be cached there). Postgres also has its own shared buffer cache, but I set this to the minimum value here (128kB) and didn't encounter any cache hits on the Postgres side. Buffer cache hits would be shown as `Buffers: shared hit=x`.

```sql
app=> explain (analyze, buffers) select * from pgbench_accounts;
                                                          QUERY PLAN
------------------------------------------------------------------------------------------------------------------------------
 Seq Scan on pgbench_accounts  (cost=0.00..65984.00 rows=2500000 width=97) (actual time=0.246..6426.156 rows=2500000 loops=1)
   Buffers: shared read=40984
```

Latency distribution when running fio:

```console
Attaching 4 probes...
^CAverage latency: 512320 ns
@io_count: 186232
@pgbench_pid: 293341

@total_latency_ns: 95410547004
@usecs:
[64, 128)              1 |                                                    |
[128, 256)            17 |                                                    |
[256, 512)        129704 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[512, 1K)          53671 |@@@@@@@@@@@@@@@@@@@@@                               |
[1K, 2K)            2021 |                                                    |
[2K, 4K)             508 |                                                    |
[4K, 8K)             148 |                                                    |
[8K, 16K)             87 |                                                    |
[16K, 32K)            27 |                                                    |
[32K, 64K)            30 |                                                    |
[64K, 128K)           18 |                                                    |
```

# Longhorn


# Done:
* measured block io latency for local-path provider using postgres queries.
* found out how much of the query time is spent on IO.
* measured postgres query latency using bpftrace on usdt probes.
* measured iops when running the postgres queries.

# TODO:
* measuring time in preadv would actually make sense I think ✅
* measure io lat for longhorn
* measure iops for longhorn
* measure query time for longhorn
* measure how much of the query time is spent on IO there.
* analyze differences. why are io lat or iops lower in longhorn?
* switch off cache; debug_io_direct and analyze changes in io latency? (1) ✅
* would be interesting to look at cache hit rate
* Reference values? FIO results

# Errors:
* measuring time between read and close does not make sense; these are unrelated
* measuring the time between clone and wait4 measures the process runtime, not any other latency (process runtime includes e.g. io latency of course).
* when the db is too small, all the lines can be cached and read from cache -> when looking at IOps using iostat, none are recorded.

# Methodology:
* Objective: compare Longhorn and local-path provider on Kubernetes
* Setup: 6 Node Kubernetes cluster, workloads running always on the same worker node in this test.
* no other applications receiving any load are running on the Kubernetes cluster
* Postgres database as a test workload: single-instance, direct IO (no asynchronous IO, easier debugging/tracing possible)
* Metrics to analyze: IO latency, IOps
* Analyze differences in values for the metrics observed between the two solutions.
* => Why are we seeing these differences?
* Visualize results: histograms for latency, what kind of distributions can we observe?