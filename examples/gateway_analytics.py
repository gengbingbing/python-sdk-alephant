import os

from alephantai import AlephantAnalyticsClient

client = AlephantAnalyticsClient(api_key=os.environ["ALEPHANT_VK"])
print(client.usage_summary(period="7d"))
