from .commands import Commands

from .regulars import regulars

from .faq import faq

dispatch_naming = {'commands': '$commands', 'regulars': '$regulars',
                   'filters': '$filters', 'faq': '$faq'}

dispatch_map = {dispatch_naming['commands']: Commands,
                dispatch_naming['regulars']: regulars,
                dispatch_naming['faq']: faq}

help_defaults = {
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
    }
}
