from integration import RoseRocketIntegration  
from backend import RoseRocketIntegrationBackend
from secretprod import secrets as pw


if __name__ == "__main__":
    rr = RoseRocketIntegration()
    rr.updatesync()