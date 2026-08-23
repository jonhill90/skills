# Widget Service

A Python data-processing service that ingests widget telemetry and
computes hourly rollups.

## Setup

```bash
pip install -r requirements.txt
python main.py
```

## Overview

Telemetry arrives as JSON lines on stdin; `main.py` batches, transforms,
and writes rollups to `output/`.
