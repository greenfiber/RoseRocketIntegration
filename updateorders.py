from integration import RoseRocketIntegration  
from backend import RoseRocketIntegrationBackend
from secret import secrets as pw


if __name__ == "__main__":
    orgs = pw.orgs.keys()
    for org in orgs:

        rr = RoseRocketIntegration(org)
        rr.updatesync(org)