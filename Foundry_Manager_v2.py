import requests
from bottle import route, run, template,ServerAdapter,redirect
import subprocess
from html.parser import HTMLParser
import threading
import time

ssl_cert=None #XYZ - 'fullchain.pem'
ssl_key=None #XYZ - 'privkey.pem'


world_mapping={"URL_Path":["world-folder","Name To Be Shown"], "URL_Path2":["world-folder-2","Name To Be Shown Two: Electric Boogaloo"]} #XYZ - Repeatable until the HTML page doesn't handle it.
foundry_base="http://blank.com" #XYZ
foundry_port=30000 #XYZ
foundry_url=foundry_base+":"+str(foundry_port)
foundry_directory="C:\Program Files\FoundryVTT" #XYZ - The directory has to point to /resources/app

idle_logout=300 #XYZ- Seconds - time to shut down foundry if at login screen and 0 users
##Populate this automatically from module configuration, can probably get pictures etc but who has time?



class SSLWrapper(ServerAdapter):
    def __init__(self, ssl_certfile = None, ssl_keyfile = None, host='0.0.0.0', port=8080):
        self._ssl_certfile = ssl_certfile
        self._ssl_keyfile = ssl_keyfile
        
        super().__init__(host, port)
        
    
    def run(self, handler):
        from  cheroot.ssl.builtin import BuiltinSSLAdapter
        from cheroot import wsgi
        server = wsgi.Server((self.host, self.port), handler)  
        self.srv = server
        
        if server.ssl_adapter is not None:
        	server.ssl_adapter = BuiltinSSLAdapter(self._ssl_certfile, self._ssl_keyfile)
        try:  
            server.start()  
        finally:  
            server.stop()  
                
    def shutdown(self):
        self.srv.stop()




class AwfulScrape_nPlayers(HTMLParser):
    #This is why javascript was invented 
    
    def __init__(self):
        super().__init__()
        
        
        self.in_label=False #We are searching for a "Current Players:" label
        self.previous_label_players=False  #If we found it, grab the first input field 
        self.nPlayers=None  #If nothing is found crash 
        
    def handle_starttag(self, tag, attrs):
        if tag == "label":
            self.in_label=True
        if (tag == "input") and self.previous_label_players:
            self.nPlayers=int(dict(attrs)["value"])
            self.previous_label_players=False

            
    def handle_endtag(self, tag):
        if tag == "label":
            self.in_label=False
        if tag == "header":
            self.in_header=False

    def handle_data(self, data):
        if self.in_label:
            if "Current Players:" in data:  
                self.previous_label_players=True
            else:
                self.previous_label_players=False


## A bunch of threading stuff 

class monitorPlayers(object):
    def __init__(self, foundry_proccess):
        self.foundry_proccess = foundry_proccess

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = False
        thread.start()      

    def run(self):
        #Keep checking number of players 
        #If it's been 0 for 5 minutes, return to setup 

        zero_players=False
        while True:
            n_players=get_logged_in_players(timeout=30.) #Returns "None" if in setup etc so it's safe
            if (n_players == 0) and zero_players:
                self.foundry_proccess.send_signal(2)
                self.foundry_proccess.send_signal(2) ##I think I need to send this twice? 
                self.foundry_proccess.wait()
                break
                
            time.sleep(idle_logout) #Wait five minutes 
            if n_players == 0:
                
                zero_players=True
            else:
                zero_players=False
        server.start()
        

class runServer(object):
    def __init__(self):
        self.server=SSLWrapper(ssl_certfile = ssl_cert, ssl_keyfile = ssl_key,port=foundry_port)

        thread = threading.Thread(target=self.run, args=([self.server]))
        thread.daemon = False                      
        thread.start()                                 
    def run(self,server):
        run(server=server) ##This isn't a cruel practical joke - the second run refers to bottle.run (I'll remove the uglyness in the future)


class bottleManager: #this is bascially just a global variable
    def __init__(self): 
        self.bottle_server=runServer()
    def shutdown(self):
        self.bottle_server.server.shutdown()
        self.bottle_server = None
    def start(self):
        self.bottle_server=runServer()


        
class startFoundryWorld(object):
    def __init__(self, world):
        self.world = world

        thread = threading.Thread(target=self.run, args=([world]))
        thread.daemon = False                            
        thread.start()                                 

    def run(self,world):
        server.shutdown()
        process_obj= subprocess.Popen(["node","main.js","--port=30000", "--dataPath=C:\Users\XYZ\AppData\Local\FoundryVTT\Data","--world=%WORLD%".replace("%WORLD%",world)],cwd=foundry_directory) #XYZ - The --dataPath MUST direct to the FoundryVTT data folder (where worlds reside)
        import time 
        time.sleep(12)
        monitorPlayers(process_obj)

