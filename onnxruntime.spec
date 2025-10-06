%global utf8_range_commit 72c943dea2b9240cd09efde15191e144bc7c7d38
%global utf8_range_name utf8_range-%( echo %utf8_range_commit | cut -c1-7 )

%bcond test 1

%global backends cpu

Summary:    A cross-platform inferencing and training accelerator
Name:       onnxruntime
Version:    1.23.0
Release:    1
License:    MIT and ASL-2.0 and Boost and BSD
URL:        https://github.com/microsoft/onnxruntime
Source0:    https://github.com/microsoft/onnxruntime/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  make
BuildRequires:	cmake(onnx)
BuildRequires:	cmake(date)
BuildRequires:	cmake(Eigen3)
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

%patchlist
https://data.gpo.zugaina.org/guru/sci-libs/onnxruntime/files/onnxruntime-1.22.2-relax-the-dependency-on-flatbuffers.patch
# based on https://data.gpo.zugaina.org/guru/sci-libs/onnxruntime/files/onnxruntime-1.22.2-use-system-libraries.patch
onnxruntime-1.22.2-use-system-libraries.patch
onnxruntime-system-eigen.patch
abseil-cpp-2508.patch
onnxruntime-c++20.patch
onnxruntime-1.21.1-clang.patch
onnxruntime-1.23.0-clang.patch

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
	-Dsafeint_SOURCE_DIR=%{_includedir}/SafeInt \
	-Donnxruntime_ENABLE_CPUINFO=ON \
	-Donnxruntime_INSTALL_UNIT_TESTS=OFF \
	-Donnxruntime_ENABLE_DLPACK:BOOL=OFF \
	-DCMAKE_CXX_STANDARD=20

%ninja_build

cd ../..

# Build python libs (they need files from an in-tree build...)
cp -r cmake/build/onnxruntime/* onnxruntime
%py_build

%install
%ninja_install -C cmake/build

mkdir -p "%{buildroot}/%{_docdir}/"
cp --preserve=timestamps -r "./docs/" "%{buildroot}/%{_docdir}/%{name}"

%py_install

%files
%license LICENSE
%doc ThirdPartyNotices.txt
%{_libdir}/libonnxruntime.so.%{version}
%{_libdir}/libonnxruntime_providers_shared.so

%files devel
%dir %{_includedir}/onnxruntime/
%{_includedir}/onnxruntime/*
%{_libdir}/libonnxruntime.so*
%{_libdir}/pkgconfig/libonnxruntime.pc
%{_libdir}/cmake/onnxruntime/*

%files -n python-onnxruntime
%{_bindir}/onnxruntime_test
%{python3_sitearch}/onnxruntime-%{version}.dist-info
%{python3_sitearch}/onnxruntime

%files doc
%doc %{_docdir}/%{name}
