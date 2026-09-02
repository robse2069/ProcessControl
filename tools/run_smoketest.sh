cd /home/pi/github/ProcessControl
git pull

cd /home/pi/docker/processcontrol
docker compose up -d
docker compose exec robot robot test/smoke_test.robot

cd /home/pi/docker/processcontrol
docker compose down