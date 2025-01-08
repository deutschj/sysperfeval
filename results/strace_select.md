### Tracing select statement with strace

To find out which systemcalls are done when a postgres select statement happens, I used strace. I'm planning to later measure the IO latency during a query using the systemcalls, that the select statement calls.

I created a table with 500 000 lines and used the following select statement:

`SELECT * FROM table_name;`

Using strace on the postgresql parent PID yielded the following results:

`strace -f -e trace=all -p 3708884
strace: Process 3708884 attached
epoll_wait(9, 0x55e597d2d658, 4, 47101) = -1 EINTR (Interrupted system call)
--- SIGUSR1 {si_signo=SIGUSR1, si_code=SI_USER, si_pid=65, si_uid=999} ---
getpid()                                = 1
kill(1, SIGURG)                         = 0
rt_sigreturn({mask=[URG]})              = -1 EINTR (Interrupted system call)
getpid()                                = 1
rt_sigprocmask(SIG_SETMASK, ~[ILL TRAP ABRT BUS FPE SEGV CONT SYS RTMIN RT_1], [URG], 8) = 0
clone(child_stack=NULL, flags=CLONE_CHILD_CLEARTID|CLONE_CHILD_SETTID|SIGCHLD, child_tidptr=0x7fbc5d339d50) = 104013
strace: Process 3936174 attached
[...]
[pid 3936174] read(6, "\27'Y\0\21\0\0\0\353\4\0\0\353\4\0\0\341\4\0\0\341\4\0\0\347\4\0\0\347\4\0\0"..., 524) = 524
[pid 3936174] close(6)                  = 0
[pid 3936174] openat(AT_FDCWD, "base/1/pg_internal.init", O_RDONLY) = 6
[pid 3936174] newfstatat(6, "", {st_mode=S_IFREG|0600, st_size=158340, ...}, AT_EMPTY_PATH) = 0
[pid 3936174] read(6, "f2W\0\350\1\0\0\0\0\0\0\177\6\0\0\1\0\0\0m\n\0\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0\0\0\0\0\0\0\0\0h\0\0\0\0\0\0\0\257\0\0\0umuser\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0\0\0\0\0\0\0\0\0\1\0\0\0\0\0\0\0\0\0\0\0\214\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0\0\0\0\0\0\0\0\0\23\0\0\0@\0\2\0\377\377\377\377\377\377\377\377\0\0\0c"..., 4096) = 4096
[pid 3936174] read(6, "\274\177\0\0\0\244\340\227\345U\0\0 \245\340\227\345U\0\0(\246\340\227\345U\0\08\246\340\227"..., 4096) = 4096
[pid 3936174] read(6, "h7\342\227\345U\0\0x7\342\227\345U\0\0\2107\342\227\345U\0\0\2607\342\227\345U\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0\343\10\0\0\376\377\1\0\0\0\0\0\377\377\377\377\0\0\0cp\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "condefault\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\350\1\0\0\0\0\0\0\177\6\0\0\1\0\0\0\26\r\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0:\3\0\0defaclnamespace\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\32\0\0\0\4\0\1\0\0\0\0\0\377\377\377\377\0\0\1ip\0\1\0\0\0\0\0\1\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\22\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\274\177\0\0\0 \341\227\345U\0\0 !\341\227\345U\0\0(\"\341\227\345U\0\0@\"\341\227"..., 4096) = 4096
[pid 3936174] read(6, "\345U\0\0(\332\341\227\345U\0\08\332\341\227\345U\0\0H\332\341\227\345U\0\0p\332\341\227"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\32\0\0\0\4\0\2\0"..., 4096) = 4096
[pid 3936174] read(6, "\177\6\0\0\1\0\0\0\23\16\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\377\377\377\377"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0\32\0\0\0\1\0\0\0\0\0\0\0\275\7\0\0h\0\0\0\1\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] mmap(NULL, 266240, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7fbc53ffb000
[pid 3936174] read(6, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "h\0\0\0\0\0\0\0(\n\0\0aggminitval\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0\22\0\0\0\1\0\n\0\377\377\377\377\377\377\377\377\0\0\1cp\0\1\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0g\1\0\0?\f\0\0\0\0\0\0\272\23\0\0\0\0\0\0\10\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\345U\0\0`\342\341\227\345U\0\0x\342\341\227\345U\0\0`\344\341\227\345U\0\0h\350\341\227"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0\0\0\0\0\0\0\0\0\25\0\0\0\2\0\n\0\377\377\377\377\377\377\377\377\0\0\1s"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] brk(0x55e597e41000)       = 0x55e597e41000
[pid 3936174] read(6, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\345U\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0\1\0\0\0p\0\0\0\1\0\0\0\0\0\0\0\32\0\0\0\1\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\341\4\0\0\0\0\0\0 \n\341\227\345U\0\0\1\0\0\0\377\377\377\377\0\1\1\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\v\0\0\0\0\0\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\350\1\0\0"..., 4096) = 4096
[pid 3936174] read(6, "\246\0\0\0\0\0\1\0B\0\0\0002\n\0\0\0\220\0T\274\177\0\0002\0\0\0\0\0\0\0"..., 4096) = 2692
[pid 3936174] read(6, "", 4096)         = 0
[pid 3936174] close(6)                  = 0
[pid 3936174] openat(AT_FDCWD, "base/1/2601", O_RDWR|O_CLOEXEC) = 6
[pid 3936174] lseek(6, 0, SEEK_END)     = 8192
[pid 3936174] openat(AT_FDCWD, "base/1/1259", O_RDWR|O_CLOEXEC) = 7
[pid 3936174] lseek(7, 0, SEEK_END)     = 114688
[pid 3936174] lseek(7, 0, SEEK_END)     = 114688
[pid 3936174] brk(0x55e597e62000)       = 0x55e597e62000
[pid 3936174] lseek(7, 0, SEEK_END)     = 114688
[pid 3936174] getpid()                  = 104013
[pid 3936174] munmap(0x7fbc5405d000, 1048576) = 0
[pid 3936174] getpid()                  = 104013
[pid 3936174] kill(65, SIGUSR2)         = 0
[pid 3936174] futex(0x7fbc60b165d8, FUTEX_WAKE_PRIVATE, 2147483647) = 0
[pid 3936174] exit_group(0)             = ?
[pid 3936174] +++ exited with 0 +++
 <detached ...>`

