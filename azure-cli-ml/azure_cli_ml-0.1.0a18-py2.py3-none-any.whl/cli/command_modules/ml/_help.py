# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.cli.core.help_files import helps

# pylint: disable=line-too-long

helps['ml'] = """
            type: group
            short-summary: Module for operationalizing machine learning models
            """

helps["ml env"] = """
                type: group
                short-summary: Manage compute environments."""

helps["ml service"] = """
                    type: group
                    short-summary: Manage operationalized services."""

helps["ml hostacct"] = """
                     type: group
                     short-summary: Manage host accounts"""

helps["ml image"] = """
                  type: group
                  short-summary: Manage operationalization images"""

helps["ml manifest"] = """
                     type: group
                     short-summary: Manage operationalization manifests"""

helps["ml model"] = """
                  type: group
                  short-summary: Manage operationalization models"""

helps["ml package"] = """
                    type: group
                    short-summary: Manage operationalization packages"""
