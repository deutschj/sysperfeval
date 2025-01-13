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

#### Measuring time from enter_preadv to exit_preadv:


#### Analysis
* time from clone() to wait4() is not IO latency but just process runtime (one might consider that query latency).
* time to complete preadv() operations as seen in the strace for the child process that postgres spawns (child process runs the queries) would be IO latency

### How much of the query time is spent on IO? Whats the IO latency?

Running 10 queries and tracing block IO latency per PID:

´´´console
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
´´´

TODO ad  histogram

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

Postgres 16: measuring time to complete pread64() syscalls:

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

Per query (process), around 1100ms of the query time are spent in pread64() operations. Whereas around 4800ms are spent in block IO operations -> probably Asynchronous IO is happening. preadv() may not always block for the full duration that disk I/O takes to complete.


### IOps

As a second metric I looked at IOps. To measure them for the postgres processes I counted read and write syscalls:

```console
Parent 'postgres' IOPS: 274
Parent 'postgres' IOPS: 221
Parent 'postgres' IOPS: 275
Parent 'postgres' IOPS: 220
Parent 'postgres' IOPS: 275
Parent 'postgres' IOPS: 220
Parent 'postgres' IOPS: 347
Parent 'postgres' IOPS: 262
Parent 'postgres' IOPS: 219
Parent 'postgres' IOPS: 275
Parent 'postgres' IOPS: 220
Parent 'postgres' IOPS: 331
Parent 'postgres' IOPS: 220
Parent 'postgres' IOPS: 220
Parent 'postgres' IOPS: 275
Parent 'postgres' IOPS: 220
Parent 'postgres' IOPS: 389
Parent 'postgres' IOPS: 220
Parent 'postgres' IOPS: 275
Parent 'postgres' IOPS: 219
Parent 'postgres' IOPS: 220
Parent 'postgres' IOPS: 275
Parent 'postgres' IOPS: 222
```

Plotting data as a histogram: ![Histogram of IOps distribution](results/local-path/iops_unequal0.png)

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

# Errors:
* measuring time between read and close does not make sense; these are unrelated
* measuring the time between clone and wait4 measures the process runtime, not any other latency (process runtime includes e.g. io latency of course).
* when the db is too small, all the lines can be cached and read from cache -> when looking at IOps using iostat, none are recorded.