### RPM external tensorflow-c 1.1.0

Source: none

BuildRequires: tensorflow-sources

%prep

%build


%install

tar xfz ${TENSORFLOW_SOURCES_ROOT}/libtensorflow.tar.gz -C %{i}

