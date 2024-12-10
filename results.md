## Running fio and observing IO latency

Using biolatency on the mounted disk (sde, the Kubernetes mount on the host):

```bash
ideweiiss8508:/usr/share/bcc/tools # ./biolatency -d sde
Tracing block device I/O... Hit Ctrl-C to end.
^C
     usecs               : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 0        |                                        |
         4 -> 7          : 0        |                                        |
         8 -> 15         : 0        |                                        |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 0        |                                        |
        64 -> 127        : 0        |                                        |
       128 -> 255        : 0        |                                        |
       256 -> 511        : 4        |                                        |
       512 -> 1023       : 19976    |                                        |
      1024 -> 2047       : 895601   |****************************************|
      2048 -> 4095       : 323932   |**************                          |
      4096 -> 8191       : 20611    |                                        |
      8192 -> 16383      : 1544     |                                        |
     16384 -> 32767      : 68       |                                        |
```

The same can be done using bpftrace, bpftrace_iolatency.bt script:

```bash
# cat bpftrace_iolatency.bt
#!/usr/bin/env bpftrace

tracepoint:block:block_rq_issue /pid == $1/ {
  @start[pid] = nsecs;
}

tracepoint:block:block_rq_complete /pid == $1 && @start[pid]/
{
  @us[pid] = hist((nsecs - @start[pid]) / 1000000);
  delete(@start[pid]);
}
```

With the fio PID attached:

```bash
# ./bpftrace_iolatency.bt 654526
Attaching 2 probes...
^C

@start[654526]: 5053340483333133
@us[654526]:
[0]                    1 |@@@@@@@@@@@@@@@@@@@@@@@@@@                          |
[1]                    1 |@@@@@@@@@@@@@@@@@@@@@@@@@@                          |
[2, 4)                 2 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[4, 8)                 0 |                                                    |
[8, 16)                0 |                                                    |
[16, 32)               0 |                                                    |
[32, 64)               0 |                                                    |
[64, 128)              0 |                                                    |
[128, 256)             1 |@@@@@@@@@@@@@@@@@@@@@@@@@@                          |
[256, 512)             0 |                                                    |
[512, 1K)              0 |                                                    |
[1K, 2K)               0 |                                                    |
[2K, 4K)               1 |@@@@@@@@@@@@@@@@@@@@@@@@@@                          |
```
// why are the results so different?

Opensnoop results (files that the fio process opens):

```bash
# pgrep fio | xargs -I{} ./opensnoop -p {}
PID    COMM               FD ERR PATH
931449 fio                 4   0 /sys/block/sde/stat
931449 fio                 4   0 /sys/block/sde/stat
931449 fio                 4   0 /sys/block/sde/stat
931449 fio                 4   0 /sys/block/sde/stat
931449 fio                 4   0 /sys/block/sde/stat
931449 fio                 4   0 /sys/block/sde/stat
```

## Benchmarking with pgbench

##### Script that gets pgbench PID, and traces block_rq_(issue|insert|complete) tracepoints (IOps):

```bash
#!/usr/bin/env bpftrace

BEGIN
{
    printf("Monitoring for new `pgbench` process creations...\n");
}

// Trace process creation (execve)
tracepoint:syscalls:sys_enter_execve
/comm == "pgbench"/
{
    @target_pid = pid; // Store the `pgbench` PID
    printf("pgbench started with PID: %d\n", pid);
}

// Trace block requests when they are inserted into the queue
tracepoint:block:block_rq_insert
/@target_pid && pid == @target_pid/
{
    printf("INSERT: PID=%d, dev=%d:%d, sector=%llu, bytes=%u, rw=%s\n",
           pid,
           args->dev >> 20, args->dev & 0xfffff, // Major and minor device numbers
           args->sector,
           args->nr_sector * 512, // Sector size in bytes
           args->rwbs);
}

// Trace block requests when they are issued to the device
tracepoint:block:block_rq_issue
/@target_pid && pid == @target_pid/
{
    printf("ISSUE: PID=%d, dev=%d:%d, sector=%llu, bytes=%u, rw=%s\n",
           pid,
           args->dev >> 20, args->dev & 0xfffff,
           args->sector,
           args->nr_sector * 512,
           args->rwbs);
}

// Trace block requests when they are completed
tracepoint:block:block_rq_complete
/@target_pid && pid == @target_pid/
{
    printf("COMPLETE: PID=%d, dev=%d:%d, sector=%llu, bytes=%u, result=%d\n",
           pid,
           args->dev >> 20, args->dev & 0xfffff,
           args->sector,
           args->nr_sector * 512,
           args->error);
}
```

##### Script Results:

