import ConfigParser
import logging

cfg = ConfigParser.ConfigParser(allow_no_value=True)


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
    print("       UnpackConfig.py        ")
    print("     By: Pawel Bartusiak      ")
    print("    Don't pirate this guy     ")
    raw_input('Yes guy? (Y/N): ')
