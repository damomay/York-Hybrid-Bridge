# Sprint 2.7.1 — York Packet Classifier

Run:

```sh
python /app/york_packet_classifier.py
```

Optional classified copies, still observed and non-executable:

```sh
python /app/york_packet_classifier.py \
  --apply-dir /config/york_protocol/packet_library/classified
```

Reports are written to `/reports/classification`.

The classifier cannot promote a packet to verified or safe-to-transmit status.
