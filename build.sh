set -o errexit

pip install -r requirements.txt

cd Almini
python manage.py collectstatic --no-input
python manage.py migrate