from setuptools import setup

plist = dict(
    NSPrincipalClass='Trashie',
    LSBackgroundOnly=True
)

setup(
    app=["trashie.py"],
    options=dict(py2app=dict(
      plist=plist, 
      resources='trash-empty.png, trash-full.png')),
    setup_requires=["py2app"],
)