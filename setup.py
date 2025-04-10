from setuptools import setup, find_packages

setup(
    name="asset_management",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "Django>=4.2.0",
        "djangorestframework>=3.14.0",
        "django-cors-headers>=4.3.0",
        "django-filter>=23.2",
        "psycopg2-binary>=2.9.6",
        "django-environ>=0.11.2",
        "django-allauth>=0.57.0",
        "dj-rest-auth>=5.0.2",
        "djangorestframework-simplejwt>=5.3.0",
    ],
    python_requires=">=3.8",
) 