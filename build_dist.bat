@echo off
echo Building Docker images...
docker compose build

echo Saving Docker images...
if not exist "out" mkdir out

echo Saving backend image...
docker save keymanagement-backend:latest -o out\backend-image.tar
echo Saving frontend image...
docker save keymanagement-frontend:latest -o out\frontend-image.tar

echo Creating distribution package...
copy docker-compose.yml out\

cd out
tar -czf keymanagement-dist.tar.gz docker-compose.yml backend-image.tar frontend-image.tar
cd ..

echo Done! Distribution package created at out\keymanagement-dist.tar.gz