```text
# ./blk_io.bt
Attaching 5 probes...
Monitoring for new `pgbench` process creations...
pgbench started with PID: 3449590
INSERT: PID=3449590, dev=8:0, sector=46387496, bytes=16384, rw=RA
ISSUE: PID=3449590, dev=8:0, sector=46387496, bytes=16384, rw=RA
INSERT: PID=3449590, dev=8:0, sector=46387528, bytes=184320, rw=RA
ISSUE: PID=3449590, dev=8:0, sector=46387528, bytes=184320, rw=RA
INSERT: PID=3449590, dev=8:0, sector=29863448, bytes=4096, rw=RA
ISSUE: PID=3449590, dev=8:0, sector=29863448, bytes=4096, rw=RA
INSERT: PID=3449590, dev=8:0, sector=29484856, bytes=4096, rw=RM
INSERT: PID=3449590, dev=8:0, sector=29864976, bytes=16384, rw=RA
ISSUE: PID=3449590, dev=8:0, sector=29864976, bytes=16384, rw=RA
INSERT: PID=3449590, dev=8:0, sector=29865008, bytes=12288, rw=RA
ISSUE: PID=3449590, dev=8:0, sector=29865008, bytes=12288, rw=RA
INSERT: PID=3449590, dev=8:0, sector=29469376, bytes=4096, rw=RM
INSERT: PID=3449590, dev=8:0, sector=62505400, bytes=282624, rw=RA
ISSUE: PID=3449590, dev=8:0, sector=62505400, bytes=282624, rw=RA
INSERT: PID=3449590, dev=8:0, sector=62506024, bytes=57344, rw=RA
ISSUE: PID=3449590, dev=8:0, sector=62506024, bytes=57344, rw=RA
INSERT: PID=3449590, dev=8:0, sector=62506136, bytes=36864, rw=RA
ISSUE: PID=3449590, dev=8:0, sector=62506136, bytes=36864, rw=RA
COMPLETE: PID=3449590, dev=8:0, sector=62506136, bytes=36864, result=0
INSERT: PID=3449590, dev=8:0, sector=71849440, bytes=12288, rw=RA
ISSUE: PID=3449590, dev=8:0, sector=71849440, bytes=12288, rw=RA
COMPLETE: PID=3449590, dev=8:16, sector=53178064, bytes=8192, result=0
COMPLETE: PID=3449590, dev=8:32, sector=2447400, bytes=4096, result=0
COMPLETE: PID=3449590, dev=8:64, sector=6938832, bytes=8192, result=0
```

##### biolatency pgbench results

time=30, clients=1, jobs=1

```bash
# ./biolatency -m -d sde -e
Tracing block device I/O... Hit Ctrl-C to end.
^C
     msecs               : count     distribution
         0 -> 1          : 17603    |****************************************|
         2 -> 3          : 2897     |******                                  |
         4 -> 7          : 654      |*                                       |
         8 -> 15         : 33       |                                        |
        16 -> 31         : 1        |                                        |
        32 -> 63         : 0        |                                        |
        64 -> 127        : 1        |                                        |

avg = 0 msecs, total: 15563 msecs, count: 21189
```

clients=10:

```bash
# ./biolatency -m -d sde -e
Tracing block device I/O... Hit Ctrl-C to end.
^C
     msecs               : count     distribution
         0 -> 1          : 57666    |****************************************|
         2 -> 3          : 41545    |****************************            |
         4 -> 7          : 4833     |***                                     |
         8 -> 15         : 295      |                                        |
        16 -> 31         : 31       |                                        |
        32 -> 63         : 159      |                                        |
        64 -> 127        : 46       |                                        |
       128 -> 255        : 27       |                                        |

avg = 1 msecs, total: 175444 msecs, count: 104602
```

With bpftrace: filter by device and pgbench PID, get block_rq_issue and block_rq_complete events -> then calculate difference in time between them:

Script can be found [here](scripts/blk_debug.bt)

```bash
# cat out1.log
Attaching 4 probes...
Monitoring pgbench for I/O latency...
pgbench started with PID: 471595
ISSUE: PID=471595, sector=46387496, dev=8388608
COMPLETE: sector=46387496, latency=198461 ns
ISSUE: PID=471595, sector=46387528, dev=8388608
COMPLETE: sector=46387528, latency=458844 ns
ISSUE: PID=471595, sector=29864976, dev=8388608
COMPLETE: sector=29864976, latency=189674 ns
ISSUE: PID=471595, sector=29865008, dev=8388608
COMPLETE: sector=29865008, latency=171986 ns
```

Add up latencies: `198461 + 458844 + 189674 + 171986 ns = 1018965 ns = 1,02ms`

However pgbench itself reports a latency avg of 2,87ms:

```text
pgbench (17.0 (Debian 17.0-1.pgdg110+1))
[...]
latency average = 2.873 ms
initial connection time = 9.289 ms 
tps = 348.055502 (without initial connection time)
```

Reference: biolatency without pgbench load

```bash
# ./biolatency -m -d sde -e
Tracing block device I/O... Hit Ctrl-C to end.
^C
     msecs               : count     distribution
         0 -> 1          : 297      |*****************                       |
         2 -> 3          : 675      |****************************************|
         4 -> 7          : 28       |*                                       |

avg = 1 msecs, total: 1909 msecs, count: 1000
```
