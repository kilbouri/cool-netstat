# cool-netstat
A Python program to collect network data, including best, worst, and average network speeds and ping.

### Usage
Written in Python, no build is required! Just run it with `python cool_netstat.py` and let it collect data!
It will run speedtests on 10-minute intervals, logging data such as measured upload/download speeds and ping.
Once you're done collecting data, send a keyboard interrupt (`Ctrl + C` (Windows/Linux) or `Command + C` (Mac)) to
stop data collection. The program will sort through the collected data, determining weekday-based best/worst/average 
speeds and ping. The program will also write the results (and all data points) to `results.txt`.

### Dependencies
Speedtest-cli is needed for running speed tests. Install with
```
pip3 install speedtest-cli
```


### Configuration
You can specify operating parameters within the module, such as:
- `interval`: how much time to put between each speed test
- `outfile`: where to output the results
- `show_res`: if `True`, the results of each test will be logged to STD_OUT