from distutils.core import setup

setup(
    name='pixel',
    version='0.1.0',
    packages=['pixel'],
    url='https://github.com/PixelTool/pixelpy',
    license='MIT',
    description='Parse rules generated by pixel_annotation_tool',
    install_requires=[
        'arrow',
        'dateparser'
    ]
)