from distutils.core import setup
setup(
  name = 'HeartsGym',         
  packages = ['HeartsGym'],   
  version = '0.2',     
  license='MIT',        
  description = 'AI Gym for the card game Hearts',   
  author = 'Jacob Haight',                  
  author_email = 'jacobrhaight@gmail.com',
  url = 'https://github.com/some45bucks/HeartsGym',
  download_url = 'https://github.com/some45bucks/HeartsGym/archive/refs/tags/V_01.tar.gz',
  keywords = ['Hearts', 'AI', 'Gym', 'CardGame'],
  install_requires=[ 
          'gym',
          'numpy'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.10',
  ],
)