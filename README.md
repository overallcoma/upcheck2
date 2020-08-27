This tool monitors the uptime of a target web server and reports to Twitter when outages occur.

Additionally includes speedtest monitoring and outage tracking.

#Environment Vars
* `RUN_MODE`
  * **`internal`** - The monitored web service
  * **`external`** - The monitoring service  
* **`TZ`** - Set timezone
* **External Run Mode Environment Vars**
  * **`MONITOR_URL`** - The URL to monitor for for status
    * ex; `http://mydynamicdnsurl.com`
  * **`TWITTER_API_KEY`** - Twitter API Key
  * **`TWITTER_API_SECRET`** - Twitter API Secret
  * **`TWITTER_ACCESS_TOKEN`** - Twitter Access Token
  * **`TWITTER_ACCESS_SECRET`** - Twitter Access Token Secret 
