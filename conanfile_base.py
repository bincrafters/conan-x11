from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os
import glob
import shutil


class BaseHeaderOnly(ConanFile):
    homepage = "https://www.x.org/wiki/"
    license = "X11"
    url = "https://github.com/bincrafters/conan-x11"
    author = "Bincrafters <bincrafters@gmail.com>"
    settings = "os", "arch", "compiler", "build_type"
    _source_subfolder = "source_subfolder"
    generators = "pkg_config"

    def package_info(self):
        self.cpp_info.builddirs.extend([os.path.join("share", "pkgconfig"),
                                        os.path.join("lib", "pkgconfig")])

    def package_id(self):
        self.info.header_only()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)

    @property
    def _configure_args(self):
        return []

    def build(self):
        for package in self.deps_cpp_info.deps:
            lib_path = self.deps_cpp_info[package].rootpath
            for dirpath, _, filenames in os.walk(lib_path):
                for filename in filenames:
                    if filename.endswith('.pc'):
                        shutil.copyfile(os.path.join(dirpath, filename), filename)
                        tools.replace_prefix_in_pc_file(filename, lib_path)
        if os.path.exists('zlib.pc'):
            os.rename('zlib.pc', 'ZLIB.pc')

        with tools.chdir(self._source_subfolder):
            args = ["--disable-dependency-tracking"]
            args.extend(self._configure_args)
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(args=args, pkg_config_paths=self.build_folder)
            env_build.make()
            env_build.install(args=["-j1"])


class BaseLib(BaseHeaderOnly):
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def configure(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    @property
    def _configure_args(self):
        if self.options.shared:
            return ["--disable-static", "--enable-shared"]
        else:
            return ["--disable-shared", "--enable-static"]

    def package(self):
        super(BaseLib, self).package()
        libdir = os.path.join(self.package_folder, "lib")
        if os.path.isdir(libdir):
            with tools.chdir(libdir):
                # libtool *.la files have hard-coded paths
                for filename in glob.glob("*.la"):
                    os.unlink(filename)
                # libXaw has broken symlinks
                if not self.options.shared:
                    for filename in glob.glob("*.dylib"):
                        os.unlink(filename)
                    for filename in glob.glob("*.so"):
                        os.unlink(filename)
                    for filename in glob.glob("*.so.*"):
                        os.unlink(filename)

    def package_id(self):
        pass
