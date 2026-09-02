cd /home/pi/github/ProcessControl
git pull

cd /home/pi/docker/processcontrol

docker compose run --rm --network host robot robot test/smoke_test.robot