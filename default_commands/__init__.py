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

from . import birthdays
from . import commands
from . import config
from . import constants
from . import faq
from . import regulars


dispatch_naming = {
    'birthdays': '$birthdays',
    'commands': '$commands',
    'config': '$config',
    'faq': '$faq',
    'filters': '$filters',
    'regulars': '$regulars',
}

dispatch_map = {
    dispatch_naming['birthdays']: birthdays.birthdays,
    dispatch_naming['commands']: commands.commands,
    dispatch_naming['config']: config.config,
    dispatch_naming['faq']: faq.faq,
    dispatch_naming['regulars']: regulars.regulars,
}

help_defaults = {
    dispatch_naming['birthdays']: {
        '': '{command} DD/MM/YYYY (Specifying year is optional)'
    },
    dispatch_naming['commands']: {
        '': '{command} help/add/edit/delete',
        'help': '{command} help <command> <args...>',
        'page': '{command} page <page#>',
        'add': '{command} add [optional: \'-ul=###\' or \'-sm=whisper/privmsg\'] '
               '<keyword> <output> (userlevel defaults to 0)',
        'edit': '{command} edit <keyword> \'-ul=<userlevel>\' and/or \'-sm=whisper/privmsg\' and/or '
                '\'-output="<output>"\'',
        'delete': '{command} delete <keyword>'
    },
    dispatch_naming['regulars']: {
        '': '{command} add/delete',
        'add': '{command} add <username>',
        'delete': '{command} add <username>'
    },
}
