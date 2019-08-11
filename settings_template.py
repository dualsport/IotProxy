# device_sites
# each entry contains device name and site name to direct to
# 'X-Device-Name' header received should match and entry here
device_sites = {'MyDevice': 'MyStaging',
                'MyOtherDevice': 'MyProduction'
               }


# Redirect site configuration
# Each entry contains:
#  a) key = redirect site being requested
#  b) dict containing url and associated token
redirect_sites = {'MyStaging':
                    {'url': 'https://staging.mysite.com',
                     'token': 'Token wDSPdC9fJxQI5iBerbgv2cwJ9tKRGjb8PTJt70I8'
                    },
                  'MyProduction':
                    {'url': 'https://prod.mysite.com',
                     'token': 'Token DZ5CHd96Zb45HE1mPMLslfQkpgMdiKikjXS7yv7U'
                    },
                 }
