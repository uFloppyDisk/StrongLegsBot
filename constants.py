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


class ConfigDefaults:
    def __init__(self, sqlconn):
        self.sqlConnectionChannel, self.sqlCursorChannel = sqlconn

        self.columns = {
            "grouping": 0,
            "variable": 1,
            "value": 2,
            "args": 3,
            "userlevel": 4,
        }

        self.defaults = {
            "birthdays": self.birthdays,
            "commands": self.commands,
            "config": self.config,
            "faq": self.faq,
            "filters": self.filters,
            "regulars": self.regulars,
        }

        self.sqlInsertString = "INSERT INTO config (grouping, variable, value, args, userlevel) VALUES (?, ?, ?, ?, ?)"
        self.sqlUpdateString = "UPDATE config SET value=?, args=?, userlevel=? WHERE grouping=? AND variable=?"
        self.sqlExecute = self.sqlCursorChannel.execute

    def all_(self, defaultto=0):
        self.birthdays(defaultto)
        self.commands(defaultto)
        self.config(defaultto)
        self.faq(defaultto)
        self.filters(defaultto)
        self.regulars(defaultto)
        return

    def updatesql(self, grouping, variables, defaultto, variable):
        self.sqlExecute("SELECT variable FROM config WHERE grouping = ?", (grouping,))
        sqlCursorOffload = self.sqlCursorChannel.fetchall()

        if defaultto == 0:
            return

        if defaultto == 1:
            for varset in variables:
                if True in [entry[0] == varset[1] for entry in sqlCursorOffload]:
                    self.sqlCursorChannel.execute(self.sqlUpdateString, (varset[2], varset[3], varset[4],
                                                                         varset[0], varset[1]))
                else:
                    self.sqlCursorChannel.execute(self.sqlInsertString, varset)

            self.sqlConnectionChannel.commit()
            return

        if defaultto == 2:
            for varset in variables:
                if True in [entry[0] == varset[1] for entry in sqlCursorOffload]:
                    pass
                else:
                    self.sqlCursorChannel.execute(self.sqlInsertString, varset)

            self.sqlConnectionChannel.commit()
            return

        if defaultto == 3:
            for varset in variables:
                if True in [entry[0] == variable for entry in sqlCursorOffload] and varset[1] == variable:
                    self.sqlCursorChannel.execute(self.sqlUpdateString, (varset[2], varset[3], varset[4],
                                                                         varset[0], varset[1]))
                else:
                    pass

            self.sqlConnectionChannel.commit()
            return

    def birthdays(self, defaultto, variable=None):
        variables = [
            ("birthdays", "enabled", True, "boolean", 400),
            ("birthdays", "keyword", "$birthdays", "string", 400),
            ("birthdays", "min_userlevel", 150, "integer,700-0", 400),
        ]

        self.updatesql("birthdays", variables, defaultto, variable)

        return

    def commands(self, defaultto, variable=None):
        variables = [
            ("commands", "enabled", True, "boolean", 400),
            ("commands", "keyword", "$commands", "string", 400),
            ("commands", "min_userlevel", 0, "integer,700-0", 400),
            ("commands", "min_userlevel_edit", 250, "integer,700-0", 400),
        ]

        self.updatesql("commands", variables, defaultto, variable)

        return

    def config(self, defaultto, variable=None):
        variables = [
            ("config", "min_userlevel_edit", 250, "integer,700-0", 400),
        ]

        self.updatesql("config", variables, defaultto, variable)

        return

    def faq(self, defaultto, variable=None):
        variables = [
            ("faq", "enabled", True, "boolean", 400),
            ("faq", "keyword", "$faq", "string", 400),
            ("faq", "min_userlevel", 0, "integer,700-0", 400),
            ("faq", "min_userlevel_edit", 400, "integer,700-0", 400),
        ]

        self.updatesql("faq", variables, defaultto, variable)

        return

    def filters(self, defaultto, variable=None):
        variables = [
            ("filters", "enabled", True, "boolean", 400),
            ("filters", "keyword", "$filters", "string", 400),
            ("filters", "min_userlevel", 0, "integer,700-0", 400),
            ("filters", "min_userlevel_edit", 250, "integer,700-0", 400),

            ("filters", "banphrases_enabled", True, "boolean", 400),
            ("filters", "banphrases_max_userlevel", 150, "integer,249-0", 400),
            ("filters", "banphrases_first_timeout", 10, "integer,86400-1", 400),
            ("filters", "banphrases_second_timeout", 600, "integer,86400-1", 400),
            ("filters", "banphrases_third_timeout", 600, "integer,86400-1", 400),
            ("filters", "banphrases_ban_after_third", False, "boolean", 400),
            ("filters", "banphrases_message", None, "string", 400),

            ("filters", "emotespam_enabled", True, "boolean", 400),
            ("filters", "emotespam_max_userlevel", 150, "integer,249-0", 400),
            ("filters", "emotespam_first_timeout", 10, "integer,86400-1", 400),
            ("filters", "emotespam_second_timeout", 600, "integer,86400-1", 400),
            ("filters", "emotespam_third_timeout", 600, "integer,86400-1", 400),
            ("filters", "emotespam_ban_after_third", False, "boolean", 400),
            ("filters", "emotespam_message", None, "string", 400),

            ("filters", "link_enabled", True, "boolean", 400),
            ("filters", "link_max_userlevel", 150, "integer,249-0", 400),
            ("filters", "link_first_timeout", 10, "integer,86400-1", 400),
            ("filters", "link_second_timeout", 600, "integer,86400-1", 400),
            ("filters", "link_third_timeout", 600, "integer,86400-1", 400),
            ("filters", "link_ban_after_third", False, "boolean", 400),
            ("filters", "link_message", None, "string", 400),

            ("filters", "spam_enabled", True, "boolean", 400),
            ("filters", "spam_max_userlevel", 150, "integer,249-0", 400),
            ("filters", "spam_first_timeout", 10, "integer,86400-1", 400),
            ("filters", "spam_second_timeout", 600, "integer,86400-1", 400),
            ("filters", "spam_third_timeout", 600, "integer,86400-1", 400),
            ("filters", "spam_ban_after_third", False, "boolean", 400),
            ("filters", "spam_message", None, "string", 400),
        ]

        self.updatesql("filters", variables, defaultto, variable)

        return

    def regulars(self, defaultto, variable=None):
        variables = [
            ("regulars", "enabled", True, "boolean", 400),
            ("regulars", "keyword", "$regulars", "string", 400),
            ("regulars", "min_userlevel", 0, "integer,700-0", 400),
            ("regulars", "min_userlevel_edit", 250, "integer,700-0", 400),
        ]

        self.updatesql("regulars", variables, defaultto, variable)

        return


def boolean(value):
    truevalues = ["True", "true", "1"]
    return value in truevalues
