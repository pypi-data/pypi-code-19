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
from exactmatch import ExactMatch


class PriorityMatch(BaseMatch):
    """ Priority Match class """

    def __init__(self):
        self.exact_match = ExactMatch()

    def match(self, match_details, mapping_list, start_col=0):
        """ matching based on prioritizing entries in the right column of the
            mapping list

        Parameters:
            match_details (list): holds the information based on which the mapping
                                  should be conducted, a row entry is structured as
                                  [Detail ,Value]
            mapping_list (list): hold the mapping information, the first row describes
                                 the properties on which mapping should be conducted and
                                 a column named target
            start_col (int): starting column for the matching algorithms of the mapping_list

        Return:
            string: target value which has been matched


        The priority match uses a given mapping_list, e.g

        +-------------------------+------------+----------+
        | Property1  | Property2  | Property3  | Target   |
        +============+============+============+==========+
        | Value1_1   |            | Value3_1   | Target1  |
        +------------+------------+------------+----------+
        | Value1_1   |            | Value3_2   | Target2  |
        +------------+------------+------------+----------+
        |            | Value2_1   | Value3_3   | Target3  |
        +------------+------------+------------+----------+
        |            | Value2_1   | Value3_4   | Target4  |
        +------------+------------+------------+----------+

        Given the above tables, the matching searches column by column,
        starting on the left hand side (highest priority columns), for
        the respective mapping list.

        For a given list of match_details, e.g.

        +------------+-----------+
        | Property1  | Value1_2  |
        +------------+-----------+
        | Property2  | Value2_1  |
        +------------+-----------+
        | Property3  | Value3_3  |
        +------------+-----------+

        the match returns in a first step a 2x4 matrix

        +------------+------------+------------+----------+
        |            | Value2_1   | Value3_3   | Target3  |
        +------------+------------+------------+----------+
        |            | Value2_1   | Value3_4   | Target4  |
        +------------+------------+------------+----------+

        As a second step, the empty columns are removed and the exact match
        algorithm is applied to the remaining properties to find the target,
        which for the given example yields Target3.

        If for column no matching is found it continues recursively at the
        next column and searches for the respective property, i.e Property3.
        """

        match = False
        rows = []

        mapping_list_cols = list(mapping_list[0])
        target_col = mapping_list_cols.index('Target')

        # todo add some description on what is going on here
        for j, attr in enumerate(mapping_list_cols[start_col:-1]):
            for i in range(1, len(mapping_list)):
                detail_value = None
                for c in range(0, len(match_details)):
                    if match_details[c][0] == attr:
                        detail_value = match_details[c][1]
                        break

                if detail_value != '':
                    if self._has_relation_operator(mapping_list[i][j]):
                        if self._apply_relation_match(mapping_list[i][j], detail_value):
                            rows.append(i)
                            match = True
                        else:
                            match = False
                    elif type(detail_value)(mapping_list[i][j]) == detail_value:
                        rows.append(i)
                        match = True
                    else:
                        match = False
                else:
                    match = False

        new_mapping_list = list()
        new_mapping_list.append(mapping_list_cols[start_col:])
        new_mapping_list.extend([mapping_list[i][start_col:] for i in rows])

        # todo add some description on what is going on here
        if len(new_mapping_list[:-1]) == 1:
            match_obj = new_mapping_list[len(new_mapping_list) - 1][target_col]
        else:
            empty_cols = [[i for i, str in enumerate(j[:]) if str == ''] for j in new_mapping_list[1:]]
            unique_empty_cols = set([item for sublist in empty_cols for item in sublist])

            n = 0
            # todo add some description on what is going on here
            for i, j in enumerate(unique_empty_cols):
                if i == 0:
                    n = 0
                    [[new_mapping_list[r].pop(j)] for r in range(0, len(new_mapping_list))]
                else:
                    n += 1
                    [[new_mapping_list[r].pop(j - n)] for r in range(0, len(new_mapping_list))]

            match_obj = self.exact_match.match(match_details, new_mapping_list)

            if not match_obj:
                new_mapping_list_cols = [map_col for map_col in new_mapping_list[0]]
                start_col = [i for i, name in enumerate(mapping_list_cols) if name == new_mapping_list_cols[0]][0] + 1

                if start_col < len(mapping_list_cols[:-1]):
                    match_obj = self.match(match_details, mapping_list, start_col)

        return match_obj
