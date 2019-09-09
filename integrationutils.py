from secret import secrets as pw
import requests
class RoseRocketIntegrationUtils():
   
    def authorg(self,whcode):
        authurl = 'https://auth.sandbox01.roserocket.com/oauth2/token'
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