The read() and close() systemcalls are visible; I'll try to use these for latency measurement.

### Measuring time between read() and close()

Following up I measured the time between the read() and close() syscalls filtering by the Postgres PID, using bpftrace:

```text
PID: 3957814 Latency between read and close: 13303 ns
PID: 3957814 Latency between read and close: 1030 ns
PID: 3957814 Latency between read and close: 51277 ns
PID: 3957814 Latency between read and close: 8942 ns
PID: 3957814 Latency between read and close: 2420 ns
PID: 3957814 Latency between read and close: 1973 ns
PID: 3957814 Latency between read and close: 5289 ns
PID: 3878649 Latency between read and close: 23855668 ns
PID: 3957815 Latency between read and close: 3170 ns
PID: 3957815 Latency between read and close: 7027 ns
PID: 3957815 Latency between read and close: 1854 ns
PID: 3957815 Latency between read and close: 41833 ns
PID: 3957815 Latency between read and close: 8385 ns
PID: 3957815 Latency between read and close: 2555 ns
PID: 3957815 Latency between read and close: 1401 ns
PID: 3957815 Latency between read and close: 9808 ns
PID: 3878649 Latency between read and close: 40491687 ns
PID: 3957922 Latency between read and close: 2582 ns
PID: 3957922 Latency between read and close: 2538 ns
PID: 3957922 Latency between read and close: 5667 ns
PID: 3957922 Latency between read and close: 4096 ns
PID: 3957922 Latency between read and close: 1602 ns
PID: 3957922 Latency between read and close: 5535 ns
PID: 3957923 Latency between read and close: 2161 ns
PID: 3957923 Latency between read and close: 2658 ns
PID: 3957923 Latency between read and close: 5308 ns
PID: 3957923 Latency between read and close: 3578 ns
PID: 3957923 Latency between read and close: 1103 ns
PID: 3957923 Latency between read and close: 5469 ns
PID: 3878649 Latency between read and close: 1418293300 ns
PID: 3878649 Latency between read and close: 17154 ns
PID: 3958083 Latency between read and close: 3588 ns
PID: 3958083 Latency between read and close: 8587 ns
PID: 3958083 Latency between read and close: 1184 ns
PID: 3958083 Latency between read and close: 32214 ns
PID: 3958083 Latency between read and close: 8564 ns
PID: 3958083 Latency between read and close: 2539 ns
PID: 3958083 Latency between read and close: 2350 ns
PID: 3958083 Latency between read and close: 5734 ns
PID: 3878649 Latency between read and close: 24256531 ns
PID: 3958084 Latency between read and close: 2800 ns
PID: 3958084 Latency between read and close: 6885 ns
PID: 3958084 Latency between read and close: 1368 ns
PID: 3958084 Latency between read and close: 37764 ns
PID: 3958084 Latency between read and close: 7819 ns
PID: 3958084 Latency between read and close: 2346 ns
PID: 3958084 Latency between read and close: 1252 ns
PID: 3958084 Latency between read and close: 5052 ns
```

