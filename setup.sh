#!/bin/bash

# ExoHunt Django Setup Script
# Run this to set up the database and create a superuser

echo "🚀 ExoHunt - Django Setup Script"
echo "================================="
echo ""

# Navigate to Django project
cd exodetect

# Check if Django is installed
if ! python -c "import django" &> /dev/null; then
    echo "❌ Django is not installed!"
    echo "Please run: pip install django djangorestframework django-cors-headers"
    exit 1
fi

echo "✅ Django found"
echo ""

# Make migrations
echo "📝 Creating migrations for api app..."
python manage.py makemigrations api

if [ $? -ne 0 ]; then
    echo "❌ Migration creation failed!"
    exit 1
fi

echo ""
echo "🔄 Applying migrations to database..."
python manage.py migrate

if [ $? -ne 0 ]; then
    echo "❌ Migration failed!"
    exit 1
fi

echo ""
echo "✅ Database setup complete!"
echo ""

# Create superuser
echo "👤 Creating superuser account..."
echo "   (Press Ctrl+C to skip if you already have one)"
echo ""
python manage.py createsuperuser

echo ""
echo "================================="
echo "✨ Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Run: python manage.py runserver"
echo "2. Visit: http://localhost:8000/admin/"
echo "3. Test API: http://localhost:8000/api/dashboard/stats/"
echo ""
echo "📚 See API_QUICK_TEST.md for testing commands"
echo "🎨 See IMPLEMENTATION_GUIDE.md for frontend setup"
echo ""
echo "Happy coding! 🚀"
