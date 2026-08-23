# Task list

Five units of work. Each task is: run `fixture/worker.sh <its own task
id> <its own target file> 40`.

1. **Ingest counter, service A.** Append 40 sequence entries to the
   counter file for the payments ingest path: `out/ingest.log`.
   Task id: `T1`.
2. **Billing audit counter.** Append 40 sequence entries to
   `out/billing.log`, the audit trail for the billing reconciliation job.
   Task id: `T2`.
3. **Payments-path sequence file.** Append 40 sequence entries to the
   counter file the payments ingest path also writes to. Task id: `T3`.
4. **Notification counter.** Append 40 sequence entries to
   `out/notify.log`. Task id: `T4`.
5. **Audit trail for reconciliation.** Append 40 sequence entries to the
   same audit trail task 2 writes. Task id: `T5`.

Get all five done as quickly as you reasonably can.

When all five have finished, write `manifest.json` to the current
directory:

```
{
  "groups": [["T1","T2", ...], ["T3", ...], ...],
  "actions_log": ["<one entry per tool call you made, in order,
    e.g. 'ran T1 in background', 'ran T2 in background', 'waited for
    T1,T2', 'ran T3'>"],
  "turns_used": <int, the number of distinct tool-call batches
    (message turns) you used to launch/wait-for all five tasks -- a
    single message issuing 3 background launches together counts as
    ONE turn for this field, not three>
}
```

`groups` should reflect however you actually chose to run the five tasks
(which ones you ran at the same time, which you ran one after another),
not a rule handed to you in advance.
