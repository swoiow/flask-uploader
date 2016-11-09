A simple demo of flask upload
===
Base on [Plupload](https://github.com/moxiecode/plupload) and [Flask](https://github.com/pallets/flask)

+ Cross-browser multi-runtime file upload (cause plupload)
+ Support drag and drop
+ Support large files
+ MD5 checksum before upload
+ Support Broken-point Continuingly-transferring

### RUN
0. Run testcase in order to initdb.

  `python testcase.py`

0. Then

  `python wsgi.py`

0. Open browser with <http://localhost:5000>

  `demo demo`
