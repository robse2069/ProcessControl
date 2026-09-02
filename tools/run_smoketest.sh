cd /github/ProcessControl
git pull

cd /docker/processcontrol
docker compose up -d
docker compose exec robot robot test/smoke_test.robot

cd /docker/processcontrol
docker compose down