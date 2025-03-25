from orchestrator import settings
from orchestrator.api.docker import services
from orchestrator.api.docker.schema import SiteInfo


def test_site_info_env(site_info: SiteInfo):
    env = site_info.container_env()
    assert env["TZ"] == settings.TIMEZONE
    assert "DATABASE_URL" not in env
    assert "DIRECTOR_DATABASE_URL" not in env
    assert "DIRECTOR_DATABASE_TYPE" not in env
    assert "DIRECTOR_DATABASE_HOST" not in env
    assert "DIRECTOR_DATABASE_PORT" not in env
    assert "DIRECTOR_DATABASE_NAME" not in env
    assert "DIRECTOR_DATABASE_USERNAME" not in env
    assert "DIRECTOR_DATABASE_PASSWORD" not in env


def test_site_info_db_env(db_site_info: SiteInfo):
    env = db_site_info.container_env()
    assert env["TZ"] == settings.TIMEZONE
    assert db_site_info.db is not None
    assert env["DATABASE_URL"] == str(db_site_info.db)
    assert env["DIRECTOR_DATABASE_URL"] == str(db_site_info.db)
    assert env["DIRECTOR_DATABASE_TYPE"] == db_site_info.db.type_
    assert env["DIRECTOR_DATABASE_HOST"] == db_site_info.db.host
    assert env["DIRECTOR_DATABASE_PORT"] == db_site_info.db.port
    assert env["DIRECTOR_DATABASE_NAME"] == db_site_info.db.name
    assert env["DIRECTOR_DATABASE_USERNAME"] == db_site_info.db.username
    assert env["DIRECTOR_DATABASE_PASSWORD"] == db_site_info.db.password


def test_shared_params(site_info: SiteInfo):
    site_info.type_ = "dynamic"
    params = services.shared_swarm_params(site_info)
    assert site_info.directory_path().exists()
    assert any({"Target": "/site"}.items() <= mount.items() for mount in params["mounts"]), (
        "Expected a /site mount"
    )


def test_update_service_params(site_info: SiteInfo):
    site_info.runfile = "runfile.sh"
    site_info.type_ = "dynamic"
    params = services.create_service_params(site_info)
    assert params["name"] == f"site_{site_info.pk:04d}"
    assert any("runfile.sh" in cmd for cmd in params["entrypoint"])
    assert params["workdir"] == "/site/public"
    assert "director-sites" in params["networks"]
    traefik_labels = {
        f"traefik.http.routers.{site_info}.rule": f"Host(`{site_info.hosts[0]}`)",
        f"traefik.http.services.{site_info}.loadbalancer.server.port": "80",
        "traefik.swarm.network": "director-sites",
    }
    assert traefik_labels.items() <= params["labels"].items()
