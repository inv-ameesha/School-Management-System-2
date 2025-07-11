from django.db import migrations

def truncate_students_teachers(apps, schema_editor):
    Student = apps.get_model('people', 'Student')
    Teacher = apps.get_model('people', 'Teacher')
    Student.objects.all().delete()
    Teacher.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('people', '0003_student_user')
    ]

    operations = [
        migrations.RunPython(truncate_students_teachers),
    ]
