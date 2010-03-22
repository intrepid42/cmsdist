### RPM external hepmc 2.03.06
Source: http://lcgapp.cern.ch/project/simu/HepMC/download/HepMC-%realversion.tar.gz
Patch0: hepmc-2.03.06-gcc43
Patch1: hepmc-2.03.06-reflex

%prep
%setup -q -n HepMC-%{realversion}
%patch0 -p1
%patch1 -p0

./configure --prefix=%{i} 

%build
make 

%install
make install

# SCRAM ToolBox toolfile
mkdir -p %i/etc/scram.d
cat << \EOF_TOOLFILE >%i/etc/scram.d/%n
<doc type=BuildSystem::ToolDoc version=1.0>
<Tool name=HepMC version=%v>
<lib name=HepMCfio>
<lib name=HepMC>
<Client>
 <Environment name=HEPMC_BASE default="%i"></Environment>
 <Environment name=LIBDIR default="$HEPMC_BASE/lib"></Environment>
 <Environment name=INCLUDE default="$HEPMC_BASE/include"></Environment>
</Client>
<Runtime name=CMSSW_FWLITE_INCLUDE_PATH value="$HEPMC_BASE/include" type=path>
</Tool>
EOF_TOOLFILE

%post
%{relocateConfig}etc/scram.d/%n
