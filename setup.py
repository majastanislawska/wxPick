from setuptools import setup, find_packages

DATA_FILES = ['src']
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'NSCameraUsageDescription': "This app requires camera access to see what your PNP machine's camera sees",
    },
}

setup(
    name="wxPick",
    version="0.1",
    packages=find_packages(
        where='src',  # '.' by default
        include=['mypackage*'],
        exclude=['test*']
    ),
    app=['wxPick.py'],
    data_files=['src/','lib/'],
    include_package_data=True,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
