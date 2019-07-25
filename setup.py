import setuptools
from splitter import VERSION_STR

setuptools.setup(
            name='video-file-splitter',
            version=VERSION_STR,
            description='split a video file into fragments',
            url='https://github.com/gwappa/video-file-splitter',
            author='Keisuke Sehara',
            author_email='keisuke.sehara@gmail.com',
            license='MIT',
            install_requires=['scikit-video>=1.1'],
            classifiers=[
                        'Development Status :: 3 - Alpha',
                        'License :: OSI Approved :: MIT License',
                        'Programming Language :: Python :: 3',
                        ],
            packages=['splitter',],
            entry_points={
                            'console_scripts': [
                                'splitvideo =splitter.__main__:main'
                            ]
                        }
            )

