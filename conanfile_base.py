from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os
import glob


class BaseHeaderOnly(ConanFile):
    homepage = "https://www.x.org/wiki/"
    license = "X11"
    url = "https://github.com/bincrafters/conan-x11"
    author = "Bincrafters <bincrafters@gmail.com>"
    settings = "os", "arch", "compiler", "build_type"
    _source_subfolder = "source_subfolder"

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

    def _format_cflags(self, dep):
        includes = self.deps_cpp_info[dep].include_paths
        includes = ["-I%s" % include for include in includes]
        return " ".join(includes)

    def _format_ldflags(self, dep):
        libs = self.deps_cpp_info[dep].libs
        libs = ["-l%s" % lib for lib in libs]
        lib_paths = self.deps_cpp_info[dep].lib_paths
        lib_paths = ["-L%s" % lib_path for lib_path in lib_paths]
        return " ".join(libs + lib_paths)

    def build(self):
        with tools.chdir(self._source_subfolder):
            args = ["--disable-dependency-tracking"]
            args.extend(self._configure_args)
            env_build = AutoToolsBuildEnvironment(self)
            env_build_vars = env_build.vars
            if "freetype" in self.deps_cpp_info.deps:
                env_build_vars["FREETYPE_CFLAGS"] = self._format_cflags("freetype")
                env_build_vars["FREETYPE_LIBS"] = self._format_ldflags("freetype")
            if "fontconfig" in self.deps_cpp_info.deps:
                env_build_vars["FONTCONFIG_CFLAGS"] = self._format_cflags("fontconfig")
                env_build_vars["FONTCONFIG_LIBS"] = self._format_ldflags("fontconfig")
            env_build.configure(vars=env_build_vars, args=args, pkg_config_paths=self.deps_cpp_info.build_paths)
            env_build.make(vars=env_build_vars)
            env_build.install(vars=env_build_vars, args=["-j1"])


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
