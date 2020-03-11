#!/usr/bin/env python
""" Amazon SageMaker Debugger is an offering from AWS which helps you automate the debugging of machine learning training jobs.
This library powers Amazon SageMaker Debugger, and helps you develop better, faster and cheaper models by catching common errors quickly.
It allows you to save tensors from training jobs and makes these tensors available for analysis, all through a flexible and powerful API.
It supports TensorFlow, PyTorch, MXNet, and XGBoost on Python 3.6+.
- Zero Script Change experience on SageMaker when using supported versions of SageMaker Framework containers or AWS Deep Learning containers
- Full visibility into any tensor which is part of the training process
- Real-time training job monitoring through Rules
- Automated anomaly detection and state assertions
- Interactive exploration of saved tensors
- Distributed training support
- TensorBoard support

"""
# Standard Library
import contextlib
import os
import sys
from datetime import date

# Third Party
import setuptools

# First Party
import smdebug

DOCLINES = (__doc__ or "").split("\n")
FRAMEWORKS = ["tensorflow", "pytorch", "mxnet", "xgboost"]
TESTS_PACKAGES = ["pytest", "torchvision", "pandas"]
INSTALL_REQUIRES = ["protobuf>=3.6.0", "numpy", "packaging", "boto3>=1.10.32"]


def compile_summary_protobuf():
    proto_paths = ["smdebug/core/tfevent/proto"]
    cmd = "set -ex && protoc "
    for proto_path in proto_paths:
        proto_files = os.path.join(proto_path, "*.proto")
        cmd += proto_files + " "
        print("compiling protobuf files in {}".format(proto_path))
    cmd += " --python_out=."
    return os.system(cmd)


@contextlib.contextmanager
def remember_cwd():
    """
    Restore current directory when exiting context
    """
    curdir = os.getcwd()
    try:
        yield
    finally:
        os.chdir(curdir)


def scan_git_secrets():
    from subprocess import check_call
    import os
    from pathlib import Path
    import tempfile

    if os.path.exists(".git/hooks/commit-msg"):
        print("git secrets: commit hook already present")
        return

    def git(*args):
        return check_call(["git"] + list(args))

    with tempfile.TemporaryDirectory(prefix="git_secrets") as tmpdir, remember_cwd():
        os.chdir(tmpdir)
        git("clone", "https://github.com/awslabs/git-secrets.git", tmpdir)
        prefix = str(Path.home())
        manprefix = os.path.join(tmpdir, "man")
        check_call(["make", "install"], env={"PREFIX": prefix, "MANPREFIX": manprefix})
        git("secrets", "--install")
        git("secrets", "--register-aws")


def build_package(version):
    packages = setuptools.find_packages(include=["smdebug", "smdebug.*"])
    setuptools.setup(
        name="smdebug",
        version=version,
        long_description="\n".join(DOCLINES[1:]),
        long_description_content_type="text/x-rst",
        author="AWS DeepLearning Team",
        description=DOCLINES[0],
        url="https://github.com/awslabs/sagemaker-debugger",
        packages=packages,
        classifiers=[
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3 :: Only",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: OS Independent",
        ],
        install_requires=INSTALL_REQUIRES,
        setup_requires=["pytest-runner"],
        tests_require=TESTS_PACKAGES,
        python_requires=">=3.6",
        license="Apache License Version 2.0",
    )


if compile_summary_protobuf() != 0:
    print(
        "ERROR: Compiling summary protocol buffers failed. You will not be able to use smdebug. "
        "Please make sure that you have installed protobuf3 compiler and runtime correctly."
    )
    sys.exit(1)


def detect_smdebug_version():
    if "--release" in sys.argv:
        sys.argv.remove("--release")
        return smdebug.__version__.strip()

    return smdebug.__version__.strip() + "b" + str(date.today()).replace("-", "")


version = detect_smdebug_version()
scan_git_secrets()
build_package(version=version)
