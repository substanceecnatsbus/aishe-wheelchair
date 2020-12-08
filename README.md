# installation
## server
```
pip install -r requirements.txt
```

# running
## server
```
$ python server --log_set [comma separated log_set enum] --record [True|False] --mode [inference|data gathering]
```
### log_set enum
- ecg
- gsr
- pm
- wm
- features
- inference
- discomfort-level