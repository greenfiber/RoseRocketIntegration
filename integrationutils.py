from secretprod import secrets as pw
import requests
class RoseRocketIntegrationUtils():
   
    def authorg(self,whcode):
        authurl = 'https://auth.roserocket.com/oauth2/token'
        authheader = {'Accept': 'application/json'}

        params = {
            "grant_type": "password",
            "username": pw.rruser,
            "password": pw.rrpw,
            "client_id": pw.orgs[whcode]['clientid'],
            "client_secret": pw.orgs[whcode]['secretid']


        }

        r = requests.post(authurl, json=params, headers=authheader)
        resp = r.json()
        
        print("AUTHRESP: {}".format(resp))
        # print("Token: {}".format(resp['data']['access_token']))
        pw.orgs[whcode]['accesstoken'] = resp['data']['access_token']
        return pw.orgs[whcode]['accesstoken']
    def formatdateforreport(self, data):
        import pytz
        from datetime import timedelta
        try:
            fd = datetime.strptime(data, '%Y%m%d')
            local = pytz.timezone("America/New_York")
            localized = local.localize(fd, is_dst=None)
            utc = localized.astimezone(pytz.utc)+timedelta(hours=6)
            return str(utc.isoformat())
        except Exception as e:
            #print("error in formatting date ")
            logging.error("Format date error {}".format(e))