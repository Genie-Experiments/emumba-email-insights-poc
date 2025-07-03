import yaml
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def load_config(config_file="config.yaml"):
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    return config


class OutlookConfig:
    def __init__(
        self,
        name,
        client_id,
        tenant_id,
        client_secret,
        scope,
        failover=None,
    ):
        self.name = name
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.client_secret = client_secret
        self.scope = scope
        self.failover = failover

    def __repr__(self):
        failover_repr = f", failover={self.failover}" if self.failover else ""
        return (
            f"OutlookConfig(name={self.name}, client_id={self.client_id}, "
            f"tenant_id={self.tenant_id}, client_secret={self.client_secret}, "
            f"scope={self.scope}, {failover_repr})"
        )


config_data = load_config(
    "config.yaml"
)

failover_config = config_data.get("failover", None)

outlook_config = OutlookConfig(
    name=config_data["source"]["name"],
    client_id=config_data["source"]["client_id"],
    tenant_id=config_data["source"]["tenant_id"],
    client_secret=config_data["source"]["client_secret"],
    scope=config_data["source"]["scope"],
    failover=failover_config,
)

if outlook_config.failover:
    logging.info("Failover section is present in the config. Handling failover logic.")
else:
    logging.info("No failover section. Proceeding with regular script execution.")
