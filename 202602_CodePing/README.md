# CodePing

Get Microsoft Teams notifications when your code is done running.

## 📋 Prerequisites
- A Microsoft Teams workflow webhook URL

## Use It
```python
from notification import notify_teams

# Do your thing...

# Get notified when done
notify_teams()
```

Returns `True` if successful, `False` if it fails (check your logs).


## 📝 Example
Check `test.py` for a working example that waits 5 seconds then pings Teams.

---

