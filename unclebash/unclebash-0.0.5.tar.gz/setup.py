from distutils.core import setup

if __name__ == "__main__":
    setup(
        name="unclebash",
        version="0.0.5",
        author="Bo Zhang",
        author_email="bozhang@nao.cas.cn",
        description=("A quick setup for ~/.bashrc file"),  # short description
        license="MIT",
        # install_requires=["numpy>=1.7","scipy","matplotlib","nose"],
        url="http://github.com/hypergravity/unclebash",
        classifiers=[
            "Development Status :: 6 - Mature",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.5",
            "Topic :: Scientific/Engineering :: Astronomy",
            "Topic :: Scientific/Engineering :: Physics"],
        package_dir={"unclebash": "unclebash"},
        packages=["unclebash"],
        package_data={"unclebash": ["data/*",
                                    "backup/*"]},
        include_package_data=True,
        requires=["numpy"]
    )
