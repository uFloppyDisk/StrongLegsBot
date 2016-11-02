"""
Copyright 2016 Pawel Bartusiak

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import configparser
import logging

cfg = configparser.ConfigParser(allow_no_value=True)


class configUnpacker:
    def __init__(self):
        self.dictConfigValues = {}

    def unpackcfg(self):
        cfg.read('cfg/config.ini')
        cfgsections = cfg.sections()
        try:
            for section in cfgsections:
                options = cfg.options(section)
                if section != '':
                    for option in options:
                        value = cfg.get(section, option)
                        self.dictConfigValues['%s_%s' % (section, option)] = value

        except Exception as configerror:
            logging.error('CONFIG ERROR: %s' % str(configerror))

        return self.dictConfigValues


if __name__ == "__main__":
    pass