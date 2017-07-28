# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from collections import OrderedDict
from .manifest import _manifest_create
from ._util import TraversalFunction


image_show_header_to_fn_dict = OrderedDict([('Id', TraversalFunction(('Id',))),
                                            ('Description', TraversalFunction(('Description',))),
                                            ('Image_Type', TraversalFunction(('ImageType',))),
                                            ('Manifest_Id', TraversalFunction(('ManifestId',)))])
