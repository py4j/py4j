import os
import shutil
from pathlib import Path
import subprocess

from setuptools import setup
from setuptools.command.sdist import sdist as _sdist
from setuptools.errors import SetupError
from setuptools_scm import get_version
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel


ROOT = Path(__file__).parent.resolve()
JAVA_DIR = ROOT / "py4j-java"
PYTHON_DIR = ROOT / "py4j-python"


def _load_version() -> str:
    return get_version(root=ROOT, relative_to=__file__)


def _jar_path(version: str) -> Path:
    return PYTHON_DIR / "py4j-java" / f"py4j{version}.jar"


def _build_jar(version: str) -> Path:
    jar = _jar_path(version)
    if jar.exists():
        return jar

    gradle_cmd = "gradlew.bat" if os.name == "nt" else "./gradlew"
    source_jar = JAVA_DIR / "py4j*.jar"
    try:
        # Only build and copy the Java jar; skip Python/doc builds.
        subprocess.check_call([gradle_cmd, "copyMainJar"], cwd=JAVA_DIR)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SetupError(f"Unable to build Py4J Java gateway jar via Gradle: {exc}") from exc

    jar_candidates = sorted(JAVA_DIR.glob("py4j*.jar"), reverse=True)
    if not jar_candidates:
        raise SetupError(f"Expected jar to be generated at {source_jar}")
    built_jar = jar_candidates[0]

    jar.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(built_jar, jar)
    return jar


class _BuildJarMixin:
    """Ensure the Java gateway jar exists before packaging artifacts."""

    def ensure_jar(self) -> Path:
        version = _load_version()
        jar = _jar_path(version)
        if not jar.exists():
            self.announce(f"Building Java gateway jar for version {version}", level=2)
            jar = _build_jar(version)
        return jar


class sdist(_BuildJarMixin, _sdist):
    def run(self) -> None:
        self.ensure_jar()
        super().run()


class bdist_wheel(_BuildJarMixin, _bdist_wheel):
    def run(self) -> None:
        self.ensure_jar()
        super().run()


cmdclass = {
    "sdist": sdist,
    "bdist_wheel": bdist_wheel,
}


version = _load_version()
jar_file = _jar_path(version)
jar_file_rel = os.path.relpath(jar_file, ROOT)

setup(
    cmdclass=cmdclass,
    data_files=[("share/py4j", [jar_file_rel])],
)
