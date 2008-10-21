from setuptools import setup

plist = dict(
    NSPrincipalClass='Trashie',
    LSBackgroundOnly=True,
    CFBundleIconFile='trashie',
    NSHumanReadableCopyright='Kunal Anand'
)

setup(
    app=["trashie.py"],
    options=dict(py2app=dict(
      plist=plist, 
      resources='trash-empty.png, trash-full.png, trashie.icns')),
    setup_requires=["py2app"],
)