from integration import RoseRocketIntegration  
from backend import RoseRocketIntegrationBackend
from secretprod import secrets as pw


if __name__ == "__main__":
    orgs = pw.orgs.keys()
    for org in orgs:
        data=RoseRocketIntegrationBackend().getAllData(org)
        rr = RoseRocketIntegration(org)
        rr.updatesync(org)
        # rr.updatecustomers(data)