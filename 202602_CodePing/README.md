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

## 📖 Read the Full Story on Medium
[**Stop Babysitting Your Notebooks: How I Taught VS Code to Ping Me on Teams**](https://medium.com/@t40r417/stop-babysitting-your-notebooks-how-i-taught-vs-code-to-ping-me-on-teams-e11e40a7c14f
)