def get_logged_in_players(timeout=0.1):
    r=requests.get(foundry_url+"/join",timeout=timeout)

    par=AwfulScrape_nPlayers()
    par.feed(r.text)
    return par.nPlayers

def _get_world_url(item):
    return "<p> &gt; <a href='/"+item[0]+"' >" + item[1][1]+"</a> </p>"

@route('/')
@route('/<world>')
def index(world=None):
    if (world == "join") or (world is None):

        return  """<!DOCTYPE html>
        <html>
        <title>Foundry World Select</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Signika">
        <style>
        body,h1 {font-family: "Signika", sans-serif}
        body, html {height: 100%;
          background-color: #3f403f;}
        .bgimg {
        min-height: 100%;
        background-position: center;
        background-size: cover;
        }
        </style>
        <body>

        <div class="bgimg w3-display-container w3-animate-opacity w3-text-white">
        <div class="w3-display-topleft w3-padding-large w3-xlarge">
            Welcome to Dimitri's Foundry Selection Screen!
        </div>
        <div class="w3-display-middle">
            <h1 class="w3-jumbo w3-animate-top"> <strong> """+"".join([_get_world_url(x) for x in world_mapping.items()]) +"""  </strong></h1>
            <hr class="w3-border-grey" style="margin:auto;width:40%">
            <p class="w3-large w3-center">This will start your selected world and you will be able to login.</p>
        </div>
        </div>

        </body>
        </html>
        """
                     
    requested_world_path,requested_world = world_mapping.get(world,[None,None])
    
    if requested_world is None:
        return template('<h1>Cannot find world <b> {{world}} </b></h1>',world=world)

    startFoundryWorld(requested_world_path)
    return  """<!DOCTYPE html>
        <html>
        <title>Foundry World Select</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Signika">
        <style>
        body,h1 {font-family: "Signika", sans-serif}
        body, html {height: 100%;
          background-color: #3f403f;}
        .bgimg {
        min-height: 100%;
        background-position: center;
        background-size: cover;
        }
        @keyframes blink {
        /**
        * At the start of the animation the dot
        * has an opacity of .2
        */
        0% {
        opacity: .2;
        }
        /**
        * At 20% the dot is fully visible and
        * then fades out slowly
        */
        20% {
        opacity: 1;
        }
        /**
        * Until it reaches an opacity of .2 and
        * the animation can start again
        */
        100% {
        opacity: .2;
        }
    }

    .saving span {
        /**
        * Use the blink animation, which is defined above
        */
        animation-name: blink;
        /**
        * The animation should take 1.4 seconds
        */
        animation-duration: 1.4s;
        /**
        * It will repeat itself forever
        */
        animation-iteration-count: infinite;
        /**
        * This makes sure that the starting style (opacity: .2)
        * of the animation is applied before the animation starts.
        * Otherwise we would see a short flash or would have
        * to set the default styling of the dots to the same
        * as the animation. Same applies for the ending styles.
        */
        animation-fill-mode: both;
    }

    .saving span:nth-child(2) {
        /**
        * Starts the animation of the third dot
        * with a delay of .2s, otherwise all dots
        * would animate at the same time
        */
        animation-delay: .2s;
    }

    .saving span:nth-child(3) {
        /**
        * Starts the animation of the third dot
        * with a delay of .4s, otherwise all dots
        * would animate at the same time
        */
        animation-delay: .4s;
}
        </style>
        <body>

        <div class="bgimg w3-display-container w3-animate-opacity w3-text-white">
        <div class="w3-display-topleft w3-padding-large w3-xlarge">
            Welcome to DnD!
        </div>
        <div class="w3-display-middle">
            <h1 class="w3-jumbo w3-animate-top"> <strong><p class="saving">Loading <span>.</span><span>.</span><span>.</span></p> </strong></h1>
        </div>
        </div>

        </body>
       

      <script>
        var timer = setTimeout(function() {
            window.location='"""+foundry_url+"""'
        }, 12000); 
     </script>
    </html>
        """ #XYZ - Edit the scripts 12000 milisecond timer depending on your machine.
        # This value determines how long the page waits before refreshing and hopefully redirecting the user to the Foundry login page 
        # (if it's too fast, the page will break and you will have to refresh until Foundry is turned on, too long... you just waste time.)
server=bottleManager()
