#%%
from notification import notify_teams
import time

# Simulate a long-running task (replace this with your actual workload)
time.sleep(5)

# Notify yourself in Microsoft Teams once execution completes
notify_teams()
