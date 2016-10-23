from .birthdays import birthdays
from .commands import Commands
from .faq import faq
from .regulars import regulars


dispatch_naming = {
    'birthdays': '$birthdays',
    'commands': '$commands',
    'faq': '$faq',
    'filters': '$filters',
    'regulars': '$regulars',
}

dispatch_map = {
    dispatch_naming['birthdays']: birthdays,
    dispatch_naming['commands']: Commands,
    dispatch_naming['faq']: faq,
    dispatch_naming['regulars']: regulars,
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
