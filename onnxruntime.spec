%global utf8_range_commit 72c943dea2b9240cd09efde15191e144bc7c7d38
%global utf8_range_name utf8_range-%( echo %utf8_range_commit | cut -c1-7 )

%bcond test 1

%global backends cpu

Summary:    A cross-platform inferencing and training accelerator
Name:       onnxruntime
Version:    1.20.1
Release:    1
License:    MIT and ASL-2.0 and Boost and BSD
URL:        https://github.com/microsoft/onnxruntime
Source0:    https://github.com/microsoft/onnxruntime/archive/v%{version}/%{name}-%{version}.tar.gz

# Add an option to not install the tests
Patch:      0000-dont-install-tests.patch
# Use the system flatbuffers
Patch:      0001-system-flatbuffers.patch
# Use the system protobuf
Patch:      0002-system-protobuf.patch
# Use the system onnx
Patch:      0003-system-onnx.patch
# Fedora targets power8 or higher
Patch:      0004-disable-power10.patch
# Do not use nsync
Patch:      0005-no-nsync.patch
# Do not link against WIL
Patch:      0006-remove-wil.patch
# Use the system safeint
Patch:      0007-system-safeint.patch
# Versioned libonnxruntime_providers_shared.so
Patch:      0008-versioned-onnxruntime_providers_shared.patch
# Disable gcc -Werrors with false positives
Patch:      0009-gcc-false-positive.patch
# Test data not available 
Patch:      0010-disable-pytorch-tests.patch
# Use the system date and boost
Patch:      0011-system-date-and-mp11.patch
# Use the system cpuinfo
Patch:      0012-system-cpuinfo.patch
# Trigger onnx fix for onnxruntime_providers_shared
Patch:      0013-onnx-onnxruntime-fix.patch
# Use the system python version
Patch:      0014-system-python.patch
# Fix errors when DISABLE_ABSEIL=ON
#Patch:      0015-abseil-disabled-fix.patch
# Fix missing includes
Patch:      0016-missing-cpp-headers.patch
# Revert https://github.com/microsoft/onnxruntime/pull/21492 until
# Fedora's Eigen3 is compatible with the fix.
Patch:      0017-revert-nan-propagation-bugfix.patch
# Backport upstream implementation of onnx
# from https://github.com/microsoft/onnxruntime/pull/21897
Patch:      0019-backport-onnx-1.17.0-support.patch
Patch:      0020-disable-locale-tests.patch
Patch:      0021-fix-range-loop-construct.patch
Patch:      0022-onnxruntime-convert-gsl-byte-to-std-byte.patch

Patch:		onnxruntime-compile.patch

BuildRequires:  cmake
BuildRequires:  make
BuildRequires:	cmake(onnx)
BuildRequires:  pkgconfig(absl_any)
BuildRequires:  boost-devel >= 1.66
BuildRequires:  bzip2

#BuildRequires:  pkgconfig(libcpuinfo)

# Need update
BuildRequires:  pkgconfig(date)
# This one too
BuildRequires:  flatbuffers
BuildRequires:  pkgconfig(flatbuffers) >= 23.5.26
BuildRequires:	%{_lib}flatbuffers-static-devel
BuildRequires:  pkgconfig(gmock)
BuildRequires:  pkgconfig(gsl)
BuildRequires:  pkgconfig(gtest)
BuildRequires:  cmake(microsoft.gsl)
BuildRequires:  pkgconfig(nlohmann_json)
BuildRequires:  pkgconfig(protobuf)
BuildRequires:  pkgconfig(python3)
BuildRequires:  python3
BuildRequires:  python-numpy
BuildRequires:  python-setuptools
BuildRequires:  python-wheel
BuildRequires:  python-pip
BuildRequires:  pkgconfig(re2)
BuildRequires:  safeint-devel
BuildRequires:  pkgconfig(zlib)
Buildrequires:  pkgconfig(eigen3)
BuildRequires:  pkgconfig(pybind11)
BuildRequires:	pkgconfig(libcpuinfo)

%description
%{name} is a cross-platform inferencing and training accelerator compatible
with many popular ML/DNN frameworks, including PyTorch, TensorFlow/Keras,
scikit-learn, and more.

%package devel
Summary:    The development part of the %{name} package
Requires:   %{name}%{_isa} = %{version}-%{release}

%description devel
The development part of the %{name} package

%package -n python-onnxruntime
Summary:    %{summary}
Requires:   %{name}%{_isa} = %{version}-%{release}

%description -n python-onnxruntime
Python bindings for the %{name} package

%package doc
Summary:    Documentation files for the %{name} package
BuildArch:  noarch

%description doc
Documentation files for the %{name} package

%prep
%autosetup -p1
# Use the system version of abseil-cpp
sed -r -i 's/(FIND_PACKAGE_ARGS[[:blank:]]+)[0-9]{8}/\1/' \
    cmake/external/abseil-cpp.cmake

# Re-compile flatbuffers schemas with the system flatc
python onnxruntime/core/flatbuffers/schema/compile_schema.py --flatc /usr/bin/flatc
python onnxruntime/lora/adapter_format/compile_schema.py --flatc /usr/bin/flatc

%build
cd cmake
%cmake -G Ninja \
	-Donnxruntime_BUILD_BENCHMARKS=OFF \
	-Donnxruntime_BUILD_SHARED_LIB=ON \
	-Donnxruntime_BUILD_UNIT_TESTS=OFF \
	-Donnxruntime_ENABLE_PYTHON=ON \
	-DPYTHON_VERSION=%{pyver} \
	-Donnxruntime_DISABLE_ABSEIL=ON \
	-Donnxruntime_USE_FULL_PROTOBUF=ON \
	-Donnxruntime_USE_NEURAL_SPEED=OFF \
-Donnxruntime_USE_PREINSTALLED_EIGEN=ON \
	-Deigen_SOURCE_PATH=/usr/include/eigen3 \
	-Donnxruntime_ENABLE_CPUINFO=ON \
	-Donnxruntime_INSTALL_UNIT_TESTS=OFF

%ninja_build

cd ../..
# Build python libs
mv ./onnxruntime ./onnxruntime.src
cp -a cmake/build/onnxruntime ./onnxruntime
cp cmake/build/requirements.txt ./requirements.txt
%py_build
mv onnxruntime onnxruntime.bin
mv onnxruntime.src onnxruntime

%install
%ninja_install -C cmake/build

mkdir -p "%{buildroot}/%{_docdir}/"
cp --preserve=timestamps -r "./docs/" "%{buildroot}/%{_docdir}/%{name}"

%py_install

ln -s "../../../../libonnxruntime_providers_shared.so.%{version}" "%{buildroot}/%{python3_sitearch}/onnxruntime/capi/libonnxruntime_providers_shared.so"

%files
%license LICENSE
%doc ThirdPartyNotices.txt
%{_libdir}/libonnxruntime.so.%{version}
%{_libdir}/libonnxruntime_providers_shared.so.%{version}

%files devel
%dir %{_includedir}/onnxruntime/
%{_includedir}/onnxruntime/*
%{_libdir}/libonnxruntime.so*
%{_libdir}/libonnxruntime_providers_shared.so
%{_libdir}/pkgconfig/libonnxruntime.pc
%{_libdir}/cmake/onnxruntime/*

%files -n python-onnxruntime
%{_bindir}/onnxruntime_test
%{python3_sitearch}/onnxruntime-%{version}.dist-info
%{python3_sitearch}/onnxruntime

%files doc
%doc %{_docdir}/%{name}
