''' Configuration '''
interval = 10           # number of minutes between completion of a test and starting a new one
outfile = "results.txt" # the path/file to output results in
show_res = False         # show result after each test?

'''	Dependencies:
		speedtest			pip3 install speedtest-cli
'''

''' Program '''
from time import localtime, sleep
import json
import threading

try:
	# import the speedtest module from speedtest-cli
	import speedtest as st
except ImportError:
	print("\nFailed to import module \"speedtest\". You can install it with:")
	print("\tpip3 install speedtest-cli")
	exit()

results = list()
num_to_day = { # will be used to translate a day (from time.localtime)
	0: "Monday",
	1: "Tuesday",
	2: "Wednesday",
	3: "Thursday",
	4: "Friday",
	5: "Saturday",
	6: "Sunday"
}
def bits_to_megabits(bits) -> float:
	return bits/1000/1000

def run_speedtest(printRes) -> dict:
	'''
		Runs a speed test and returns a dictionary result
	'''
	t = st.Speedtest()

	start = localtime()
	ping = t.results.ping
	up = bits_to_megabits(t.upload())
	dn = bits_to_megabits(t.download())
	end = localtime()
	
	# assemble tuple
	result = {
		"ping": ping,
		"upload": up,
		"download": dn,
		"t_started": { 
			"weekday": start[6],
			"hour": start[3],
			"minute": start[4],
			"second": start[5]
		},
		"t_finished": { 
			"weekday": end[6],
			"hour": end[3],
			"minute": end[4],
			"second": end[5]
		}
	}

	if printRes:
		# print the results of the most recent test
		print(f"\tPing: %d ms" % ping)
		print(f"\tDown: %.2f Mbps" % dn)
		print(f"\t  Up: %.2f Mbps" % up)
	
	return result

def make_time_string(result) -> str:
	'''
		Creates a 24-hour time string (hh:mm) from a given speedtest result
	'''
	hour = result["t_started"]["hour"]
	minute = result["t_started"]["minute"]
	if hour < 10:
		string = "0" + str(hour)
	else:
		string = str(hour)

	string += ":"

	if minute < 10:
		string += "0" + str(minute)
	else:
		string += str(minute)

	return string

def create_stat_string(name, average, best, worst, unit="") -> str:
	'''
		Creates a string to be printed that displays the best, worst, and average of
		a given statistic in a human-readable format
	'''
	t_best = make_time_string(best_ping_result)
	t_worst = make_time_string(worst_ping_result)

	string = "\t" + name + "\n"
	string += ("\t\tAverage: %.2f" % average) + f"{unit}\n"
	string += ("\t\t   Best: %.2f" % best) + f"{unit} (Time: " +  t_best + ")\n"
	string += ("\t\t  Worst: %.2f" % worst) + f"{unit} (Time: " + t_worst + ")\n"

	return string

if __name__ == "__main__":
	completed = 0
	print("Running network speed tests. Use [Ctrl/Cmd + C] to stop data collection.")

	while (True):
		try:
			results.append(run_speedtest(show_res))
			print(f"Completed tests: {completed + 1}", end="\n")

			completed += 1
			sleep(60 * interval)

		except KeyboardInterrupt:
			print("Stopping data collection. Please wait for data compilation.")
			break

	res_by_day = dict()
	for result in results:
		if result["t_started"]["weekday"] not in res_by_day.keys():
			res_by_day[result["t_started"]["weekday"]] = list()

		res_by_day[result["t_started"]["weekday"]].append(result)

	stats_by_day = dict()
	for day in range(0, 7):
		if day not in res_by_day.keys():
			continue

		# stats for each weekday
		count = len(res_by_day[day])

		worst_ping_result = res_by_day[day][0]
		best_ping_result = res_by_day[day][0]
		avg_ping = 0

		best_up_result = res_by_day[day][0]
		worst_up_result = res_by_day[day][0]
		avg_up = 0

		best_down_result = res_by_day[day][0]
		worst_down_result = res_by_day[day][0]
		avg_down = 0

		# determine the day's stats
		for result in res_by_day[day]:
			ping = result["ping"]
			up = result["upload"]
			down = result["download"]

			# ping -> lower is better
			if (worst_down_result["ping"] < ping):
				worst_ping_result = result
			if (ping < best_ping_result["ping"]):
				best_ping_result = result
			avg_ping += ping

			# upload -> higher is better
			if (up < worst_up_result["upload"]):
				worst_up_result = result
			if (best_up_result["upload"] < up):
				best_up_result = result
			avg_up += up

			# download -> higher is better
			if (down < worst_down_result["download"]):
				worst_down_result = result
			if (best_down_result["download"] < down):
				best_down_result = result
			avg_down += down

		avg_ping = float(avg_ping) / count
		avg_up = float(avg_up) / count
		avg_down = float(avg_down) / count

		# store the day's stats
		stats_by_day[num_to_day[day]] = {
			"ping": {
				"best": best_ping_result,
				"worst": worst_ping_result,
				"average": avg_ping
			},
			"upload": {
				"best": best_up_result,
				"worst": worst_up_result,
				"average": avg_up
			},
			"download": {
				"best": best_down_result,
				"worst": worst_down_result,
				"average": avg_down
			}
		}

		# output the stats of the weekday
		print(f"Stats for {num_to_day[day]}:")
		best_ping = best_ping_result["ping"]
		worst_ping = worst_ping_result["ping"]
		print(create_stat_string("Ping", avg_ping, best_ping, worst_ping, unit="ms"))

		best_up = best_up_result["upload"]
		worst_up = worst_up_result["upload"]
		print(create_stat_string("Upload", avg_up, best_up, worst_up, unit="Mbps"))

		best_down = best_down_result["download"]
		worst_down = worst_down_result["download"]
		print(create_stat_string("Download", avg_down, best_down, worst_down, unit="Mbps"))

	with(open("results.txt", "w")) as out:
		final_results = {
			"stats": stats_by_day,
			"datapoints": results
		}
		out.write(json.dumps(final_results, indent=4))

	print("Data has been logged in /results.txt")