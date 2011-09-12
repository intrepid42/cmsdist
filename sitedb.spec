### RPM cms sitedb 2.0.0
## INITENV +PATH PATH %i/xbin
## INITENV +PATH PYTHONPATH %i/$PYTHON_LIB_SITE_PACKAGES
## INITENV +PATH PYTHONPATH %i/x$PYTHON_LIB_SITE_PACKAGES
## INITENV SETV SITEDB_LEGACY_PYTHONPATH %i/legacy

%define webdoc_files %i/doc/
%define cvssrc cvs://:pserver:anonymous@cmscvs.cern.ch:2401/cvs_server/repositories/CMSSW?passwd=AA_:yZZ3e
%define svnsrc svn://svn.cern.ch/reps/CMSDMWM/SiteDB/tags/%{realversion}
%define svnwmc svn://svn.cern.ch/reps/CMSDMWM/WMCore/tags/0.7.4
Source0: %{svnwmc}?scheme=svn+ssh&strategy=export&module=WMCore&output=/wmcore_sitedb.tar.gz
Source1: %{svnsrc}?scheme=svn+ssh&strategy=export&module=SiteDB&output=/sitedb.tar.gz
Source2: %{cvssrc}&strategy=export&module=WEBTOOLS&nocache=true&export=WEBTOOLS&tag=-rSiteDBv1-slc5-v3&output=/old-sitedb.tar.gz
Source3: %{cvssrc}&strategy=export&module=WEBTOOLS&nocache=true&export=WEBTOOLS&tag=-rV01-03-47&output=/old-webtools.tar.gz
Requires: cherrypy yui py2-cx-oracle py2-cjson rotatelogs protovis py2-sphinx
Requires: py2-cheetah py2-pysqlite py2-formencode py2-pycrypto beautifulsoup py2-sqlalchemy oracle-env py2-pyopenssl
# ^ = line for legacy SiteDB support, remove when migrating fully to sitedb 2.x

%prep
%setup -T -b 0 -n WMCore
%setup -D -T -b 1 -n SiteDB
perl -p -i -e "s{<VERSION>}{%{realversion}}g" doc/conf.py
%setup -D -T -c -a 2 -n LEGACY-SITEDB
rm -f WEBTOOLS/Applications/SiteDB/Utilities/MigrateSites # requires phedex
rm -f WEBTOOLS/Applications/SiteDB/Schema/writergrants.py
%setup -D -T -c -a 3 -n LEGACY-WEBTOOLS
rm -rf WEBTOOLS/{Applications,Configuration,Tools/StartupScripts}
rm -fr WEBTOOLS/SecurityModule/{perl,crypttest}

%build
cd ../WMCore
python setup.py build_system -s wmc-web
cd ../SiteDB
python setup.py build_system

%install
mkdir -p %i/{doc,etc/profile.d} %i/{x,}{bin,lib,data} %i/{x,}$PYTHON_LIB_SITE_PACKAGES
cd ../WMCore
python setup.py install_system -s wmc-web --prefix=%i
cd ../SiteDB
python setup.py install_system --prefix=%i
find %i -name '*.egg-info' -exec rm {} \;

cd ../LEGACY-WEBTOOLS/WEBTOOLS
mkdir -p %i/legacy
cp -r * %i/legacy
cp cmsWeb %i/bin

cd ../../LEGACY-SITEDB/WEBTOOLS
mkdir -p %i/legacy/Applications
cp -r Applications/SiteDB %i/legacy/Applications
mkdir -p %i/legacy/Applications/SiteDB/csv

python -m compileall %i/legacy || true

# Generate dependencies-setup.{sh,csh} so init.{sh,csh} picks full environment.
: > %i/etc/profile.d/dependencies-setup.sh
: > %i/etc/profile.d/dependencies-setup.csh
for tool in $(echo %{requiredtools} | sed -e's|\s+| |;s|^\s+||'); do
  root=$(echo $tool | tr a-z- A-Z_)_ROOT; eval r=\$$root
  if [ X"$r" != X ] && [ -r "$r/etc/profile.d/init.sh" ]; then
    echo "test X\$$root != X || . $r/etc/profile.d/init.sh" >> %i/etc/profile.d/dependencies-setup.sh
    echo "test X\$$root != X || source $r/etc/profile.d/init.csh" >> %i/etc/profile.d/dependencies-setup.csh
  fi
done

# Generate an env.sh which sets a few things more than init.sh.
(echo ". %i/etc/profile.d/init.sh;"
 echo "export YUI_ROOT PROTOVIS_ROOT SITEDB_ROOT;") > %i/etc/profile.d/env.sh

%post
%{relocateConfig}etc/profile.d/{env,dep*}.*sh

%files
%i/
%exclude %i/doc

## SUBPACKAGE webdoc
