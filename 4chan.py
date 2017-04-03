import urllib, urllib2, time, json, random, math, sched
 
# COORDINATES TO ATTACK
center = []
 
 
# COLOR TO PLACE - 3 IS BLACK MOTHERFUCKERS
void_color = 3
 
# ------------------------------------------------------------------------
 
print "All hail the Void"
 
xy = raw_input("Enter where you want to center your attack in the form x, y-> ")
center.append(int(xy.split(",")[0]))
center.append(int(xy.split(",")[1]))
 
radius = int(raw_input("Enter the radius of your attack "))
 
print "For each account you want to use, enter it in like username:password"
print "When you're done, type 'done'"
 
accounts = []
 
while True:
    user_input = raw_input("Account-> ")
    if user_input.lower() != 'done' and user_input != '':
        accounts.append(user_input)
    else:
        break
 
# ------------------------------------------------------------------------
 
print "Getting user agent list for anonymity (please wait)"
user_agent_list=list(set([ua for ua in urllib.urlopen("https://raw.githubusercontent.com/sqlmapproject/sqlmap/master/txt/user-agents.txt").read().splitlines() if not ua.startswith("#")]))
 
# Store session tokens instead of getting a new one every single time (inefficient) like the old version did
sessions = {}
 
def genSessions( accountlist ):
    opener = urllib2.build_opener()
    opener.addheaders = [('User-Agent', random.choice(user_agent_list))]
    for account in accountlist:
        username = account.split(":")[0]
        password = ':'.join(account.split(":")[1:])
        data = urllib.urlencode({'op': 'login-main', 'user': username, 'passwd': password, 'api_type': 'json'})
        time.sleep(random.randrange(0, 10))
        rawresp = opener.open('https://www.reddit.com/api/login/'+urllib.quote(username), data).read()
        response = json.loads(rawresp)
        if not response['json'].get('errors'):
            print "Adding session for " + username
            sessions[username] = response['json']['data']['cookie']
        else:
            print 'Error: connection problem for account: '+ username
            print response
            continue
 
 
def main( accounts ):
    print "Running Build the Void"
 
    while True:
        # Fill the void
        opener = urllib2.build_opener()
        ua = random.choice(user_agent_list)
        for session in sessions.keys():
            cookie = sessions[session]
            color = 3
            while color == void_color:
                # Find a non-black square
                xtest = center[0]+random.randint(-radius,radius)
                ytest = center[1]+random.randint(-radius,radius)
                if math.sqrt((center[0] - xtest)**2 + (center[1] - ytest)**2) > radius:
                    continue
                else:
                    time.sleep(random.randrange(0, 4))
                    print "Testing", xtest, ytest, "..."
                    opener.addheaders = [('User-Agent', ua)]
                    opener.addheaders.append(('Cookie', 'reddit_session=' + cookie))
                    resp = opener.open("https://www.reddit.com/api/place/pixel.json?x="+str(xtest)+"&y="+str(ytest)).read()
                    try:
                        color = int(json.loads(resp)["color"])
                    except Exception, e:
                        color = 3
            print "Found a non-void color at", str(xtest), str(ytest)
            data = urllib.urlencode({'x': xtest, 'y': ytest, 'color': void_color})
            newopener = urllib2.build_opener()
            newopener.addheaders = [('User-Agent', ua)]
            newopener.addheaders.append(('Cookie', 'reddit_session=' + cookie))
            # print "Pulling me.json"
            time.sleep(random.randrange(0, 5))
            modhash = json.loads(newopener.open("https://reddit.com/api/me.json").read())["data"]["modhash"]
            newopener.addheaders.append(('x-modhash', modhash))
            # print "Pulling draw.json"
            time.sleep(random.randrange(0, 5))
            next=newopener.open("https://www.reddit.com/api/place/draw.json", data).read()
            # print next
            # print "Pulling pixel.json a second time..."
            time.sleep(random.randrange(0, 5))
            finalresp = newopener.open("https://www.reddit.com/api/place/pixel.json?x="+str(xtest)+"&y="+str(ytest)).read()
            if session in finalresp:
                print "Added successfully"
                # time.sleep(15)
            else:
                print finalresp
        print "All accounts on cooldown. Sleeping..."
        time.sleep(300 + random.randrange(0, 25))
 
 
# ------------------------------------------------------------------------
 
# If any problem occurs, keep retrying forever. All hail the void.
genSessions( accounts )
while True:
    # TODO: Keep track of individual account cooldowns. Currently if an account in the queue has a cooldown the others after it aren't tried until that cooldown is finished
    try:
        main( accounts )
    except Exception as e:
        if str(e) == "HTTP Error 502: Bad Gateway":
            print '502 error! Reddit being shit as always!'
            print 'Retrying in 2 seconds...'
            time.sleep(2)
        elif str(e) == "HTTP Error 403: Forbidden":
            print '403 error! Likely an account is shadow banned!'
            time.sleep(2)
        else:
            print 'Error: ' + str(e) + '\n'
            print '429 error! Account is on cooldown.'
            print 'Retrying in 15 seconds'
            time.sleep(15)
