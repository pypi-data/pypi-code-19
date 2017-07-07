# -*- coding: utf-8 -*-

#  goma
#  ----
#  Generic object mapping algorithm.
#
#  Author:  pbrisk <pbrisk_at_github@icloud.com>
#  Copyright: 2016, 2017 Deutsche Postbank AG
#  Website: https://github.com/pbrisk/goma
#  License: APACHE Version 2 License (see LICENSE file)


from basematch import BaseMatch


class ExactMatch(BaseMatch):
    def match(self, match_details, mapping_list):
        """ matching based on exact entries of all columns of the
            mapping list

        Parameters:
            match_details (list): holds the information based on which the mapping
                                  should be conducted, a row entry is structured as
                                  ['Detail', 'Value']
            mapping_list (list): holds the mapping information, the first row describes
                                 the properties on which mapping should be conducted and
                                 a column named target
            start_col (int): starting column for the matching algorithms of the mapping_list

        The exact match uses a given mapping_list, e.g

        +-------------------------+------------+----------+
        | Property1  | Property2  | Property3  | Target   |
        +============+============+============+==========+
        | Value1_1   |  Value2_1  | Value3_1   | Target1  |
        +------------+------------+------------+----------+
        | Value1_2   |  Value2_2  | Value3_2   | Target2  |
        +------------+------------+------------+----------+

        Given the above tables, the matching searches row by row,
        if all criteria in the matching list of a given list of
        details (match_details) are met.

        For a given list of match_details, e.g.

        +------------+-----------+
        | Property1  | Value1_2  |
        +------------+-----------+
        | Property2  | Value2_2  |
        +------------+-----------+
        | Property3  | Value3_2  |
        +------------+-----------+

        the match returns in a Target 2. If one matching criteria is not
        met, the match returns None.
        """

        match_obj = None

        mapping_list_cols = [map_col for map_col in mapping_list[0]]
        target_col = [i for i, name in enumerate(mapping_list[0]) if name == 'Target'][0]

        for i in range(1, len(mapping_list)):
            matches = 0
            for j, attr in enumerate(mapping_list_cols[:-1]):
                detail_value = None
                for c in range(0, len(match_details)):
                    if match_details[c][0] == attr:
                        detail_value = match_details[c][1]
                        break

                if detail_value != '':
                    if self._has_relation_operator(mapping_list[i][j]):
                        if self._apply_relation_match(mapping_list[i][j], detail_value):
                            matches += 1
                        else:
                            break
                    elif not detail_value:
                        break
                    elif type(detail_value)(mapping_list[i][j]) == detail_value:
                        matches += 1
                    else:
                        break
                else:
                    break

            if matches == len(mapping_list_cols[:-1]):
                match_obj = mapping_list[i][target_col]
                break

        return match_obj
