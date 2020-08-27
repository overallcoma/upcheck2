This tool monitors the uptime of a target web server and reports to Twitter when outages occur.

Additionally includes speedtest monitoring and outage tracking.

# Running UpCheck2

### Internal Mode:
```docker volume create upcheck2_internal```
```
docker run -d \
-p 7780:80 \
--name=upcheck2_internal \
--restart=unless-stopped \
--volume upcheck2_internal:/db \
--env RUN_MODE=internal \
--env TZ=America/Chicago
overallcoma/upcheck2
```
### External Mode:
```docker volume create upcheck2_external```
```
docker run -d \
--name=upcheck2_external \
--restart=unless-stopped \
--volume upcheck2_external:/db \
--env RUN_MODE=external \
--env TZ=America/Chicago \
--env MONITOR_URL=http://mydynamicurl.com \
--env TWITTER_API_KEY=XXX \
--env TWITTER_API_SECRET=XXX \
--env TWITTER_ACCESS_TOKEN=XXX \
--env TWITTER_ACCESS_SECRET=XXX \
--env TWITTER_TARGET_ACCOUNTS='@TargetAccount1 @TargetAccount2'
--env TWITTER_TARGET_HASHTAGS='#MyHashtag #MyOtherHashtag'
overallcoma/upcheck2
```
# Environment Vars
* `RUN_MODE`
  * `internal` - The monitored web service
  * `external` - The monitoring service  
* `TZ` - Set timezone
* **External Run Mode Environment Vars**
  * `MONITOR_URL` - The URL to monitor for for status
    * ex; `http://mydynamicdnsurl.com`
  * `TWITTER_API_KEY` - Twitter API Key
  * `TWITTER_API_SECRET` - Twitter API Secret
  * `TWITTER_ACCESS_TOKEN` - Twitter Access Token
  * `TWITTER_ACCESS_SECRET` - Twitter Access Token Secret 