Latency outliers can be noticed, so I decided to print the time measurements as a histogram, using BPFtrace as well:

```text
@latency:
[0]                    1 |@@                                                  |
[1]                   11 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                      |
[2, 4)                16 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@         |
[4, 8)                19 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[8, 16)                3 |@@@@@@@@                                            |
[16, 32)               2 |@@@@@                                               |
[32, 64)               2 |@@@@@                                               |
[64, 128)              0 |                                                    |
[128, 256)             0 |                                                    |
[256, 512)             0 |                                                    |
[512, 1K)              0 |                                                    |
[1K, 2K)               0 |                                                    |
[2K, 4K)               0 |                                                    |
[4K, 8K)               0 |                                                    |
[8K, 16K)              0 |                                                    |
[16K, 32K)             2 |@@@@@                                               |
[32K, 64K)             0 |                                                    |
[64K, 128K)            0 |                                                    |
[128K, 256K)           0 |                                                    |
[256K, 512K)           1 |@@                                                  |
[512K, 1M)             0 |                                                    |
[1M, 2M)               0 |                                                    |
[2M, 4M)               0 |                                                    |
[4M, 8M)               1 |@@                                                  |
```

In the latency histogram, the "outliers" can be seen (these are the slow select queries that I fired using pgbench), the other read() statements in the 1-64us range are others that postgres does in the process.

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

Important: when using the local-volume-provisioner, there are no block devices created. Instead, directory-based volumes are used -> we have to trace systemcalls like read() or write() instead of using block tracepoints.

We can observe a bi-modal distribution when looking at time from read() to close():

```
@latency:
[0]                    6 |                                                    |
[1]                  589 |@@@@@@@@@@@@@@@@@@@@@@@                             |
[2, 4)              1300 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[4, 8)              1291 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ |
[8, 16)               50 |@@                                                  |
[16, 32)              12 |                                                    |
[32, 64)              25 |@                                                   |
[64, 128)              0 |                                                    |
[128, 256)             0 |                                                    |
[256, 512)             0 |                                                    |
[512, 1K)              0 |                                                    |
[1K, 2K)               0 |                                                    |
[2K, 4K)               1 |                                                    |
[4K, 8K)               1 |                                                    |
[8K, 16K)              1 |                                                    |
[16K, 32K)            15 |                                                    |
[32K, 64K)             4 |                                                    |
[64K, 128K)           10 |                                                    |
[128K, 256K)         481 |@@@@@@@@@@@@@@@@@@@                                 |
[256K, 512K)           9 |                                                    |
[512K, 1M)             0 |                                                    |
[1M, 2M)               0 |                                                    |
[2M, 4M)               2 |                                                    |
[4M, 8M)               0 |                                                    |
[8M, 16M)              1 |                                                    |
```

I ran the query 500 times, 482 of which had a latency of about ~220ms. The other read() statements in the 1-8us range are most probably smaller read operations, that are performed in the course of the query processing.
