
#!/bin/bash
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Change to project directory and run Django commands
cd Almini
python manage.py collectstatic --no-input
python manage.py migrate