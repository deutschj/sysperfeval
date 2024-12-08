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

Using my bpftrace_iolatency.bt script:

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

Opensnoop results:

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
